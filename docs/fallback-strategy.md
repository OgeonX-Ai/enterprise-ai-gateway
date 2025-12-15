# Provider Fallback Strategy

The Enterprise AI Gateway supports automatic fallback between providers.

---

## 1. STT Fallback

Order:
1. Local Whisper
2. Azure Speech
3. Third-party STT (Deepgram)

Triggers:
- Timeout
- High latency
- Low confidence

---

## 2. LLM Fallback

Order:
1. Azure OpenAI
2. OpenAI
3. Local Ollama

Triggers:
- API errors
- Rate limits
- Cost thresholds

---

## 3. Policy Controls

- Max latency
- Max cost per request
- Language constraints
- Privacy requirements

---

## 4. Observability

Fallback events are logged with:
- request_id
- provider_before
- provider_after
- reason
