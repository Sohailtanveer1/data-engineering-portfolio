#!/usr/bin/env python3
"""
determine_version.py

Determines the next semantic version for a job/library package based on
Conventional Commits since the last release tag — implements the
versioning approach in
ci-cd/06-environment-promotion-and-release.md and
07-spark-migration/04-packaging-and-dependency-management.md.

Rules:
  - Any commit with "BREAKING CHANGE:" in its body, or a "!" after the
    type (e.g. "feat!:"), bumps MAJOR.
  - Any "feat:" commit (no breaking marker) bumps MINOR.
  - Any "fix:" commit bumps PATCH.
  - If none of the above are found, PATCH is bumped by default.

Usage:
    python determine_version.py [--repo-path .]

Prints the new version string (e.g. "2.4.0") to stdout.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from typing import Tuple

BREAKING_PATTERN = re.compile(r"^(feat|fix|refactor)(\([^)]*\))?!:", re.MULTILINE)
BREAKING_BODY_PATTERN = re.compile(r"BREAKING CHANGE:", re.MULTILINE)
FEAT_PATTERN = re.compile(r"^feat(\([^)]*\))?:", re.MULTILINE)
FIX_PATTERN = re.compile(r"^fix(\([^)]*\))?:", re.MULTILINE)


def get_last_tag(repo_path: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", repo_path, "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_commit_messages_since(repo_path: str, since_tag: str | None) -> str:
    range_spec = f"{since_tag}..HEAD" if since_tag else "HEAD"
    result = subprocess.run(
        ["git", "-C", repo_path, "log", range_spec, "--pretty=format:%B%n---COMMIT-BOUNDARY---"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def parse_current_version(tag: str | None) -> Tuple[int, int, int]:
    if not tag:
        return (0, 0, 0)
    cleaned = tag.lstrip("v")
    parts = cleaned.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return (0, 0, 0)


def determine_bump(commit_log: str) -> str:
    if BREAKING_PATTERN.search(commit_log) or BREAKING_BODY_PATTERN.search(commit_log):
        return "major"
    if FEAT_PATTERN.search(commit_log):
        return "minor"
    if FIX_PATTERN.search(commit_log):
        return "patch"
    return "patch"  # default to patch if no conventional prefix found


def bump_version(current: Tuple[int, int, int], bump: str) -> Tuple[int, int, int]:
    major, minor, patch = current
    if bump == "major":
        return (major + 1, 0, 0)
    if bump == "minor":
        return (major, minor + 1, 0)
    return (major, minor, patch + 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", default=".", help="Path to the git repository")
    args = parser.parse_args()

    last_tag = get_last_tag(args.repo_path)
    commit_log = get_commit_messages_since(args.repo_path, last_tag)
    bump = determine_bump(commit_log)
    current_version = parse_current_version(last_tag)
    new_version = bump_version(current_version, bump)

    print(f"{new_version[0]}.{new_version[1]}.{new_version[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
