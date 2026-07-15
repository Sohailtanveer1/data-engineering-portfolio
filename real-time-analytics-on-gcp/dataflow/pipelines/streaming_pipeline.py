"""Streaming pipeline: Pub/Sub -> validate -> window -> dedup -> (enrich) ->
BigQuery Bronze, with a raw-archive side sink to GCS and a DLQ side output
to Pub/Sub for anything that fails parsing/validation.

One pipeline, five parallel per-domain branches (orders/inventory/shipments/
returns/suppliers) — they share transform code but write to different
BigQuery tables and only shipments gets the enrichment step, so branching
here is clearer than trying to force everything through one generic path.

    python streaming_pipeline.py \
        --project=$PROJECT_ID --region=us-central1 --environment=dev \
        --runner=DataflowRunner --streaming \
        --staging_location=gs://$PROJECT_ID-dataflow-staging-dev/staging \
        --temp_location=gs://$PROJECT_ID-dataflow-staging-dev/temp \
        --service_account_email=sa-dataflow-worker-dev@$PROJECT_ID.iam.gserviceaccount.com \
        --subnetwork=regions/us-central1/subnetworks/supplychain-dev-subnet \
        --no_use_public_ips \
        --job_name=supplychain-streaming-dev \
        --pipeline_version=$(git rev-parse --short HEAD)

See scripts/deploy_dataflow_pipeline.sh for the Flex Template build+launch
that wraps this for CI/CD.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import apache_beam as beam
from apache_beam.io.gcp.bigquery import BigQueryDisposition, WriteToBigQuery
from apache_beam.io.gcp.pubsub import ReadFromPubSub, WriteToPubSub
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, StandardOptions
from apache_beam.transforms.trigger import AccumulationMode, AfterCount, AfterProcessingTime, AfterWatermark
from apache_beam.transforms.window import FixedWindows
from apache_beam.utils.timestamp import Duration

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from supplychain_common.config import DOMAINS  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "transforms"))
from add_audit_columns import AddAuditColumns  # noqa: E402
from deduplicate import DeduplicateByEventId  # noqa: E402
from enrich_shipment import EnrichShipment  # noqa: E402
from parse_and_validate import DLQ_TAG, VALID_TAG, ParseAndValidate  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("streaming_pipeline")

# Fixed 60s windows, closed on watermark with an early speculative firing
# every 30s (so BigQuery gets data before the window fully closes — this is
# a streaming ingestion pipeline, not a windowed aggregation, so we want
# results as soon as possible) and allowed lateness of 1 hour. An event
# arriving more than an hour after its own event_timestamp, relative to the
# watermark, is dropped from this window and never reaches BigQuery via
# this path — see docs/architecture/watermarking-and-late-data.md for the
# backfill process that covers that gap from the GCS raw archive instead.
WINDOW_SIZE_SECONDS = 60
ALLOWED_LATENESS_SECONDS = 3600


def build_domain_pipeline(pipeline, domain: str, opts: PipelineArgs):
    subscription = f"projects/{opts.project}/subscriptions/supplychain.{domain}.v1.dataflow-sub"
    dlq_topic = f"projects/{opts.project}/topics/supplychain.{domain}.v1.dlq"

    messages = pipeline | f"Read.{domain}" >> ReadFromPubSub(subscription=subscription, with_attributes=True)

    parsed = messages | f"ParseValidate.{domain}" >> beam.ParDo(ParseAndValidate(domain)).with_outputs(
        VALID_TAG, DLQ_TAG
    )

    (
        parsed[DLQ_TAG]
        | f"EncodeDLQ.{domain}" >> beam.Map(lambda rec: json.dumps(rec).encode("utf-8"))
        | f"WriteDLQ.{domain}" >> WriteToPubSub(topic=dlq_topic)
    )

    windowed = parsed[VALID_TAG] | f"Window.{domain}" >> beam.WindowInto(
        FixedWindows(WINDOW_SIZE_SECONDS),
        trigger=AfterWatermark(early=AfterProcessingTime(30), late=AfterCount(1)),
        accumulation_mode=AccumulationMode.DISCARDING,
        allowed_lateness=Duration(seconds=ALLOWED_LATENESS_SECONDS),
    )

    # Raw archive: everything that passed schema validation, BEFORE dedup —
    # a replay/backfill source should hold every observed event, duplicates
    # included, since dedup logic itself might be what you're re-running a
    # backfill to fix.
    (
        windowed
        | f"ToJSON.{domain}" >> beam.Map(lambda r: json.dumps(r.event))
        | f"WriteArchive.{domain}"
        >> beam.io.WriteToText(
            file_path_prefix=f"gs://{opts.raw_archive_bucket}/{domain}/",
            file_name_suffix=".jsonl",
            num_shards=0,
        )
    )

    deduped = (
        windowed
        | f"KeyByEventId.{domain}" >> beam.Map(lambda r: (r.event["event_id"], r))
        | f"Dedup.{domain}" >> beam.ParDo(DeduplicateByEventId())
    )

    if domain == "shipments":
        deduped = deduped | "EnrichShipment" >> beam.ParDo(EnrichShipment(opts.project, opts.carrier_secret_id))

    rows = deduped | f"AddAudit.{domain}" >> beam.ParDo(AddAuditColumns(opts.pipeline_version))

    write_result = rows | f"WriteBQ.{domain}" >> WriteToBigQuery(
        table=f"{opts.project}:supplychain_bronze.{domain}",
        # CREATE_NEVER: the table is Terraform-managed (schema, partitioning,
        # clustering) — Beam must never be allowed to auto-create or
        # implicitly alter it.
        create_disposition=BigQueryDisposition.CREATE_NEVER,
        write_disposition=BigQueryDisposition.WRITE_APPEND,
        method=WriteToBigQuery.Method.STORAGE_WRITE_API,
    )

    (
        write_result.failed_rows_with_errors
        | f"LogBQFailures.{domain}"
        >> beam.Map(lambda failure: logger.error("BIGQUERY_WRITE_FAILURE domain=%s error=%s", domain, failure))
    )


class PipelineArgs(argparse.Namespace):
    project: str
    raw_archive_bucket: str
    carrier_secret_id: str
    pipeline_version: str
    environment: str


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--environment", required=True, choices=["dev", "uat", "prod"])
    parser.add_argument("--raw_archive_bucket", required=True, help="e.g. PROJECT-raw-event-archive-dev")
    parser.add_argument("--carrier_secret_id", default=None, help="defaults to carrier-tracking-api-key-<environment>")
    parser.add_argument("--pipeline_version", required=True, help="git SHA or build tag, for the audit column")
    known_args, pipeline_argv = parser.parse_known_args(argv)
    if known_args.carrier_secret_id is None:
        known_args.carrier_secret_id = f"carrier-tracking-api-key-{known_args.environment}"
    return known_args, pipeline_argv


def run(argv=None):
    opts, pipeline_argv = parse_args(argv)

    pipeline_options = PipelineOptions(pipeline_argv)
    pipeline_options.view_as(StandardOptions).streaming = True
    pipeline_options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=pipeline_options) as pipeline:
        for domain in DOMAINS:
            build_domain_pipeline(pipeline, domain, opts)


if __name__ == "__main__":
    run(sys.argv[1:])
