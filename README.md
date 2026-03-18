# PlanMyBerlin

PlanMyBerlin is a Berlin-focused travel and itinerary planning assistant built for Sprint 2 of the Turing College AI course. It helps visitors design realistic day-by-day plans tailored to their interests, budget, and time, using local knowledge about Berlin’s neighbourhoods, attractions, and transport.

---

## What it is for

PlanMyBerlin is designed to:

- Help visitors **plan trips to Berlin** with realistic, structured day-by-day itineraries.
- Tailor suggestions to **interests, budget level, and travel pace** (e.g. “3 days, museums and food, low budget”).
- Show **how the plan was generated** using RAG over a Berlin-specific knowledge base plus tools for itinerary building and rough budget estimation.

---

## How it is built

- **Language:** Python 3.13.9  
- **Environment & deps:** `uv` (no `requirements.txt`, uses `pyproject.toml`)  
- **UI:** Streamlit (single-page app, no separate front end)  
- **LLM:** OpenAI API (initially **GPT-4o mini**; may be extended later)  
- **RAG:** LangChain, embeddings over a Berlin corpus, vector search in **Chroma**  
- **Tools:** LangChain tools for building itineraries, estimating budgets, and organising activities by area/time  

For detailed planning and evaluation notes, see `docs/PROJECT_PLANNING_AND_EVALUATION.md`.

---

## How to run it (local, WIP)

Anyone who wants to try the app locally will need **Python, uv, and an OpenAI API key**.

### 1. Clone the repository

```bash
git clone https://github.com/TuringCollegeSubmissions/kmemis-AE.2.5.git
cd kmemis-AE.2.5
```

*(The repo is named `kmemis-AE.2.5` by Turing College; the project itself is PlanMyBerlin.)*

### 2. Install dependencies with uv

```bash
uv sync
```

This will create and manage a virtual environment under `.venv/` and install all dependencies from `pyproject.toml`.

### 3. Configure your OpenAI API key

From the project root (`kmemis-AE.2.5/`), copy the example env file and add your key:

```bash
cp ../.env.example ../.env    # if shared at sprint_2 root
```

Then edit `.env` and set:

```bash
OPENAI_API_KEY=sk-your-key-here
```

Make sure `.env` is **never committed** (it should be in `.gitignore`).

### 4. Run the app

Start the Streamlit app (trip request form → generate plan → view itinerary and budget):

```bash
uv run streamlit run planmyberlin/ui/app.py
```

---

## Project structure (early)

```text
kmemis-AE.2.5/                        # repo root (clone = this folder)
├── README.md                         # This file – what the app is, how to run
├── AGENTS.md                         # Project rules and conventions
├── docs/
│   └── PROJECT_PLANNING_AND_EVALUATION.md   # Project plan, phases, evaluation notes
├── data/
│   ├── raw/                          # Source documents for Berlin knowledge base
│   └── vectorstore/                  # Persisted Chroma vector DB
├── planmyberlin/
│   ├── rag/                          # RAG pipeline (ingestion, embeddings, retrieval)
│   ├── tools/                        # LangChain tools (itinerary, budget, organiser)
│   └── ui/                           # Streamlit app components
├── main.py                           # Temporary entry point for early testing
├── pyproject.toml                    # Python project + dependency metadata (used by uv)
└── .python-version                   # Python version pin
```

---

## Course context

This project is part of the Turing College AI Engineering course, Sprint 2 (“Building Applications with LangChain, RAGs, and Streamlit”). It is for learning and portfolio purposes.

---

## Optional tasks (progress)

Checklist of Sprint 2 optional tasks. Marked with ✅ when implemented.  
For maximum bonus points, the goal is at least **2 medium** and **1 hard** (or more, depending on time).

### Easy

- ✅ **1. Add conversation history and export functionality** – Per-session plan history in the UI plus per-plan JSON and text exports.
- ✅ **2. Add visualisation of RAG process** – “RAG retrieval debug” expander shows sights/restaurants retrieval queries, top retrieved snippet previews, and per-snippet similarity scores (Chroma distance).

### Medium

- *(None implemented yet.)*

### Hard

- *(None implemented yet.)*

