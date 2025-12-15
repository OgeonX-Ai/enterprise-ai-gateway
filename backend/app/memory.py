from typing import Dict, List


class MemoryStore:
    """Simple in-memory conversation history keyed by session id."""

    def __init__(self) -> None:
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self._sessions.get(session_id, [])

    def append(self, session_id: str, sender: str, content: str) -> None:
        history = self._sessions.setdefault(session_id, [])
        history.append({"sender": sender, "content": content})

    def reset(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
