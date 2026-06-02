import os

from common.aws_clients import dynamodb_resource


def handler(event, context):
    """Real-time support: WebSocket $disconnect."""

    connection_id = event["requestContext"]["connectionId"]

    ddb = dynamodb_resource()
    table = ddb.Table(os.environ["CONNECTIONS_TABLE"])

    table.delete_item(Key={"connection_id": connection_id})

    return {"statusCode": 200, "body": "disconnected"}
