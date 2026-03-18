# Optional tasks — What we implement (PlanMyBerlin)

This document records which optional Sprint 2 tasks we implement for **PlanMyBerlin** and how. We will fill it gradually, **after** each optional task is complete.

---

## Easy

*(Not implemented yet — we will document tasks here as we complete them.)*

### Easy #1 — Add conversation history and export functionality

- **Status:** ✅ Implemented  
- **Summary:** We added a per-session **plan history** and simple export options. Every time the user generates a plan, the app stores `{request, result}` in `st.session_state["history"]` (keeping the last 10 entries). A “Previous plans (this session)” expander lets the user re-load any earlier plan (request + result) without re-running the pipeline. Under the current plan, two **download buttons** allow exporting the itinerary: (1) **JSON** (`profile`, `itinerary`, `budget`, `transport`) and (2) a readable **text** summary (days, segments, and total budget). This satisfies “conversation history and export” without changing the RAG or tools logic.

### Easy #2 — Add visualisation of RAG process

- **Status:** ✅ Implemented  
- **Summary:** After generating a plan, the UI now shows a collapsed expander **“RAG retrieval debug (how we chose candidates)”**. It displays:
  - the exact **sights retrieval query** used for Chroma search,
  - a short list of **top retrieved sights snippet previews**,
  - the exact **restaurants retrieval query** used for Chroma search,
  - a short list of **top retrieved restaurant snippet previews**.

  Additionally, it now shows a **similarity score per retrieved snippet** (Chroma distance as returned by `similarity_search_with_score`). This is an informational “how the retrieval worked” view, not a hard guarantee of correctness.

Implementation-wise, the retrieval queries and preview snippets are generated in `planmyberlin/rag/planning.py` and passed through `planmyberlin/tools/pipeline.py` into the final result dict, then rendered in `planmyberlin/ui/app.py`.

### Easy #3 — Include source citations in responses

- **Status:** ✅ Implemented  
- **Summary:** Each itinerary segment (sights + restaurants) now includes an inline citation label derived from the original retrieved markdown source file (e.g. `places_berlin.md` → `places: <Place Name>`, `restaurants_berlin.md` → `restaurants: <Restaurant Name>`). The citation is displayed next to the segment in the Streamlit UI and included in the exported text summary. This is implemented by:
  - adding `citation` fields during parsing in `planmyberlin/tools/parsing.py`,
  - carrying them into itinerary segments in `planmyberlin/tools/itinerary_builder.py`,
  - rendering them inline in `planmyberlin/ui/app.py`.

### Easy #4 — Add an interactive help feature or chatbot guide

- **Status:** ✅ Implemented  
- **Summary:** Added an in-UI **request helper** expander (“Help me write my request”). It includes:
  - 4 clickable **example prompts** that fill the main request box via `st.session_state` and re-run the page.
  - A lightweight **template builder** (days, budget level, pace, districts, interests, food style, transport preference) that composes a well-structured request string without additional LLM calls.

This satisfies “interactive help / chatbot guide” at an easy, stable MVP level by helping users provide better inputs for PlanMyBerlin.

---

## Medium

*(Not implemented yet — we will document tasks here as we complete them.)*

### Medium #1 — Implement multi-model support (OpenAI, Anthropic, etc.)

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Medium #2 — Add real-time data updates to knowledge base

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Medium #3 — Implement advanced caching strategies

- **Status:** ✅ Implemented  
- **Summary:** Added a Streamlit cache (`st.cache_data`) around the end-to-end pipeline call. Identical user requests reuse the previously computed result (TripProfile parsing, RAG retrieval, itinerary building, budget estimation, and transport guidance) for up to 1 hour (`ttl=3600`). This reduces repeated OpenAI API calls and makes the UI feel faster while keeping the underlying RAG/docs logic unchanged.

### Medium #4 — Add user authentication and personalisation

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Medium #5 — Calculate and display token usage and costs

- **Status:** ✅ Implemented  
- **Summary:** Added token/cost visibility in the Streamlit UI. The backend now captures OpenAI token usage via LangChain’s `get_openai_callback` during the planning pipeline run and returns it as `token_usage`, which is rendered in a dedicated expander (“Token usage & estimated cost”). The value is also included in the exported plan JSON.

### Medium #6 — Add visualisation of tool call results

- **Status:** ✅ Implemented  
- **Summary:** Added a “Tool call results visualization” expander in the Streamlit UI. It now shows the `area_organiser` intermediate output (“daily slots”) plus the raw outputs from `budget_estimator` and `transport_adviser` (as structured JSON), improving explainability for reviewers.

### Medium #7 — Implement conversation export in various formats (PDF, CSV, JSON)

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Medium #8 — Connect to tools from a publicly available remote MCP server

- **Status:** Not implemented  
- **Summary (planned):** TBD  

---

## Hard

*(Not implemented yet — we will document tasks here as we complete them.)*

### Hard #1 — Deploy to cloud with proper scaling

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #2 — Implement advanced indexing (e.g., RAPTOR, ColBERT)

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #3 — Implement A/B testing for different RAG strategies

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #4 — Add automated knowledge base updates

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #5 — Fine-tune the model for your specific domain

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #6 — Add multi-language support

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #7 — Implement advanced analytics dashboard

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #8 — Implement your tools (functions) as MCP servers

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Hard #9 — Implement an evaluation of your RAG system, using RAGAs or otherwise

- **Status:** Not implemented  
- **Summary (planned):** TBD  

