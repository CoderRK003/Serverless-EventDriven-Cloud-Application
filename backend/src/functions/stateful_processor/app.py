import json
import os
import time

from common.aws_clients import cloudwatch_client, dynamodb_resource
from common.config import load_config


def handler(event, context):
    """Module 7: Stateful Processing Layer (DynamoDB state).

    This Lambda can be invoked (optionally) after execution to update per-device
    state such as counters and last-seen timestamps.

    Input: { "events": [ ...processed events... ] }
    """

    cfg = load_config()
    events = event.get("events") or []

    ddb = dynamodb_resource()
    state_table = ddb.Table(os.environ["STATE_TABLE"])

    start = time.time()

    for e in events:
        device_id = e.get("device_id", "unknown")
        state_table.update_item(
            Key={"device_id": device_id},
            UpdateExpression="SET last_seen_ts = :t ADD total_events :inc",
            ExpressionAttributeValues={
                ":t": int(time.time() * 1000),
                ":inc": 1,
            },
        )

    cw = cloudwatch_client()
    cw.put_metric_data(
        Namespace=cfg["metrics"]["namespace"],
        MetricData=[
            {"MetricName": "StateUpdates", "Value": float(len(events)), "Unit": "Count"},
            {"MetricName": "StateUpdateLatencyMs", "Value": float((time.time() - start) * 1000), "Unit": "Milliseconds"},
        ],
    )

    return {"ok": True, "updated": len(events)}
