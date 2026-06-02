import json
import os

from common.aws_clients import sqs_client
from common.responses import json_response


def _route_message(msg: dict) -> str:
    priority = (msg.get("priority") or "normal").lower()
    if priority == "high":
        return os.environ["HIGH_PRIORITY_QUEUE_URL"]
    return os.environ["DEFAULT_QUEUE_URL"]


def handler(event, context):
    """Module 4: Event Router (SQS -> Lambda -> SQS).

    Reads messages from the ingress queue and routes them to queue(s) based on
    event type / priority.

    Note: With AWS, routing can also be implemented using SNS, EventBridge, or
    multiple API routes. Here we keep it simple and explicit.
    """

    sqs = sqs_client()

    records = event.get("Records", [])
    for r in records:
        body = json.loads(r["body"])
        out_queue = _route_message(body)
        sqs.send_message(
            QueueUrl=out_queue,
            MessageBody=json.dumps(body),
            MessageAttributes=r.get("messageAttributes") or {},
        )

    return json_response(200, {"ok": True, "routed": len(records)})
