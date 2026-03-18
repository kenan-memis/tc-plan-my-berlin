"""Full planning pipeline: user text -> profile + RAG context + itinerary + budget."""

from __future__ import annotations

import json as _json
import sys
from typing import Any, Dict, Optional
from langchain_community.callbacks import get_openai_callback

from ..rag.planning import plan_from_request
from .area_organiser import build_daily_slots
from .itinerary_builder import build_itinerary
from .budget_estimator import estimate_budget
from .transport_adviser import build_transport_guidance


def plan_itinerary_from_request(
    user_text: str,
    *,
    trip_profile_provider: str = "openai",
    trip_profile_model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    End-to-end: parse request -> retrieve context -> build slots -> itinerary -> budget.
    Returns a single dict with profile, itinerary, budget, and raw context (sights/restaurants).
    """
    token_usage: Dict[str, Any] = {}

    with get_openai_callback() as cb:
        context = plan_from_request(
            user_text,
            trip_profile_provider=trip_profile_provider,
            trip_profile_model=trip_profile_model,
        )
        profile = context["profile"]
        sights_docs = context["sights"]
        restaurants_docs = context["restaurants"]
        rag_debug = context.get("rag_debug") or {}

        slots = build_daily_slots(profile, sights_docs, restaurants_docs)
        itinerary = build_itinerary(profile, slots)
        budget = estimate_budget(profile, itinerary)
        transport = build_transport_guidance(profile, itinerary)

        # LangChain returns estimated pricing based on OpenAI model pricing.
        token_usage = {
            "prompt_tokens": cb.prompt_tokens,
            "completion_tokens": cb.completion_tokens,
            "total_tokens": cb.total_tokens,
            "total_cost": float(cb.total_cost) if cb.total_cost is not None else None,
            # Keep raw callback attributes that are useful for debugging.
            "model": getattr(cb, "model", None),
        }

    return {
        "profile": profile,
        "itinerary": itinerary,
        "slots": slots,
        "budget": budget,
        "transport": transport,
        "token_usage": token_usage,
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
