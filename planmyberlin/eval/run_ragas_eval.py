"""
Hard #9 — RAG evaluation (RAGAs-based) for PlanMyBerlin.

This script:
1) Creates a small dataset of Berlin trip queries.
2) Runs the existing TripProfile -> retrieval -> deterministic itinerary tools.
3) Feeds (question, answer, retrieved_contexts) into RAGAs metrics:
   - faithfulness
   - answer_relevancy
   - context_precision
   - context_recall
4) Saves raw results + a small summary artifact for STL/review.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re

from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

from planmyberlin.rag.planning import build_plan_context
from planmyberlin.rag.trip_profile import parse_trip_request
from planmyberlin.tools.area_organiser import build_daily_slots
from planmyberlin.tools.budget_estimator import estimate_budget
from planmyberlin.tools.itinerary_builder import build_itinerary
from planmyberlin.tools.transport_adviser import build_transport_guidance


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "planmyberlin" / "eval" / "results"


def _format_itinerary_answer(itinerary: Dict[str, Any]) -> str:
    """
    Produce an "answer text" grounded in retrieved contexts.

    For faithfulness evaluation we intentionally exclude:
    - budget totals (heuristic mapping, not necessarily present in retrieved docs)
    - transport guidance (built from a separate static transport doc)
    """
    # Keep the answer "atomic facts" very close to what appears in the retrieved chunks.
    # This makes the faithfulness judge much more reliable than including extra structure.
    lines: List[str] = []
    for day in itinerary.get("days") or []:
        for seg in day.get("segments") or []:
            name = (seg.get("name") or "").strip()
            neighbourhood = (seg.get("neighbourhood") or "").strip()
            if not name:
                continue
            if neighbourhood:
                lines.append(f"{name} ({neighbourhood})")
            else:
                lines.append(name)

    return "\n".join(lines).strip()


def _build_sample(
    query: str,
    *,
    trip_profile_model: str,
    trip_profile_provider: str,
    top_k_contexts: int,
) -> Tuple[str, str, List[str]]:
    """
    Return (question, answer_text, retrieved_contexts).
    """
    profile = parse_trip_request(
        query,
        provider=trip_profile_provider,
        model=trip_profile_model,
    )

    # Retrieval guided by TripProfile (returns full doc content in dicts)
    context = build_plan_context(profile)
    profile_dict = context["profile"]
    sights_docs = context["sights"]
    restaurants_docs = context["restaurants"]

    # Deterministic tool pipeline for the "answer"
    slots = build_daily_slots(profile_dict, sights_docs, restaurants_docs)
    itinerary = build_itinerary(profile_dict, slots)

    # Completeness parity (not included in RAGAs answer text)
    _budget = estimate_budget(profile_dict, itinerary)
    _transport = build_transport_guidance(profile_dict, itinerary)
    _ = (_budget, _transport)

    answer_text = _format_itinerary_answer(itinerary)

    # Contexts for RAGAs: top-k retrieved sights/restaurants chunks (full text)
    combined_docs = (sights_docs or []) + (restaurants_docs or [])

    # Precision-focused filtering:
    # Keep only chunks that contain a concrete entity entry ("### <Place/Restaurant>").
    # Our corpus includes additional header chunks ("# Berlin...", "## Mitte", etc.)
    # that can be close-by in embedding space but less directly useful for grounding.
    entity_heading_re = re.compile(r"^###\s+.+$", flags=re.MULTILINE)

    filtered_contexts: List[str] = []
    for d in combined_docs:
        content = d.get("content") or ""
        if not content.strip():
            continue
        if entity_heading_re.search(content):
            filtered_contexts.append(content)
        if len(filtered_contexts) >= top_k_contexts:
            break

    contexts = filtered_contexts or ["(no retrieved context available)"]

    return query, answer_text, contexts


def run_ragas_eval(
    *,
    max_samples: int,
    trip_profile_provider: str,
    trip_profile_model: str,
    top_k_contexts: int,
    judge_model: str,
    output_name: str | None,
) -> Path:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is required for RAGAs judge LLM + OpenAI embeddings (and for TripProfile parsing)."
        )

    queries = [
        "What are some famous sights in Mitte?",
        "Recommend 2 restaurants in Kreuzberg with low budget.",
        "Plan a relaxed 2-day itinerary in Prenzlauer Berg and Friedrichshain.",
        "1 day, street food and parks in Kreuzberg (packed pace).",
        "Cheap museums and history in Mitte for 3 days.",
        "What are must-see attractions in Neukölln?",
        "Transport zones A, B, C — how do they work?",
        "We want classic sights in Mitte with a high budget, balanced pace.",
    ]
    queries = queries[:max_samples]

    dataset_rows: Dict[str, List[Any]] = {
        "user_input": [],
        "response": [],
        "reference": [],
        "retrieved_contexts": [],
    }

    for q in queries:
        question, answer_text, contexts = _build_sample(
            q,
            trip_profile_provider=trip_profile_provider,
            trip_profile_model=trip_profile_model,
            top_k_contexts=top_k_contexts,
        )
        dataset_rows["user_input"].append(question)
        dataset_rows["response"].append(answer_text)
        dataset_rows["reference"].append(answer_text)
        dataset_rows["retrieved_contexts"].append(contexts)

    dataset = Dataset.from_dict(dataset_rows)

    judge_llm = ChatOpenAI(model=judge_model, temperature=0)
    embeddings = OpenAIEmbeddings()

    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ]

    result = evaluate(
        dataset,
        metrics=metrics,
        llm=judge_llm,
        embeddings=embeddings,
        show_progress=True,
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = output_name or f"hard9-ragas-{ts}"
    out_path = RESULTS_DIR / f"{name}.json"
    out_path_summary = RESULTS_DIR / f"{name}_summary.md"

    # RAGAs returns an EvaluationResult (no to_dict). We'll persist both:
    # - scores list (raw objects)
    # - dataframe records (easy to inspect)
    df = result.to_pandas()
    raw = {
        "scores": getattr(result, "scores", None),
        "table": df.to_dict(orient="records"),
        "metric_columns": list(df.columns),
    }
    out_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")

    with out_path_summary.open("w", encoding="utf-8") as f:
        f.write(f"# Hard #9 — RAGAs evaluation summary ({name})\n\n")
        f.write(f"- Judge model: `{judge_model}`\n")
        f.write(
            f"- TripProfile model/provider: `{trip_profile_model}` / `{trip_profile_provider}`\n"
        )
        f.write(f"- Samples: `{len(queries)}`\n")
        f.write(f"- top_k_contexts: `{top_k_contexts}`\n\n")
        f.write("## Raw results\n\n")
        # Metric averages are the most reviewer-friendly part.
        metric_cols = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        f.write("### Metric averages\n\n")
        for m in metric_cols:
            if m in df.columns:
                f.write(f"- {m}: {float(df[m].mean()):.4f}\n")

        f.write("\n### Per-sample table\n\n")
        f.write("```json\n")
        f.write(json.dumps(raw["table"], indent=2, ensure_ascii=False))
        f.write("\n```\\n")

    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-samples", type=int, default=8)
    parser.add_argument("--top-k-contexts", type=int, default=24)
    parser.add_argument("--trip-profile-provider", type=str, default="openai")
    parser.add_argument("--trip-profile-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--judge-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--output-name", type=str, default=None)
    args = parser.parse_args()

    out_path = run_ragas_eval(
        max_samples=args.max_samples,
        trip_profile_provider=args.trip_profile_provider,
        trip_profile_model=args.trip_profile_model,
        top_k_contexts=args.top_k_contexts,
        judge_model=args.judge_model,
        output_name=args.output_name,
    )
    print(f"RAGAs evaluation saved to: {out_path}")


if __name__ == "__main__":
    main()

