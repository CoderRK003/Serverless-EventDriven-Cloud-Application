import os
from datetime import datetime, timedelta, timezone

from common.aws_clients import logs_client
from common.responses import json_response


def handler(event, context):
    """Module 10 (UI support): Logging & Alerts API (CloudWatch Logs Insights).

    This endpoint is designed for a demo dashboard.

    - If `queryId` is provided (GET), it returns the query results.
    - Otherwise it starts a new Insights query and returns the created `queryId`.

    Query defaults to errors/warnings across the main Lambda log groups.
    """

    params = event.get("queryStringParameters") or {}
    query_id = params.get("queryId")

    logs = logs_client()

    if query_id:
        resp = logs.get_query_results(queryId=query_id)
        return json_response(
            200,
            {
                "ok": True,
                "queryId": query_id,
                "status": resp.get("status"),
                "results": resp.get("results", []),
            },
        )

    minutes = int(params.get("minutes", 15))
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)

    # Keep the list small and explicit for academic clarity.
    log_groups = [
        f"/aws/lambda/{os.environ.get('AWS_LAMBDA_FUNCTION_NAME', '')}",
    ]

    # Use provided logGroups if sent from UI (comma-separated)
    lg = params.get("logGroups")
    if lg:
        log_groups = [x.strip() for x in lg.split(",") if x.strip()]

    query_string = params.get(
        "query",
        "fields @timestamp, @message | filter @message like /ERROR|Error|Exception|WARN/ | sort @timestamp desc | limit 50",
    )

    resp = logs.start_query(
        logGroupNames=log_groups,
        startTime=int(start.timestamp()),
        endTime=int(end.timestamp()),
        queryString=query_string,
    )

    return json_response(
        200,
        {
            "ok": True,
            "queryId": resp["queryId"],
            "status": "Running",
            "note": "Call this endpoint again with ?queryId=... to fetch results.",
        },
    )
