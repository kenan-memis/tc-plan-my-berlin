# PlanMyBerlin – Project Planning and Evaluation

## 1. Project plan

### 1.1 Goal and scope

- **Project name**: PlanMyBerlin  
- **Goal**: Berlin-focused travel and itinerary planning assistant that builds realistic day-by-day plans tailored to interests, budget, and time.  
- **Domain**: Travel planning for **Berlin only** (no worldwide travel).  
- **Stack**: Python 3.13.9, uv, Streamlit, LangChain, OpenAI, local vector DB (**Chroma**, persisted under `data/vectorstore/`).  
- **Deadline context**: Project should be feature-complete and ready for STL review **before 23 March** (presentation deadline), leaving buffer to schedule the review.

### 1.2 Mapping Sprint 2 core requirements to PlanMyBerlin

| Requirement area | Sprint 2 requirement | PlanMyBerlin approach |
|------------------|---------------------|------------------------|
| **RAG implementation** | Create a knowledge base, embeddings, chunking, similarity search | Build a Berlin-specific corpus: neighbourhood overviews, attractions, sample itineraries, transport tips, safety notes. Use chunking (by section/attraction) and embeddings in a local vector DB. Implement similarity search over these chunks. |
| **Advanced RAG** | Query translation + structured retrieval | Parse user trip request (dates/days, budget level, interests, travel pace) into a structured “TripProfile”. Use that profile to drive targeted retrieval (e.g. attractions by theme and area, transport info) and to structure the final itinerary. |
| **Tool calling** | ≥3 tools, domain-relevant | Implement LangChain tools for: (1) **Itinerary builder** (builds day-by-day plan from TripProfile + retrieved places), (2) **Budget estimator** (rough daily/total costs by category), (3) **Time & area organiser** (cluster attractions by nearby areas / simple time rules). Potential extra tools later: weather lookup stub, packing checklist generator. |
| **Domain specialisation** | Focused domain & knowledge base | Restrict to Berlin, with curated content for a few key neighbourhoods (e.g. Mitte, Kreuzberg, Neukölln, Prenzlauer Berg, Friedrichshain) and major sights. Prompts explicitly frame the assistant as a **Berlin trip planner** and include safety/realism constraints. |
| **Security** | Domain-relevant security measures | No bookings/payments; no real-time availability claims. Clear disclaimers (“informational only”). Input validation (length, basic prompt-injection checks). Rate limiting per session. Safe handling of API keys with `.env` and never exposing them in UI. |
| **Technical implementation** | LangChain, error handling, logging, validation, rate limiting | Use LangChain for model + tools orchestration and RAG chain. Add try/except around tool and model calls; log errors and key events (at least to console, potentially to a simple log file). Validate inputs (days in range, budget level, interests not empty). Simple per-session call counter for rate limiting. |
| **User interface** | Intuitive UI, show context & tool results, progress indicators | Streamlit app with clear sections: trip preferences form, generated itinerary, budget summary, and “how this was generated” panel (showing key retrieved snippets). Use spinners/progress text for long operations. Display tool outputs (itinerary, budget breakdown) in cards/tables. |

### 1.3 Phases and timeline

Assuming “today” is around mid-March and presentation is due by **23 March**, aim to be review-ready a few days earlier.

| Phase | Focus | Target |
|-------|-------|--------|
| **A. Setup & skeleton** | Confirm project structure, uv/Streamlit boilerplate, `.env.example`, minimal homepage that loads. | Day 1 |
| **B. Data & RAG MVP** | Prepare initial Berlin corpus (markdown/JSON files), implement embedding + vector store, simple similarity search + basic Q&A (no tools yet). | Day 2–3 |
| **C. Trip profile & query translation** | Design `TripProfile` schema (days, interests, budget, pace). Implement logic (or an LLM helper) that converts a natural-language request into this structured profile. | Day 3–4 |
| **D. Tools implementation** | Implement at least three tools: itinerary builder, budget estimator, area/time organiser. Integrate them via LangChain tool calling. | Day 4–6 |
| **E. Streamlit UI v1** | Build the main Streamlit page: form for trip preferences, button to run the chain, display of itinerary + budget + key sources. | Day 6–7 |
| **F. Robustness & security** | Add input validation, basic rate limiting, friendly error messages, and domain-specific safety disclaimers. | Day 7–8 |
| **G. Documentation & evaluation** | Fill “Understanding core concepts”, “Technical implementation”, and “Reflection” sections in this document and related docs. | Day 8–9 |
| **H. Optional tasks & polish** | Take on 2 medium + 1 hard optional task (e.g. multi-model support, token cost display, simple deployment). | Day 9–11 (adjust as needed) |

This timeline is a guide; actual dates can be updated as you progress.

### 1.4 Implementation strategy

- **Strategy:** Deliver a small but complete vertical slice early (Berlin corpus + RAG Q&A + minimal UI), then layer on query translation, tools, and UI polish.  
- **MVP:** Single-page Streamlit app where the user enters trip preferences, clicks a button, and gets a day-by-day itinerary plus a rough budget for a fixed number of days.  
- **Then:** Add more flexible profiles (different day counts, interests), better explanations, and optional features once the core flow is solid.

---

## 2. Understanding core concepts (for presentation)

Use this section to collect short, clear explanations you can use during your STL review.

### 2.1 How RAG works in PlanMyBerlin

- High-level explanation of embeddings, vector search, and how we retrieve Berlin content before generating an answer.  
- How query translation to `TripProfile` improves retrieval quality compared to naive keyword search.

### 2.2 Tool calling in this project

- What tools are implemented, what inputs/outputs they have, and when they are triggered.  
- Why we use tools instead of “just prompts” for itinerary structure and budget calculations.

### 2.3 Prompt engineering for a Berlin travel assistant

- How system prompts define the assistant’s role, tone, and safety constraints.  
- How we structure prompts to combine retrieved context, trip profile, and tool results.

### 2.4 User, system, and tool roles in LangChain

- How messages and tool calls flow through the LangChain chain in this app.

*(You will fill these subsections with concrete explanations once the implementation is in place.)*

---

## 3. Technical implementation (to be filled as you build)

Describe how PlanMyBerlin meets the Sprint 2 technical requirements.

- **3.1 Architecture overview** – main modules (RAG, tools, UI) and how they interact.  
- **3.2 RAG pipeline details** – data format, chunking strategy, embedding model, vector DB choice, retrieval settings.  
- **3.3 Tool implementation** – specifics of itinerary, budget, and organiser tools.  
- **3.4 Streamlit UI** – layout, components used, how results and context are shown.  
- **3.5 Security and reliability** – validation, rate limiting, error handling, logging.

---

## 4. Reflection and improvement

Use this section later to prepare for questions like:

- Why you chose this RAG design and these tools.  
- What limitations PlanMyBerlin has (data freshness, coverage, assumptions).  
- What you would improve next if you had more time (data, UI, evaluation, deployment, etc.).

