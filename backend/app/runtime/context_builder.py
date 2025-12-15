from typing import Any, Dict, List

from ..models import ChatMessage


class ContextBuilder:
    def build(self, history: List[ChatMessage], rag_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        conversation = [{"role": msg.role, "content": msg.content} for msg in history]
        if rag_results:
            snippets = "\n".join([item["snippet"] for item in rag_results])
            conversation.append({"role": "system", "content": f"Knowledge snippets:\n{snippets}"})
        return conversation
