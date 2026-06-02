import os

from common.aws_clients import cloudwatch_client, lambda_client, sqs_client
from common.config import load_config


def _desired_concurrency(cfg: dict, total_queue_depth: int) -> int:
    s = cfg["scaling"]
    min_c = int(s["minReservedConcurrency"])
    max_c = int(s["maxReservedConcurrency"])

    out_th = int(s["queueDepthScaleOutThreshold"])
    in_th = int(s["queueDepthScaleInThreshold"])

    if total_queue_depth >= out_th:
        return max_c
    if total_queue_depth <= in_th:
        return min_c

    ratio = (total_queue_depth - in_th) / max(1, (out_th - in_th))
    desired = min_c + int((max_c - min_c) * ratio)
    return max(min_c, min(max_c, desired))


def handler(event, context):
    """Module 8: Dynamic Auto-Scaling Controller.

    For demo simplicity, this function is triggered on a schedule (EventBridge).
    It reads SQS depth and updates Reserved Concurrency on the execution Lambda.

    Note: This is an academic visualization of scaling logic; real systems use
    target tracking, provisioned concurrency, and more safeguards.
    """

    cfg = load_config()

    sqs = sqs_client()
    q_urls = [
        os.getenv("INGRESS_QUEUE_URL"),
        os.environ["DEFAULT_QUEUE_URL"],
        os.environ["HIGH_PRIORITY_QUEUE_URL"],
    ]

    depths = []
    for url in q_urls:
        if not url:
            continue
        attrs = sqs.get_queue_attributes(
            QueueUrl=url,
            AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
        )["Attributes"]
        depths.append(int(attrs.get("ApproximateNumberOfMessages", 0)) + int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)))

    total_depth = sum(depths)
    desired = _desired_concurrency(cfg, total_depth)

    exec_fn = os.environ["EXECUTION_LAMBDA_NAME"]
    lam = lambda_client()

    lam.put_function_concurrency(FunctionName=exec_fn, ReservedConcurrentExecutions=desired)

    cw = cloudwatch_client()
    cw.put_metric_data(
        Namespace=cfg["metrics"]["namespace"],
        MetricData=[
            {"MetricName": "DesiredReservedConcurrency", "Value": float(desired), "Unit": "Count"},
            {"MetricName": "TotalQueueDepth", "Value": float(total_depth), "Unit": "Count"},
        ],
    )

    return {"ok": True, "queue_depth": total_depth, "desired_reserved_concurrency": desired}
