# Voice Interaction Pipeline

This document describes real-time and asynchronous voice workflows supported by the Enterprise AI Gateway.

---

## 1. Live Voice Interaction (Push-to-Talk)

Flow:
Microphone →
STT →
LLM →
Tool Calls →
TTS →
Speaker

Used for:
- Live commands
- Ticket queries
- Status checks

---

## 2. Voice Callback on Ticket Update

Flow:
ServiceNow Webhook →
Gateway →
LLM Summary →
TTS →
Outbound Call (Twilio)

Used for:
- Incident updates
- SLA warnings
- Resolution notifications

---

## 3. Channels

| Channel | Direction | Notes |
|------|----------|------|
| web | bidirectional | Browser UI |
| phone | outbound | Twilio |
| ivr | inbound | SIP/Twilio |
| mobile | bidirectional | Future |

---

## 4. Audio Formats

- Input: WAV 16kHz mono (preferred)
- Output: WAV / MP3

---

## 5. Provider Strategy

- Local STT preferred when GPU available
- Cloud STT fallback when latency required
- TTS typically cloud-based for quality
