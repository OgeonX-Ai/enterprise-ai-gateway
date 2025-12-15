# Large Language Model (LLM) Provider Matrix

This document lists practical LLM options supported by the Enterprise AI Gateway.
The goal is to allow seamless routing from Speech-to-Text (STT) output into:
- Local LLMs
- Cloud LLM APIs
- Enterprise-grade platforms
- Tool- and function-calling workflows

---

## 1. Local / Self-Hosted LLMs

| LLM | Runtime | Tool Calling | Pros | Cons | Verdict |
|----|--------|--------------|------|------|--------|
| LLaMA.cpp | CPU/GPU | Partial | Fully local, privacy | Slow on CPU | Good |
| Ollama | CPU/GPU | Partial | Easy local dev | Model limits | Very good |
| LM Studio | GPU | Partial | GUI + local | Closed UX | OK |
| Mistral (local) | GPU | Partial | Fast, strong | Needs GPU | Good |

---

## 2. Public Cloud LLM APIs

| Provider | Models | Tool Calling | Pros | Cons | Verdict |
|-------|--------|--------------|------|------|--------|
| Azure OpenAI | GPT-4.x, GPT-4o | Yes | Enterprise, EU-ready | Paid | **Best enterprise LLM** |
| OpenAI | GPT-4.x | Yes | Best reasoning | Compliance | Good |
| Anthropic | Claude 3.x | Yes | Long context | No STT | Good |
| Google Gemini | Gemini 1.x | Partial | Fast | Weak FI | OK |

---

## 3. Combined Platforms (STT + LLM)

| Platform | STT | LLM | Tool Calling | Finnish | Verdict |
|--------|-----|-----|--------------|---------|--------|
| Azure AI | Yes | Yes | Yes | ⭐⭐⭐⭐⭐ | **Best combo** |
| Google Vertex | Yes | Yes | Partial | ⭐⭐⭐⭐ | OK |
| OpenAI Platform | Whisper | Yes | Yes | ⭐⭐⭐⭐⭐ | Batch only |

---

## 4. LLM Output Contract (Gateway Standard)

```json
{
  "text": "LLM response",
  "model": "gpt-4o-mini",
  "provider": "azure-openai",
  "tool_calls": [
    { "tool": "servicenow.create_ticket", "args": {} }
  ],
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 456
  }
}
```

---

## 5. Key Insight

There is no single system that cleanly combines:

- Best Finnish STT
- Local execution
- Enterprise LLM reasoning
- Tool calling
- ServiceDesk automation
- Voice callbacks

The Enterprise AI Gateway exists to orchestrate these.
