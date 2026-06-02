import json
import os

from common.aws_clients import apigw_mgmt_client, dynamodb_resource


def handler(event, context):
    """Real-time support: broadcast messages to all connected dashboard clients.

    Other modules can invoke this Lambda async with a payload like:
      {"type":"event", "data": {...}}

    WebSocket management API endpoint is provided via WS_API_ENDPOINT.
    """

    endpoint = os.environ["WS_API_ENDPOINT"]
    con_table = os.environ["CONNECTIONS_TABLE"]

    body = event if isinstance(event, dict) else {"data": event}
    data = json.dumps(body).encode("utf-8")

    ddb = dynamodb_resource()
    table = ddb.Table(con_table)

    resp = table.scan(Limit=500)
    items = resp.get("Items", [])

    mgmt = apigw_mgmt_client(endpoint_url=endpoint)

    stale = []
    for it in items:
        cid = it["connection_id"]
        try:
            mgmt.post_to_connection(ConnectionId=cid, Data=data)
        except Exception:
            stale.append(cid)

    for cid in stale:
        table.delete_item(Key={"connection_id": cid})

    return {"ok": True, "sent": len(items) - len(stale), "stale": len(stale)}
