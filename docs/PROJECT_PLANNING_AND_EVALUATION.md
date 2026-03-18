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

### 1.5 RAG knowledge base: data scope and sources

**In-scope for the corpus (saved as files under `data/raw/`, then embedded):**

| Content type | Scope | Rationale |
|--------------|--------|-----------|
| **Restaurants** | Curated list of Berlin restaurants (by area, cuisine, budget tier). | JTL suggestion; easy to source and chunk; directly supports “where to eat” in itineraries. |
| **Popular places / sights** | Must-see attractions, museums, neighbourhood highlights (e.g. Mitte, Kreuzberg, Prenzlauer Berg, Friedrichshain). | Core of “what to do”; pairs well with itinerary and budget tools. |
| **Transport (high-level only)** | Overview of Berlin transport: zones (A/B/C), main ticket types (e.g. day ticket, WelcomeCard), key U‑Bahn/S‑Bahn lines and how they connect areas. **No** real-time schedules or live APIs. | Keeps itineraries realistic (how to get between areas) without the complexity of live/GTFS data. |

**Data approach:**

- **Geographic scope (initial):** Focus on a **small set of key districts** first (e.g. Mitte, Kreuzberg, Prenzlauer Berg, Friedrichshain), then extend to more of Berlin if time allows.
- **Source:** Curated, static content (e.g. from official tourism sites, Wikipedia, or trusted guides). Fetched or copied once, then saved as **markdown** in `data/raw/`.
- **Storage:** Files in `data/raw/`; no database or external API at query time.
- **Pipeline:** Ingest → chunk (by section/place/theme) → embed → store in Chroma under `data/vectorstore/`. Retrieval runs only over this static index.

**Out of scope for now:** Real-time transport (live departures, route planning APIs), bookings, payments, or dynamic pricing.

---

## 2. Understanding core concepts (for presentation)

Use this section to collect short, clear explanations you can use during your STL review.

### 2.1 How RAG works in PlanMyBerlin

- **Embeddings + vector search:** We store Berlin knowledge as markdown files under `data/raw/`. During ingestion, documents are chunked and converted into embeddings (vector representations). At query time, the user’s request is embedded and we retrieve the most similar chunks from **Chroma** (`data/vectorstore/`). Those retrieved chunks become the “grounding context” for planning.
- **Why this improves quality:** Instead of relying on the model’s general knowledge, the assistant uses our curated Berlin corpus (districts, sights, restaurants, transport overview). This makes responses more consistent and aligned with our chosen scope.
- **Advanced RAG (query translation):** We translate the free-text user request into a structured `TripProfile` (days, budget, districts, pace, food style). That profile is used to shape retrieval queries (e.g. budget-friendly restaurants in chosen districts) and to drive the planning logic.

### 2.2 Tool calling in this project

- **Tools implemented (domain-relevant):**
  - **Area/time organiser**: assigns day-by-day focus areas (districts) and selects candidate sights/restaurants for each day.
  - **Itinerary builder**: creates a structured day plan (morning/lunch/afternoon/dinner) and respects “cheap lunch + nicer dinner”.
  - **Budget estimator**: estimates daily and total costs using price-level heuristics.
  - **Transport adviser (static):** generates “getting around” guidance from the transport overview (zones/tickets/hubs) and user constraints (e.g. “metro only”), without real-time routing.
- **Why tools instead of prompts:** These steps are deterministic or rule-based and produce structured outputs (itinerary JSON, cost totals). Tools reduce hallucinations, make outputs predictable, and simplify UI rendering.

### 2.3 Prompt engineering for a Berlin travel assistant

- **Role and scope:** Prompts keep the assistant strictly Berlin-focused and “informational only” (no bookings, no live availability).
- **Structured extraction:** We use a strict JSON schema to extract `TripProfile` from free-text. This is safer and easier to validate than free-form parsing.
- **Grounding:** We keep planning grounded in retrieved Berlin snippets and our tool outputs (itinerary + budget).

### 2.4 User, system, and tool roles in LangChain

