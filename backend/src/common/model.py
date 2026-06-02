from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


EventType = Literal["telemetry", "alert", "heartbeat"]
Priority = Literal["low", "normal", "high"]


@dataclass
class Event:
    event_id: str
    event_type: EventType
    priority: Priority
    device_id: str
    ts: int
    payload: Dict[str, Any]
    trace_id: Optional[str] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Event":
        return Event(
            event_id=str(d["event_id"]),
            event_type=d["event_type"],
            priority=d.get("priority", "normal"),
            device_id=str(d.get("device_id", "unknown")),
            ts=int(d["ts"]),
            payload=dict(d.get("payload", {})),
            trace_id=d.get("trace_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "priority": self.priority,
            "device_id": self.device_id,
            "ts": self.ts,
            "payload": self.payload,
            "trace_id": self.trace_id,
        }
