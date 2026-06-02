import json
import os
import time
import uuid

from common.aws_clients import sqs_client
from common.aws_clients import lambda_client
from common.config import load_config
from common.responses import json_response


def handler(event, context):
    """Module 2: Event Ingestion Service (API Gateway -> Lambda).

    Receives a single event (or a list of events) and enqueues them into SQS.
    """

    cfg = load_config()
    queue_url = os.getenv("INGRESS_QUEUE_URL") or os.environ["DEFAULT_QUEUE_URL"]
    ws_broadcast_fn = os.getenv("WS_BROADCAST_LAMBDA")

    try:
        body = event.get("body")
        payload = json.loads(body) if isinstance(body, str) else (body or {})

        items = payload if isinstance(payload, list) else [payload]
        now_ms = int(time.time() * 1000)
        trace_id = str(uuid.uuid4())

        sqs = sqs_client()
        entries = []
        for idx, item in enumerate(items[:10]):
            item.setdefault("event_id", str(uuid.uuid4()))
            item.setdefault("ts", now_ms)
            item.setdefault("event_type", "telemetry")
            item.setdefault("priority", "normal")
            item.setdefault("device_id", "device-1")
            item.setdefault("trace_id", trace_id)

            entries.append(
                {
                    "Id": str(idx),
                    "MessageBody": json.dumps(item),
                    "MessageAttributes": {
                        "event_type": {"StringValue": item["event_type"], "DataType": "String"},
                        "priority": {"StringValue": item["priority"], "DataType": "String"},
                        "trace_id": {"StringValue": trace_id, "DataType": "String"},
                    },
                }
            )

        resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)

        if ws_broadcast_fn:
            lam = lambda_client()
            lam.invoke(
                FunctionName=ws_broadcast_fn,
                InvocationType="Event",
                Payload=json.dumps({"type": "ingest", "data": items}).encode("utf-8"),
            )

        return json_response(
            200,
            {
                "ok": True,
                "enqueued": len(entries),
                "failed": len(resp.get("Failed", [])),
                "trace_id": trace_id,
                "queues": {
                    "default": cfg["routing"]["defaultQueue"],
                    "high": cfg["routing"]["highPriorityQueue"],
                },
            },
        )
    except Exception as e:
        return json_response(500, {"ok": False, "error": str(e)})