- **User → profile:** User provides one free-text request in Streamlit. The model converts it into a structured `TripProfile`.
- **Profile → retrieval:** The profile shapes which Berlin snippets are retrieved from Chroma.
- **Retrieval → tools:** Candidate sights/restaurants are fed into planning tools that generate the itinerary and budget.
- **Tools → UI:** Streamlit renders the structured itinerary, budget totals, and a transport guidance section.

This flow is easy to demonstrate in review: you can show the profile JSON, then the resulting itinerary and budget.

---

## 3. Technical implementation (to be filled as you build)

Describe how PlanMyBerlin meets the Sprint 2 technical requirements.

### 3.1 Architecture overview

- **Data**: `data/raw/*.md` (Berlin corpus) and `data/vectorstore/` (Chroma persisted embeddings).
- **RAG**: `planmyberlin/rag/`:
  - `ingest.py` builds the vector store.
  - `trip_profile.py` parses user requests into structured profiles.
  - `planning.py` retrieves candidate sights/restaurants guided by the profile.
- **Tools**: `planmyberlin/tools/`:
  - `area_organiser.py`, `itinerary_builder.py`, `budget_estimator.py`, `transport_adviser.py`
  - `pipeline.py` orchestrates the end-to-end flow.
- **UI**: `planmyberlin/ui/app.py` Streamlit app (input → generate → render results).

### 3.2 RAG pipeline details

- **Data format**: markdown with `## District` and `### Place/Restaurant` sections.
- **Chunking**: `RecursiveCharacterTextSplitter` with ~800 char chunks and overlap.
- **Embeddings**: OpenAI embeddings via `OpenAIEmbeddings()`.
- **Vector DB**: Chroma persisted under `data/vectorstore/`.
- **Retrieval**:
  - Profile-shaped search queries.
  - Top-k retrieval (e.g. 12 docs for sights and 12 for restaurants in the planning stage).

### 3.3 Tool implementation (minimum three)

- **Area/time organiser**: chooses districts per day based on `pace` and district preferences.
- **Itinerary builder**: creates daily segments and applies meal cost preferences (cheap lunch / nicer dinner).
- **Budget estimator**: applies price-level heuristics (`$`, `$$`, `$$$`) and provides totals + per-day breakdown.
- **Transport adviser**: provides zones/tickets/hubs guidance and notes about user transport constraints (static only).

### 3.4 Streamlit UI

- One text input for the trip request.
- “Generate plan” button with progress spinner.
- Results sections:
  - Trip profile (JSON)
  - Itinerary (day-by-day)
  - Budget estimate (total + per-day)
  - Getting around (transport guidance)
  - Source counts (how many snippets were used)

### 3.5 Security and reliability

- **Input validation**: max input length; blocks empty inputs; basic prompt-injection phrase checks.
- **Rate limiting**: per-session request limit in Streamlit session state.
- **Disclaimers**: informational-only; no real-time availability/booking/live routing; rough budget estimates.
- **Error handling**: try/except around pipeline call; user-friendly error message; logs exception for debugging.

---

## 4. Reflection and improvement

Use this section later to prepare for questions like:

### 4.1 Why this design

- **Berlin-only scope** keeps the knowledge base deep and reviewable within sprint time.
- **Query translation (`TripProfile`)** makes planning more structured and reduces ambiguity.
- **Tools** provide deterministic structure for itineraries and budgets, improving consistency and explainability.

### 4.2 Limitations

- **Static corpus**: data may be incomplete or outdated (opening hours, prices, closures).
- **No real-time routing**: transport guidance is high-level; no step-by-step directions.
- **Heuristic budget**: price-level mapping is approximate, not a real quote.
- **Small dataset**: only a subset of Berlin districts and venues.

### 4.3 Improvements if time allows

- Add per-item **source citations** (show which snippet supported each suggestion).
- Add conversation history and export (JSON/PDF).
- Add token/cost display per request.
- Add simple evaluation (golden questions + expected sources) or RAGAs later.

