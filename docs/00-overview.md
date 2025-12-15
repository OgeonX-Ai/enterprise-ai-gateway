# Overview

The Enterprise AI Gateway is a single backend runtime that exposes a vendor-agnostic control plane for conversational agents. It owns session memory, applies policy, and orchestrates connectors for LLM, RAG/Search, speech (STT/TTS), and service desk systems while presenting a unified API and static web client.

## Problem it solves
- Fragmented integrations across multiple bots and channels
- Duplicated prompts and inconsistent governance
- Secrets leaking into clients when each tool calls vendors directly
- High coupling between UI and downstream providers

## Why gateway-owned agents
- Centralized policy enforcement (PII redaction, rate limits)
- Shared memory and context for all channels
- Pluggable connectors that can swap between mocks, stubs, and production providers without UI changes
- Single audit surface for observability and compliance

## Supported channels and services (current demo)
- Channels: web (live), stubs for Teams and IVR routes
- LLM providers: mock, Azure OpenAI stub
- RAG/Search: mock search, Azure AI Search stub
- Speech: mock STT/TTS, Azure Speech stub
- Service desk: ServiceNow, Remedy, Jira Service Management stubs

## Glossary
- **Connector**: Adapter that implements a service contract (LLM, RAG, STT/TTS, ServiceDesk).
- **Provider**: A concrete implementation registered for a connector type (e.g., `azure-openai`).
- **Policy**: Redaction and guardrails executed before any downstream calls.
- **Runtime**: Orchestration pipeline that builds context, calls connectors, and shapes the response.
- **Session**: Gateway-owned conversational thread with stored turns and correlation IDs.
