#!/usr/bin/env python3
"""
check_dag_best_practices.py

Static analysis enforcing the DAG authoring standard from
09-composer-migration/04-dag-best-practices.md — run as a CI/CD gate
per ci-cd/workflows/dag-sync.yml.

Checks (per DAG file):
  - No apparent top-level I/O or expensive computation (heuristic regex
    scan for requests/urlopen/database calls outside function bodies)
  - default_args declares 'owner'
  - A 'sla' is declared somewhere in the file
  - DAG ID follows the <data_domain>_<job_name> naming convention
  - Any DataprocDeleteClusterOperator/cluster-teardown task uses
    trigger_rule="all_done"

Usage:
    python check_dag_best_practices.py dags/

Exit codes:
    0 - all DAG files pass
    1 - one or more violations found
    2 - invocation error (e.g., path not found)
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import List


TOP_LEVEL_IO_PATTERNS = [
    re.compile(r"^\s*requests\.(get|post|put|delete)\("),
    re.compile(r"^\s*urlopen\("),
    re.compile(r"^\s*\w+\.connect\("),  # heuristic for a DB connection call
]

DAG_ID_PATTERN = re.compile(r'dag_id\s*=\s*["\']([a-z0-9_]+)_([a-z0-9_]+)["\']')


class Violation:
    def __init__(self, file: str, rule: str, detail: str):
        self.file = file
        self.rule = rule
        self.detail = detail

    def __str__(self) -> str:
        return f"{self.file}: [{self.rule}] {self.detail}"


def check_top_level_io(file_path: Path, source: str, tree: ast.AST) -> List[Violation]:
    """Flags I/O-looking calls at module top level (outside any function/class)."""
    violations = []
    function_and_class_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    function_and_class_lines.add(child.lineno)

    for lineno, line in enumerate(source.splitlines(), start=1):
        if lineno in function_and_class_lines:
            continue
        for pattern in TOP_LEVEL_IO_PATTERNS:
            if pattern.match(line):
                violations.append(
                    Violation(
                        str(file_path),
                        "no-top-level-io",
                        f"Line {lineno}: possible I/O call at module top level: {line.strip()}",
                    )
                )
    return violations


def check_owner_declared(file_path: Path, source: str) -> List[Violation]:
    if "owner" not in source:
        return [Violation(str(file_path), "owner-required", "No 'owner' field found in default_args")]
    return []


def check_sla_declared(file_path: Path, source: str) -> List[Violation]:
    if "sla" not in source:
        return [Violation(str(file_path), "sla-required", "No 'sla' field found")]
    return []


def check_dag_id_naming(file_path: Path, source: str) -> List[Violation]:
    match = DAG_ID_PATTERN.search(source)
    if not match:
        return [
            Violation(
                str(file_path),
                "dag-id-naming",
                "dag_id does not match <data_domain>_<job_name> convention "
                "per 13-infrastructure/03-naming-and-tagging-standards.md",
            )
        ]
    return []


def check_cluster_teardown_trigger_rule(file_path: Path, source: str) -> List[Violation]:
    if "DataprocDeleteClusterOperator" in source and 'trigger_rule="all_done"' not in source:
        return [
            Violation(
                str(file_path),
                "cluster-teardown-trigger-rule",
                "DataprocDeleteClusterOperator found without trigger_rule=\"all_done\" — "
                "see 07-spark-migration/03-dataproc-submission-patterns.md",
            )
        ]
    return []


def check_file(file_path: Path) -> List[Violation]:
    source = file_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        return [Violation(str(file_path), "syntax-error", str(exc))]

    violations: List[Violation] = []
    violations += check_top_level_io(file_path, source, tree)
    violations += check_owner_declared(file_path, source)
    violations += check_sla_declared(file_path, source)
    violations += check_dag_id_naming(file_path, source)
    violations += check_cluster_teardown_trigger_rule(file_path, source)
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dags_dir", help="Directory containing DAG files to check")
    args = parser.parse_args()

    dags_dir = Path(args.dags_dir)
    if not dags_dir.is_dir():
        print(f"Error: {dags_dir} is not a directory", file=sys.stderr)
        return 2

    dag_files = sorted(dags_dir.rglob("*_dag.py")) + sorted(dags_dir.rglob("*_factory.py"))
    all_violations: List[Violation] = []
    for file_path in dag_files:
        all_violations += check_file(file_path)

    if all_violations:
        print(f"Found {len(all_violations)} DAG best-practice violation(s):\n")
        for v in all_violations:
            print(f"  - {v}")
        return 1

    print(f"Checked {len(dag_files)} DAG file(s) — all passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
