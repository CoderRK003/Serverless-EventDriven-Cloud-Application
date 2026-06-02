import json
import os

from boto3.dynamodb.conditions import Key

from common.aws_clients import dynamodb_resource
from common.responses import json_response


def handler(event, context):
    """Module 11: Result Processing & Storage (API for dashboard).

    Returns the most recent processed results from DynamoDB.
    """

    limit = int((event.get("queryStringParameters") or {}).get("limit", 50))

    ddb = dynamodb_resource()
    table = ddb.Table(os.environ["RESULTS_TABLE"])

    resp = table.scan(Limit=limit)
    items = resp.get("Items", [])

    items_sorted = sorted(items, key=lambda x: int(x.get("ts", 0)), reverse=True)[:limit]

    for it in items_sorted:
        if "result_json" in it and isinstance(it["result_json"], str):
            try:
                it["result"] = json.loads(it["result_json"])
            except Exception:
                it["result"] = it["result_json"]

    return json_response(200, {"ok": True, "items": items_sorted})
