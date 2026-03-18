"""Full planning pipeline: user text -> profile + RAG context + itinerary + budget."""

from __future__ import annotations

import json as _json
import sys
from typing import Any, Dict

from ..rag.planning import plan_from_request
from .area_organiser import build_daily_slots
from .itinerary_builder import build_itinerary
from .budget_estimator import estimate_budget
from .transport_adviser import build_transport_guidance


def plan_itinerary_from_request(user_text: str) -> Dict[str, Any]:
    """
    End-to-end: parse request -> retrieve context -> build slots -> itinerary -> budget.
    Returns a single dict with profile, itinerary, budget, and raw context (sights/restaurants).
    """
    context = plan_from_request(user_text)
    profile = context["profile"]
    sights_docs = context["sights"]
    restaurants_docs = context["restaurants"]
    rag_debug = context.get("rag_debug") or {}

    slots = build_daily_slots(profile, sights_docs, restaurants_docs)
    itinerary = build_itinerary(profile, slots)
    budget = estimate_budget(profile, itinerary)
    transport = build_transport_guidance(profile, itinerary)

    return {
        "profile": profile,
        "itinerary": itinerary,
        "slots": slots,
        "budget": budget,
        "transport": transport,
        "rag_debug": rag_debug,
        "context": {
            "sights_count": len(sights_docs),
            "restaurants_count": len(restaurants_docs),
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python -m planmyberlin.tools.pipeline \"Your trip request\"")
        sys.exit(1)
    text = " ".join(sys.argv[1:])
    result = plan_itinerary_from_request(text)
    print(_json.dumps(result, indent=2, ensure_ascii=False))
