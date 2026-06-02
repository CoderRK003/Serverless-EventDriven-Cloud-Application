import os
import time

from common.aws_clients import dynamodb_resource


def handler(event, context):
    """Real-time support: WebSocket $connect.

    Stores the connectionId in DynamoDB so other Lambdas can broadcast events.
    """

    connection_id = event["requestContext"]["connectionId"]

    ddb = dynamodb_resource()
    table = ddb.Table(os.environ["CONNECTIONS_TABLE"])

    table.put_item(
        Item={
            "connection_id": connection_id,
            "connected_ts": int(time.time() * 1000),
        }
    )

    return {"statusCode": 200, "body": "connected"}
