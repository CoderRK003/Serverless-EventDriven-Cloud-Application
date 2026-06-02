import json
import os
from functools import lru_cache
from pathlib import Path

from common.aws_clients import dynamodb_resource


@lru_cache(maxsize=1)
def load_config() -> dict:
    """Load central deployment configuration.

    Priority:
    1) CONFIG_JSON env var (inline JSON)
    2) CONFIG_PATH env var (path to JSON)
    3) ../../config/deployment_config.json (repo default)
    """

    inline = os.getenv("CONFIG_JSON")
    if inline:
        return json.loads(inline)

    config_path = os.getenv("CONFIG_PATH")
    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    repo_default = (
        Path(__file__).resolve().parents[3] / "config" / "deployment_config.json"
    )

    table_name = os.getenv("CONFIG_TABLE")
    config_id = os.getenv("CONFIG_ID", "active")
    if table_name:
        ddb = dynamodb_resource()
        table = ddb.Table(table_name)
        item = table.get_item(Key={"config_id": config_id}).get("Item")
        if item and item.get("config_json"):
            return json.loads(item["config_json"])

    with open(repo_default, "r", encoding="utf-8") as f:
        return json.load(f)
