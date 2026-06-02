import os

from common.aws_clients import sqs_client
from common.responses import json_response


def handler(event, context):
    """Queue Depth Visualization API.

    Returns ApproximateNumberOfMessages and ApproximateNumberOfMessagesNotVisible
    for the default and high priority queues.
    """

    sqs = sqs_client()

    queues = {
        "ingress": os.getenv("INGRESS_QUEUE_URL"),
        "default": os.environ["DEFAULT_QUEUE_URL"],
        "high": os.environ["HIGH_PRIORITY_QUEUE_URL"],
    }

    out = {}
    for name, url in queues.items():
        if not url:
            continue
        attrs = sqs.get_queue_attributes(
            QueueUrl=url,
            AttributeNames=[
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
            ],
        )["Attributes"]

        out[name] = {
            "visible": int(attrs.get("ApproximateNumberOfMessages", 0)),
            "inflight": int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)),
        }

    return json_response(200, {"ok": True, "queues": out})
