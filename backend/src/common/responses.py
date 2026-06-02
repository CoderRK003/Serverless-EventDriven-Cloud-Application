import json
from typing import Any, Dict, Optional


def json_response(status_code: int, body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    base_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
    }
    if headers:
        base_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": base_headers,
        "body": json.dumps(body, default=str),
    }
