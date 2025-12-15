from typing import Optional


class RuntimeRouter:
    def should_open_ticket(self, message: str) -> Optional[str]:
        lowered = message.lower()
        if "incident" in lowered or "ticket" in lowered:
            return "create"
        if "status" in lowered:
            return "status"
        return None
