#!/usr/bin/env python3
"""
reconcile_table.py

Config-driven table-level reconciliation engine — implements the checks
described in 06-data-migration/07-data-reconciliation-framework.md and
16-data-validation/01-validation-framework-architecture.md.

Reads a YAML config describing which checks to run for a table, executes
them against source and target, and emits a structured JSON report per
16-data-validation/06-reconciliation-reporting.md.

Usage:
    python reconcile_table.py --config validation-configs/pricing_daily_price_snapshot.yaml

Exit codes:
    0 - all checks passed
    1 - one or more checks failed
    2 - invocation/config error
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import sys
from typing import Any, Dict, List, Optional

import yaml


@dataclasses.dataclass
class CheckResult:
    check_type: str
    status: str  # "PASS" or "FAIL"
    details: Dict[str, Any] = dataclasses.field(default_factory=dict)


class QueryRunner:
    """
    Abstraction over the actual query execution backend (BigQuery client,
    Hive/Spark SQL session). Kept as an injectable interface so this
    module's check logic can be unit-tested with a fake runner — see
    07-spark-migration/08-oop-design-patterns.md dependency-injection
    principle applied here.
    """

    def scalar(self, sql: str) -> Any:
        raise NotImplementedError("Provide a real backend implementation (BigQuery/Spark SQL client).")


class ReconciliationEngine:
    def __init__(self, source_runner: QueryRunner, target_runner: QueryRunner):
        self._source = source_runner
        self._target = target_runner

    def run(self, config: Dict[str, Any]) -> List[CheckResult]:
        results: List[CheckResult] = []
        table = config["table"]
        for check in config.get("checks", []):
            check_type = check["type"]
            handler = getattr(self, f"_check_{check_type}", None)
            if handler is None:
                results.append(
                    CheckResult(check_type, "FAIL", {"error": f"Unknown check type: {check_type}"})
                )
                continue
            results.append(handler(table, check))
        return results

    def _check_row_count(self, table: str, check: Dict[str, Any]) -> CheckResult:
        source_count = self._source.scalar(f"SELECT COUNT(*) FROM {table}")
        target_count = self._target.scalar(f"SELECT COUNT(*) FROM {table}")
        tolerance = check.get("tolerance", 0)
        passed = abs(source_count - target_count) <= tolerance
        return CheckResult(
            "row_count",
            "PASS" if passed else "FAIL",
            {"source_value": source_count, "target_value": target_count, "tolerance": tolerance},
        )

    def _check_aggregate(self, table: str, check: Dict[str, Any]) -> CheckResult:
        column = check["column"]
        function = check["function"].upper()
        sql = f"SELECT {function}({column}) FROM {table}"
        source_value = self._source.scalar(sql)
        target_value = self._target.scalar(sql)
        tolerance = check.get("tolerance", 0)
        passed = abs((source_value or 0) - (target_value or 0)) <= tolerance
        return CheckResult(
            f"aggregate_{function.lower()}_{column}",
            "PASS" if passed else "FAIL",
            {"source_value": source_value, "target_value": target_value, "tolerance": tolerance},
        )

    def _check_null_check(self, table: str, check: Dict[str, Any]) -> CheckResult:
        details = {}
        all_passed = True
        for column in check["columns"]:
            sql = f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL"
            target_nulls = self._target.scalar(sql)
            expected = check.get("expected_null_count", 0)
            passed = target_nulls == expected
            all_passed = all_passed and passed
            details[column] = {"null_count": target_nulls, "expected": expected}
        return CheckResult("null_check", "PASS" if all_passed else "FAIL", details)

    def _check_duplicate_check(self, table: str, check: Dict[str, Any]) -> CheckResult:
        key_cols = ", ".join(check["key_columns"])
        sql = (
            f"SELECT COUNT(*) FROM ("
            f"SELECT {key_cols} FROM {table} GROUP BY {key_cols} HAVING COUNT(*) > 1"
            f") dup"
        )
        duplicate_groups = self._target.scalar(sql)
        passed = duplicate_groups == 0
        return CheckResult(
            "duplicate_check", "PASS" if passed else "FAIL", {"duplicate_key_groups": duplicate_groups}
        )

    def _check_business_rule(self, table: str, check: Dict[str, Any]) -> CheckResult:
        # Business rule SQL is defined per-rule in the config's `sql`
        # field — see 16-data-validation/04-business-rule-validation.md
        # for the catalog this maps to.
        sql = check["sql"]
        violation_count = self._target.scalar(sql)
        passed = violation_count == 0
        return CheckResult(
            f"business_rule_{check.get('rule', 'unnamed')}",
            "PASS" if passed else "FAIL",
            {"violation_count": violation_count},
        )


def build_report(config: Dict[str, Any], results: List[CheckResult]) -> Dict[str, Any]:
    overall_status = "PASS" if all(r.status == "PASS" for r in results) else "FAIL"
    return {
        "table": config["table"],
        "run_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "trigger": config.get("schedule", "manual"),
        "overall_status": overall_status,
        "checks": [dataclasses.asdict(r) for r in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to the table's validation YAML config")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Real usage: instantiate concrete QueryRunner implementations backed
    # by the BigQuery client / Spark SQL session for source and target.
    # Left abstract here — see the class docstring above.
    raise SystemExit(
        "This script requires concrete QueryRunner implementations to be wired in "
        "for the actual source/target platforms before execution. "
        "See ReconciliationEngine.__init__ and the QueryRunner class."
    )


if __name__ == "__main__":
    sys.exit(main())
