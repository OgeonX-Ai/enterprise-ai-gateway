from ..common.errors import PolicyViolation
from ..common.redaction import redact


class PolicyEngine:
    def enforce(self, content: str) -> str:
        if len(content) > 4000:
            raise PolicyViolation("Message too long")
        return redact(content)
