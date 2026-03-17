# PlanMyBerlin – AGENTS Guide

## Project overview
PlanMyBerlin is a Berlin-focused travel and itinerary planning assistant.
It helps visitors design realistic day-by-day plans tailored to interests, budget, and time, using local knowledge about Berlin’s neighbourhoods, attractions, and transport.

## Tech stack and tools
- Language: Python 3.13.9
- Package & env management: uv (no requirements.txt)
- UI: Streamlit
- LLM / orchestration: LangChain (OpenAI models)
- Vector store: Chroma (local, persisted under `data/vectorstore/`)

## Conventions and rules
- Secrets: API keys and credentials live in `.env` and are never committed.
- Dependency management: all packages are added via `uv` only.
- Scope: Only Berlin travel; no worldwide travel planning.
- Safety: No bookings, payments, or real-time availability; purely planning and guidance.

## Planned components (high-level)
- `rag/`: ingestion, chunking, embeddings, retrieval
- `tools/`: itinerary builder, budget estimator, time/distance helpers
- `ui/`: Streamlit app and interaction flows
- `data/`: local knowledge base (Berlin-specific content)

