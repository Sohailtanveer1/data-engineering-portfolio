#!/usr/bin/env python3
"""
validate_storage_migration.py

Compares file count, total size, and per-file checksums between an HDFS
source path and a GCS target path — implements the validation levels
described in 05-storage-migration/05-checksum-and-validation.md.

Usage:
    python validate_storage_migration.py \\
        --source-path hdfs:///data/pricing/ \\
        --target-path gs://acme-prod-pricing-raw/ \\
        --domain pricing \\
        --sample-rate 1.0

Exit codes:
    0 - validation passed
    1 - validation failed (mismatch found)
    2 - invocation error
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import subprocess
import sys
from typing import Dict, List


@dataclasses.dataclass
class FileEntry:
    path: str
    size_bytes: int
    checksum: str = ""


@dataclasses.dataclass
class ValidationResult:
    domain: str
    source_file_count: int
    target_file_count: int
    source_total_bytes: int
    target_total_bytes: int
    mismatched_files: List[str]
    missing_in_target: List[str]
    missing_in_source: List[str]

    @property
    def passed(self) -> bool:
        return (
            self.source_file_count == self.target_file_count
            and self.source_total_bytes == self.target_total_bytes
            and not self.mismatched_files
            and not self.missing_in_target
            and not self.missing_in_source
        )

    def to_report(self) -> dict:
        return {
            "domain": self.domain,
            "status": "PASS" if self.passed else "FAIL",
            "source_file_count": self.source_file_count,
            "target_file_count": self.target_file_count,
            "source_total_bytes": self.source_total_bytes,
            "target_total_bytes": self.target_total_bytes,
            "mismatched_files": self.mismatched_files,
            "missing_in_target": self.missing_in_target,
            "missing_in_source": self.missing_in_source,
        }


def list_hdfs_files(path: str) -> Dict[str, FileEntry]:
    """Lists files under an HDFS path with size, via `hdfs dfs -ls -R`."""
    result = subprocess.run(
        ["hdfs", "dfs", "-ls", "-R", path], capture_output=True, text=True, check=True
    )
    entries: Dict[str, FileEntry] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 8 or parts[0].startswith("d"):
            continue  # skip directories and malformed lines
        size_bytes = int(parts[4])
        file_path = parts[-1]
        relative = file_path.replace(path.rstrip("/"), "").lstrip("/")
        entries[relative] = FileEntry(path=relative, size_bytes=size_bytes)
    return entries


def list_gcs_files(path: str) -> Dict[str, FileEntry]:
    """Lists objects under a GCS path with size, via `gsutil ls -l`."""
    result = subprocess.run(
        ["gsutil", "ls", "-l", "-r", path.rstrip("/") + "/**"],
        capture_output=True,
        text=True,
        check=True,
    )
    entries: Dict[str, FileEntry] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 3 or not parts[0].isdigit():
            continue  # skip summary/total lines
        size_bytes = int(parts[0])
        object_path = parts[-1]
        relative = object_path.replace(path.rstrip("/"), "").lstrip("/")
        entries[relative] = FileEntry(path=relative, size_bytes=size_bytes)
    return entries


def compute_hdfs_checksum(full_path: str) -> str:
    result = subprocess.run(
        ["hdfs", "dfs", "-checksum", full_path], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def compute_gcs_checksum(full_path: str) -> str:
    result = subprocess.run(
        ["gsutil", "hash", "-c", full_path], capture_output=True, text=True, check=True
    )
    for line in result.stdout.splitlines():
        if "crc32c" in line.lower():
            return line.split(":")[-1].strip()
    return ""


def validate(
    source_path: str, target_path: str, domain: str, sample_rate: float
) -> ValidationResult:
    source_files = list_hdfs_files(source_path)
    target_files = list_gcs_files(target_path)

    source_keys = set(source_files.keys())
    target_keys = set(target_files.keys())

    missing_in_target = sorted(source_keys - target_keys)
    missing_in_source = sorted(target_keys - source_keys)

    common_keys = sorted(source_keys & target_keys)
    sample_size = max(1, int(len(common_keys) * sample_rate)) if common_keys else 0
    sampled_keys = common_keys[:sample_size]

    mismatched_files: List[str] = []
    for key in sampled_keys:
        src = source_files[key]
        tgt = target_files[key]
        if src.size_bytes != tgt.size_bytes:
            mismatched_files.append(key)
            continue
        # Full checksum comparison only for the sampled subset — see
        # 05-storage-migration/05-checksum-and-validation.md tolerance
        # note on sampling for large, lower-tier domains.
        src_checksum = compute_hdfs_checksum(f"{source_path.rstrip('/')}/{key}")
        tgt_checksum = compute_gcs_checksum(f"{target_path.rstrip('/')}/{key}")
        if src_checksum and tgt_checksum and src_checksum != tgt_checksum:
            mismatched_files.append(key)

    return ValidationResult(
        domain=domain,
        source_file_count=len(source_files),
        target_file_count=len(target_files),
        source_total_bytes=sum(f.size_bytes for f in source_files.values()),
        target_total_bytes=sum(f.size_bytes for f in target_files.values()),
        mismatched_files=mismatched_files,
        missing_in_target=missing_in_target,
        missing_in_source=missing_in_source,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-path", required=True, help="HDFS source path")
    parser.add_argument("--target-path", required=True, help="GCS target path")
    parser.add_argument("--domain", required=True, help="Data domain name for the report")
    parser.add_argument(
        "--sample-rate",
        type=float,
        default=1.0,
        help="Fraction of common files to checksum-compare (1.0 = full coverage, required for Tier 1)",
    )
    args = parser.parse_args()

    try:
        result = validate(args.source_path, args.target_path, args.domain, args.sample_rate)
    except subprocess.CalledProcessError as exc:
        print(f"Error running validation command: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result.to_report(), indent=2))
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
