import os
from datetime import datetime, timedelta, timezone

from common.aws_clients import cloudwatch_client
from common.config import load_config
from common.responses import json_response


def handler(event, context):
    """Module 9: Monitoring & Metrics Collector (API for dashboard).

    The dashboard polls this endpoint to fetch CloudWatch metrics. In production
    you'd likely use CloudWatch dashboards or a streaming pipeline; for a demo,
    polling is simple and reliable.
    """

    cfg = load_config()
    namespace = cfg["metrics"]["namespace"]

    minutes = int((event.get("queryStringParameters") or {}).get("minutes", 15))
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)

    cw = cloudwatch_client()

    metrics = [
        "ExecutionEventsProcessed",
        "ExecutionLatencyMs",
        "AdaptiveBatchSize",
        "BatchDispatchCount",
        "BatchDispatchLatencyMs",
        "StateUpdates",
        "DesiredReservedConcurrency",
        "TotalQueueDepth",
    ]

    out = {}
    for m in metrics:
        resp = cw.get_metric_statistics(
            Namespace=namespace,
            MetricName=m,
            StartTime=start,
            EndTime=end,
            Period=60,
            Statistics=["Average", "Sum"],
        )
        points = sorted(resp.get("Datapoints", []), key=lambda d: d["Timestamp"])
        out[m] = [
            {
                "ts": p["Timestamp"].isoformat(),
                "avg": p.get("Average"),
                "sum": p.get("Sum"),
                "unit": p.get("Unit"),
            }
            for p in points
        ]

    return json_response(200, {"ok": True, "namespace": namespace, "metrics": out})
