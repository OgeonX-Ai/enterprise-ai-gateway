from typing import Dict, List

from ..models import ChatMessage


class MemoryStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, List[ChatMessage]] = {}

    def create_session(self, session_id: str) -> None:
        self._sessions.setdefault(session_id, [])

    def append_turn(self, session_id: str, message: ChatMessage) -> None:
        self._sessions.setdefault(session_id, []).append(message)

    def history(self, session_id: str) -> List[ChatMessage]:
        return self._sessions.get(session_id, [])
