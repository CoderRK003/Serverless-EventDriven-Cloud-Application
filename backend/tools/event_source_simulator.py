import argparse
import json
import random
import time
import uuid

import requests


def _make_event(device_id: str, event_type: str, priority: str) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "priority": priority,
        "device_id": device_id,
        "ts": int(time.time() * 1000),
        "payload": {
            "value": random.randint(0, 100),
            "temp": random.uniform(18.0, 40.0),
        },
    }


def main():
    """Module 1: Event Source Simulator.

    Sends synthetic IoT-like events to API Gateway endpoint.

    Usage:
      python backend/tools/event_source_simulator.py --url https://.../events --eps 5
    """

    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--eps", type=int, default=5)
    p.add_argument("--device", default="device-1")
    args = p.parse_args()

    event_types = ["telemetry", "alert", "heartbeat"]
    priorities = ["low", "normal", "high"]

    delay = 1.0 / max(args.eps, 1)

    while True:
        ev = _make_event(
            device_id=args.device,
            event_type=random.choice(event_types),
            priority=random.choices(priorities, weights=[0.7, 0.25, 0.05])[0],
        )
        r = requests.post(args.url, json=ev, timeout=10)
        print(r.status_code, r.text)
        time.sleep(delay)


if __name__ == "__main__":
    main()
