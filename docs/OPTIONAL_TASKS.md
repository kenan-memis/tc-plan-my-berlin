# Optional tasks — What we implement (PlanMyBerlin)

This document records which optional Sprint 2 tasks we implement for **PlanMyBerlin** and how. We will fill it gradually, **after** each optional task is complete.

---

## Easy

*(Not implemented yet — we will document tasks here as we complete them.)*

### Easy #1 — Add conversation history and export functionality

- **Status:** ✅ Implemented  
- **Summary:** We added a per-session **plan history** and simple export options. Every time the user generates a plan, the app stores `{request, result}` in `st.session_state["history"]` (keeping the last 10 entries). A “Previous plans (this session)” expander lets the user re-load any earlier plan (request + result) without re-running the pipeline. Under the current plan, two **download buttons** allow exporting the itinerary: (1) **JSON** (`profile`, `itinerary`, `budget`, `transport`) and (2) a readable **text** summary (days, segments, and total budget). This satisfies “conversation history and export” without changing the RAG or tools logic.

### Easy #2 — Add visualisation of RAG process

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Easy #3 — Include source citations in responses

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Easy #4 — Add an interactive help feature or chatbot guide

- **Status:** Not implemented  
- **Summary (planned):** TBD  

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

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Medium #4 — Add user authentication and personalisation

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Medium #5 — Calculate and display token usage and costs

- **Status:** Not implemented  
- **Summary (planned):** TBD  

### Medium #6 — Add visualisation of tool call results

- **Status:** Not implemented  
- **Summary (planned):** TBD  

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

