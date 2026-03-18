from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, List

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from .trip_profile import TripProfile, parse_trip_request


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"


def _get_vectorstore() -> Chroma:
    embeddings = OpenAIEmbeddings()
    return Chroma(
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )


def build_plan_context(profile: TripProfile) -> Dict[str, Any]:
    """
    Use the TripProfile to retrieve candidate places and restaurants.

    This does not yet build a full itinerary; it prepares structured inputs
    that the itinerary and budget tools will use in the next phase.
    """
    vs = _get_vectorstore()

    # Build high-level queries based on interests, districts, and food style.
    interests_text = ", ".join(profile.interests) or "general sightseeing"
    districts_text = ", ".join(profile.district_preferences) or "central Berlin"

    sights_query = (
        f"Sights and neighbourhood highlights in {districts_text} for someone "
        f"interested in {interests_text}."
    )
    restaurants_query = (
        f"Restaurants in {districts_text} that fit a {profile.budget_level} budget."
    )

    # Retrieve docs and similarity scores (if available from the vector store).
    # Chroma typically returns a distance-like value where *lower* means "more similar".
    try:
        sights_results = vs.similarity_search_with_score(sights_query, k=12)
        restaurants_results = vs.similarity_search_with_score(restaurants_query, k=12)
        sights_docs = [d for d, _score in sights_results]
        restaurants_docs = [d for d, _score in restaurants_results]
        sights_scores = [float(_score) for _doc, _score in sights_results]
        restaurants_scores = [float(_score) for _doc, _score in restaurants_results]
    except Exception:
        sights_docs = vs.similarity_search(sights_query, k=12)
        restaurants_docs = vs.similarity_search(restaurants_query, k=12)
        sights_scores = []
        restaurants_scores = []

    def _preview(text: str, limit: int = 260) -> str:
        t = (text or "").strip()
        if len(t) <= limit:
            return t
        return t[: limit - 3] + "..."

    rag_debug = {
        "sights_query": sights_query,
        "restaurants_query": restaurants_query,
        "top_sights_previews": [_preview(d.page_content) for d in (sights_docs[:5] or [])],
        "top_restaurants_previews": [
            _preview(d.page_content) for d in (restaurants_docs[:5] or [])
        ],
        "top_sights_scores": sights_scores[:5] if sights_scores else [],
        "top_restaurants_scores": restaurants_scores[:5] if restaurants_scores else [],
    }

    def _docs_to_dicts(docs: List[Any]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for d in docs:
            items.append(
                {
                    "content": d.page_content,
                    "metadata": getattr(d, "metadata", {}),
                }
            )
        return items

    return {
        "profile": asdict(profile),
        "sights": _docs_to_dicts(sights_docs),
        "restaurants": _docs_to_dicts(restaurants_docs),
        "rag_debug": rag_debug,
    }


def plan_from_request(user_text: str) -> Dict[str, Any]:
    """
    High-level entry point for later phases:
    - parse user request into a TripProfile
    - retrieve candidate sights and restaurants guided by that profile
    """
    profile = parse_trip_request(user_text)
    context = build_plan_context(profile)
    return context


if __name__ == "__main__":
    import sys
    import json as _json

    if len(sys.argv) < 2:
        print("Usage: uv run python -m planmyberlin.rag.planning \"Your trip request here\"")
        raise SystemExit(1)

    text = " ".join(sys.argv[1:])
    result = plan_from_request(text)
    print(_json.dumps(result, indent=2, ensure_ascii=False))

