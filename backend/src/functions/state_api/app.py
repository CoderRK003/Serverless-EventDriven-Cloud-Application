import os

from common.aws_clients import dynamodb_resource
from common.responses import json_response


def handler(event, context):
    """Module 7 (UI support): Stateful Data Visualization API.

    Returns per-device state from DynamoDB.
    """

    limit = int((event.get("queryStringParameters") or {}).get("limit", 50))

    ddb = dynamodb_resource()
    table = ddb.Table(os.environ["STATE_TABLE"])

    resp = table.scan(Limit=limit)
    items = resp.get("Items", [])
    items_sorted = sorted(items, key=lambda x: int(x.get("last_seen_ts", 0)), reverse=True)[:limit]

    return json_response(200, {"ok": True, "items": items_sorted})
