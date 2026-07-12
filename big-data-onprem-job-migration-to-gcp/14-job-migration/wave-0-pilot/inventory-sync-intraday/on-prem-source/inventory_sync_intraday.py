"""
inventory_sync_intraday.py — ON-PREM ORIGINAL (Spark 2.4.8, PySpark).

Runs every 15 minutes via cron (see run_inventory_sync.sh and
crontab-entry.txt), reconciling WMS-reported on-hand quantity changes
(landed via Kafka -> HDFS staging, out of this job's scope) into the
authoritative on-hand-by-warehouse table used by the storefront
availability feed.

Known issues (do not fix here — see ../migration-record.md):
  - Hardcoded paths, no config externalization
  - No idempotency guard: a re-run for the same window double-applies
    quantity deltas, since deltas are ADDED, not set to an absolute value
  - No negative-on-hand-quantity check — a delta-application bug can
    silently drive quantity negative, which is a real (if rare)
    upstream-consumer-visible bug reported twice in the last 6 months
    per operations interview
  - No structured retry; a transient HDFS read failure just fails the run
    and waits for the next 15-minute cron tick — SLA-relevant since a
    missed run compounds (next run only sees the newest window's deltas,
    the missed window's deltas are silently lost, not caught up)
"""

import sys
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions as F

HDFS_DELTA_STAGING = "hdfs://nn01.internal.acme.com:8020/data/inventory/wms_delta_staging/"
HIVE_ON_HAND_TABLE = "inventory.on_hand_by_warehouse"


def main():
    if len(sys.argv) < 2:
        print("Usage: inventory_sync_intraday.py <window_id, e.g. 2026-07-12T0815>")
        sys.exit(1)
    window_id = sys.argv[1]

    conf = SparkConf().setAppName("inventory_sync_intraday")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)

    deltas = sqlContext.read.parquet(HDFS_DELTA_STAGING + "window=" + window_id + "/")
    current = sqlContext.read.table(HIVE_ON_HAND_TABLE)

    # Sum deltas per (warehouse, sku) in case this window has multiple
    # WMS events for the same item.
    net_deltas = deltas.groupBy("warehouse_id", "sku").agg(F.sum("quantity_delta").alias("net_delta"))

    updated = current.join(net_deltas, on=["warehouse_id", "sku"], how="outer")
    updated = updated.withColumn(
        "on_hand_quantity",
        F.coalesce(F.col("on_hand_quantity"), F.lit(0)) + F.coalesce(F.col("net_delta"), F.lit(0)),
    ).select("warehouse_id", "sku", "on_hand_quantity")

    # NON-IDEMPOTENT: this OVERWRITES the whole table with the recomputed
    # state every run. If this run is re-triggered manually after a
    # partial failure, and the delta-staging directory for this window_id
    # has since been partially cleaned up by another process, the
    # recomputed on_hand_quantity will be wrong and silently written over
    # the previous (correct) value. Flagged as the highest-priority fix
    # in migration — see ../migration-record.md.
    updated.write.mode("overwrite").insertInto(HIVE_ON_HAND_TABLE, overwrite=True)

    print("inventory_sync_intraday complete for window %s" % window_id)
    sc.stop()


if __name__ == "__main__":
    main()
