import json
import os

from common.aws_clients import dynamodb_resource
from common.config import load_config
from common.responses import json_response


def handler(event, context):
    """Module 12: Deployment & Configuration Manager (API + DynamoDB).

    GET  -> returns active config
    POST -> updates active config in DynamoDB (demo-only)

    Note: For simplicity, the SAM template will create a Config table with a
    single item key (config_id='active').
    """

    method = (event.get("requestContext") or {}).get("http", {}).get("method") or event.get("httpMethod")
    method = (method or "GET").upper()

    table_name = os.environ.get("CONFIG_TABLE")
    if not table_name:
        return json_response(500, {"ok": False, "error": "CONFIG_TABLE env var not set"})

    ddb = dynamodb_resource()
    table = ddb.Table(table_name)

    if method == "GET":
        cfg = load_config()
        return json_response(200, {"ok": True, "config": cfg})

    if method == "POST":
        body = event.get("body")
        payload = json.loads(body) if isinstance(body, str) else (body or {})

        table.put_item(Item={"config_id": "active", "config_json": json.dumps(payload)})
        return json_response(200, {"ok": True})

    return json_response(405, {"ok": False, "error": "Method not allowed"})
