import json
import os
import time
from statistics import mean

from common.aws_clients import cloudwatch_client, lambda_client
from common.config import load_config


def _choose_batch_size(cfg: dict, queue_depth: int) -> int:
    b = cfg["batching"]
    min_b, max_b = int(b["minBatchSize"]), int(b["maxBatchSize"])

    if queue_depth <= 0:
        return min_b

    if queue_depth > 500:
        return max_b

    scaled = min_b + int((max_b - min_b) * min(queue_depth, 500) / 500)
    return max(min_b, min(max_b, scaled))


def handler(event, context):
    """Module 5: Adaptive Batching Engine (SQS -> Lambda).

    This Lambda receives routed SQS messages. It dynamically decides a batch size
    and invokes the serverless execution engine with that batch.

    For a demo framework, we treat the current batch (invocation payload) as the
    'batch' and publish batch-size metrics to CloudWatch.
    """

    cfg = load_config()
    exec_fn = os.environ["EXECUTION_LAMBDA_NAME"]

    records = event.get("Records", [])
    events = [json.loads(r["body"]) for r in records]

    queue_depth_hint = int(os.getenv("QUEUE_DEPTH_HINT", "0"))
    batch_size = _choose_batch_size(cfg, queue_depth_hint)

    batches = [events[i : i + batch_size] for i in range(0, len(events), batch_size)]

    lam = lambda_client()
    cw = cloudwatch_client()

    latencies = []
    for b in batches:
        start = time.time()
        lam.invoke(
            FunctionName=exec_fn,
            InvocationType="Event",
            Payload=json.dumps({"events": b}).encode("utf-8"),
        )
        latencies.append((time.time() - start) * 1000)

    cw.put_metric_data(
        Namespace=cfg["metrics"]["namespace"],
        MetricData=[
            {"MetricName": "AdaptiveBatchSize", "Value": float(batch_size), "Unit": "Count"},
            {"MetricName": "BatchDispatchCount", "Value": float(len(batches)), "Unit": "Count"},
            {"MetricName": "BatchDispatchLatencyMs", "Value": float(mean(latencies) if latencies else 0.0), "Unit": "Milliseconds"},
        ],
    )

    return {"ok": True, "batch_size": batch_size, "batches": len(batches)}
