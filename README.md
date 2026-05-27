# enterprise-ai-gateway

> Vendor-agnostic AI service bus that routes chat, voice, and knowledge requests across LLM, RAG, speech, and service-desk providers — with session memory, policy enforcement, and per-request provider selection.

[![CI](https://github.com/OgeonX-Ai/enterprise-ai-gateway/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/OgeonX-Ai/enterprise-ai-gateway/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[![Coding-Autopilot-System](https://img.shields.io/badge/ecosystem-Coding--Autopilot--System-blue)](https://github.com/Coding-Autopilot-System)

Part of the [Coding-Autopilot-System](https://github.com/Coding-Autopilot-System) ecosystem: [gsd-orchestrator](https://github.com/Coding-Autopilot-System/gsd-orchestrator) | [Promptimprover](https://github.com/Coding-Autopilot-System/Promptimprover) | [autogen](https://github.com/Coding-Autopilot-System/autogen)

**See also:** [OgeonX-Ai/android](https://github.com/OgeonX-Ai/android) — AI voice interaction client for Android

## Architecture

\`\`\`mermaid
flowchart LR
  Client[Web / Agent Client] -->|/v1/chat| GW[API Gateway\nFastAPI]
  GW --> Policy[Policy Engine]
  Policy --> Memory[Session Memory]
  Memory --> RAG[RAG\nAzure AI Search]
  Memory --> LLM[LLM Router\nAzure OpenAI / OpenAI / Anthropic / Ollama]
  GW --> Speech[Speech Services\nSTT / TTS]
  LLM --> SD[Service Desk\nServiceNow / Jira / Remedy]
\`\`\`

The gateway receives requests through a FastAPI endpoint and passes them through a policy engine for input sanitization. Session memory maintains per-conversation context. The core routes to multiple AI providers: LLM inference (Azure OpenAI, OpenAI, Anthropic, Ollama), retrieval-augmented generation (Azure AI Search), speech-to-text and text-to-speech (Azure Speech, Whisper, ElevenLabs), and service desk integration (ServiceNow, Jira Service Management, Remedy). A service registry exposes available capabilities at runtime, and correlation IDs trace requests across all layers.

## Features

- **Multi-LLM routing** — per-request provider selection across Azure OpenAI, OpenAI, Anthropic, and Ollama
- **RAG augmentation** — retrieval-augmented generation against Azure AI Search
- **Speech services** — STT (Azure Speech, faster-whisper, OpenAI Whisper API) and TTS
- **Service desk integration** — intent detection and ticket operations for ServiceNow, Jira SM, and Remedy
- **Policy enforcement** — input sanitization before LLM submission
- **Session memory** — persistent per-session chat history
- **Service registry** — live capability discovery for front-end provider selectors
- **Correlation IDs** — `X-Correlation-ID` header propagated through all layers
- **Debug SSE stream** — `/v1/debug/stream` for live log streaming
- **Kubernetes-ready** — deployment and service manifests included

## Quick Start

\`\`\`bash
git clone https://github.com/OgeonX-Ai/enterprise-ai-gateway.git
cd enterprise-ai-gateway/backend
pip install -r requirements.txt
cp .env.example .env  # configure provider keys as needed
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
\`\`\`

---

Part of the [Coding-Autopilot-System](https://github.com/Coding-Autopilot-System) ecosystem: [gsd-orchestrator](https://github.com/Coding-Autopilot-System/gsd-orchestrator) | [Promptimprover](https://github.com/Coding-Autopilot-System/Promptimprover) | [autogen](https://github.com/Coding-Autopilot-System/autogen)
