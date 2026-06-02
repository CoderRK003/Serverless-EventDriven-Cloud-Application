import json
import os
import time

from common.aws_clients import cloudwatch_client, dynamodb_resource, lambda_client
from common.config import load_config


def _process_one(e: dict) -> dict:
    """User-defined function placeholder.

    For demo/academic purposes, we compute a simple derived value and tag the
    event as processed.
    """

    payload = e.get("payload") or {}
    value = payload.get("value", 0)
    derived = float(value) * 1.5

    return {
        **e,
        "processed": True,
        "derived": derived,
        "processed_ts": int(time.time() * 1000),
    }


def handler(event, context):
    """Module 6: Serverless Execution Engine (Lambda, Python).

    Input: { "events": [ ... ] }
    Output is written into DynamoDB (results table) and metrics are pushed to CloudWatch.
    """

    cfg = load_config()
    events = event.get("events") or []
    ws_broadcast_fn = os.getenv("WS_BROADCAST_LAMBDA")

    ddb = dynamodb_resource()
    results_table = ddb.Table(os.environ["RESULTS_TABLE"])

    cw = cloudwatch_client()

    start = time.time()
    processed = [_process_one(e) for e in events]

    for item in processed:
        results_table.put_item(
            Item={
                "event_id": item["event_id"],
                "ts": int(item["ts"]),
                "event_type": item.get("event_type", "telemetry"),
                "priority": item.get("priority", "normal"),
                "device_id": item.get("device_id", "unknown"),
                "trace_id": item.get("trace_id"),
                "result_json": json.dumps(item),
            }
        )

    elapsed_ms = (time.time() - start) * 1000

    cw.put_metric_data(
        Namespace=cfg["metrics"]["namespace"],
        MetricData=[
            {"MetricName": "ExecutionEventsProcessed", "Value": float(len(processed)), "Unit": "Count"},
            {"MetricName": "ExecutionLatencyMs", "Value": float(elapsed_ms), "Unit": "Milliseconds"},
        ],
    )

    if ws_broadcast_fn and processed:
        lam = lambda_client()
        lam.invoke(
            FunctionName=ws_broadcast_fn,
            InvocationType="Event",
            Payload=json.dumps({"type": "processed", "data": processed[:50]}).encode("utf-8"),
        )

    return {"ok": True, "processed": len(processed), "latency_ms": elapsed_ms}
