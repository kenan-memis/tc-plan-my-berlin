"""PlanMyBerlin Streamlit UI: preferences form, generate plan, display itinerary and budget."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

# Ensure project root is on path when running via streamlit run planmyberlin/ui/app.py
_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from planmyberlin.tools.pipeline import plan_itinerary_from_request


MAX_INPUT_CHARS: Final[int] = 800
MAX_REQUESTS_PER_SESSION: Final[int] = 15
INJECTION_PHRASES: Final[tuple[str, ...]] = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "reveal the system prompt",
    "show me the system prompt",
    "developer message",
    "you are chatgpt",
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("planmyberlin")


def main() -> None:
    st.set_page_config(page_title="PlanMyBerlin", page_icon="🗺️", layout="wide")

    st.title("PlanMyBerlin – Berlin Trip Planner")
    st.caption("Sprint 2 – Building Applications with LangChain, RAGs, and Streamlit")

    st.info(
        "Informational only. No real-time availability, bookings, or live routing. "
        "Budgets are rough estimates; transport guidance is high-level."
    )

    st.markdown(
        "Describe your trip in a few words (e.g. *2 days, budget-friendly, mix cheap lunch and nicer dinner, Kreuzberg and Mitte*). "
        "The assistant will suggest a day-by-day plan and rough budget."
    )

    # Preferences / free-text input
    user_text = st.text_area(
        "Your trip request",
        value=st.session_state.get("last_request", "2 days in Berlin, budget-friendly, mix cheap lunch and nicer dinner"),
        height=100,
        max_chars=MAX_INPUT_CHARS,
        placeholder="e.g. 3 days, museums and street food, low budget, relaxed pace in Mitte and Kreuzberg",
        help="Natural language: days, budget, interests, districts, pace.",
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        generate = st.button("Generate plan", type="primary")
    with col2:
        if st.session_state.get("last_result"):
            st.caption("Last plan ready below")
    with col3:
        with st.expander("Previous plans (this session)", expanded=False):
            history = st.session_state.get("history", [])
            if not history:
                st.caption("No previous plans yet.")
            else:
                labels = [f"{i+1}. {item['request'][:60]}..." for i, item in enumerate(history)]
                idx = st.selectbox("Select a plan to view again", range(len(history)), format_func=lambda i: labels[i])
                if st.button("Load selected plan"):
                    st.session_state["last_result"] = history[idx]["result"]
                    st.session_state["last_request"] = history[idx]["request"]
                    st.success("Loaded plan from history. Scroll down to view.")

    if generate:
        text = (user_text or "").strip()
        if not text:
            st.error("Please enter a short trip description.")
            st.stop()

        # Rate limit per Streamlit session (simple cost guard)
        st.session_state["request_count"] = int(st.session_state.get("request_count", 0)) + 1
        if st.session_state["request_count"] > MAX_REQUESTS_PER_SESSION:
            st.error(
                f"Rate limit reached: max {MAX_REQUESTS_PER_SESSION} requests per session. "
                "Refresh the page to start a new session."
            )
            st.stop()

        # Very basic prompt-injection guard (best-effort)
        lowered = text.lower()
        if any(phrase in lowered for phrase in INJECTION_PHRASES):
            st.error("Request blocked: please rephrase without trying to override system instructions.")
            st.stop()

        st.session_state["last_request"] = text
        with st.spinner("Building your plan (parsing request, retrieving places, building itinerary)…"):
            try:
                result = plan_itinerary_from_request(text)
                st.session_state["last_result"] = result
                history = st.session_state.get("history", [])
                history.append({"request": text, "result": result})
                st.session_state["history"] = history[-10:]  # keep last 10
            except Exception as e:
                logger.exception("Failed to build plan")
                st.error(f"Something went wrong: {e}")
                if st.session_state.get("last_result") is not None:
                    del st.session_state["last_result"]
                st.stop()
        st.success("Plan ready.")

    result = st.session_state.get("last_result")
    if not result:
        st.info("Enter your trip request above and click **Generate plan** to see an itinerary and budget.")
        return

    profile = result.get("profile") or {}
    itinerary = result.get("itinerary") or {}
    budget = result.get("budget") or {}
    transport = result.get("transport") or {}
    rag_debug = result.get("rag_debug") or {}
    context = result.get("context") or {}

    # Profile summary
    with st.expander("Trip profile (how we understood your request)", expanded=False):
        st.json(profile)

    # RAG debug (Easy #2)
    with st.expander("RAG retrieval debug (how we chose candidates)", expanded=False):
        if not rag_debug:
            st.warning(
                "RAG debug info is missing from this generated plan. "
                "If you recently updated the backend, please restart Streamlit (stop + re-run) "
                "to ensure the latest code is loaded."
            )
            st.stop()

        st.markdown("**Sights retrieval query**")
        if rag_debug.get("sights_query"):
            st.code(rag_debug["sights_query"])

        if rag_debug.get("top_sights_previews"):
            scores = rag_debug.get("top_sights_scores") or []
            st.markdown("**Top retrieved sights snippets**")
            for i, preview in enumerate(rag_debug["top_sights_previews"][:5]):
                score = scores[i] if i < len(scores) else None
                st.markdown(f"{i+1}.")
                if preview:
                    if score is not None:
                        st.caption(f"Similarity score (Chroma distance): {score:.4f}")
                    st.code(preview)

        st.divider()

        st.markdown("**Restaurants retrieval query**")
        if rag_debug.get("restaurants_query"):
            st.code(rag_debug["restaurants_query"])

        if rag_debug.get("top_restaurants_previews"):
            scores = rag_debug.get("top_restaurants_scores") or []
            st.markdown("**Top retrieved restaurant snippets**")
            for i, preview in enumerate(rag_debug["top_restaurants_previews"][:5]):
                score = scores[i] if i < len(scores) else None
                st.markdown(f"{i+1}.")
                if preview:
                    if score is not None:
                        st.caption(f"Similarity score (Chroma distance): {score:.4f}")
                    st.code(preview)

    # Itinerary by day
    st.subheader("Your itinerary")
    days = itinerary.get("days") or []
    for day_data in days:
        day_num = day_data.get("day", 0)
        focus = day_data.get("focus_areas") or []
        segments = day_data.get("segments") or []
        st.markdown(f"**Day {day_num}** — {', '.join(focus) or 'Berlin'}")
        for seg in segments:
            time_of_day = seg.get("time_of_day", "")
            activity_type = seg.get("activity_type", "")
            name = seg.get("name", "")
            neighbourhood = seg.get("neighbourhood", "")
            price = seg.get("price_level", "")
            label = f"{time_of_day.capitalize()}: **{name}**"
            if neighbourhood:
                label += f" ({neighbourhood})"
            if price and activity_type == "restaurant":
                label += f" — {price}"
            st.markdown(f"- {label}")
        st.divider()

    # Budget
    st.subheader("Budget estimate")
    total = budget.get("total") or {}
    per_day = budget.get("per_day") or []
    within = budget.get("within_budget", True)
    st.metric("Total (food + activities)", f"€{total.get('total_eur', 0):.1f}")
    st.caption(f"Food: €{total.get('food_eur', 0):.1f}  ·  Activities (approx.): €{total.get('activities_eur', 0):.1f}")
    if budget.get("daily_budget_food_eur") is not None:
        st.caption(f"Daily food budget you asked for: €{budget['daily_budget_food_eur']:.0f}")
    if not within:
        st.warning("Estimated food cost is above your stated daily budget.")
    if per_day:
        st.markdown("**Per day**")
        for row in per_day:
            st.markdown(f"- Day {row.get('day', 0)}: €{row.get('total_eur', 0):.1f} (food €{row.get('food_eur', 0):.1f}, activities €{row.get('activities_eur', 0):.1f})")

    # Export current plan
    import json as _json
    import base64 as _base64

    st.subheader("Export this plan")
    plan_str_json = _json.dumps(
        {
            "profile": profile,
            "itinerary": itinerary,
            "budget": budget,
            "transport": transport,
        },
        indent=2,
        ensure_ascii=False,
    )

    # Simple text export
    lines = ["PlanMyBerlin – Trip Plan", ""]
    for day_data in days:
        day_num = day_data.get("day", 0)
        focus = ", ".join(day_data.get("focus_areas") or []) or "Berlin"
        lines.append(f"Day {day_num} — {focus}")
        for seg in day_data.get("segments") or []:
            time_of_day = seg.get("time_of_day", "").capitalize()
            name = seg.get("name", "")
            neighbourhood = seg.get("neighbourhood", "")
            price = seg.get("price_level", "")
            label = f"{time_of_day}: {name}"
            if neighbourhood:
                label += f" ({neighbourhood})"
            if price and seg.get("activity_type") == "restaurant":
                label += f" — {price}"
            lines.append(f"- {label}")
        lines.append("")
    if total:
        lines.append(f"Total estimated cost (food + activities): €{total.get('total_eur', 0):.1f}")
    text_export = "\n".join(lines)

    # Use HTML download links so we can control spacing precisely.
    plan_b64 = _base64.b64encode(plan_str_json.encode("utf-8")).decode("ascii")
    text_b64 = _base64.b64encode(text_export.encode("utf-8")).decode("ascii")
    href_json = f"data:application/json;base64,{plan_b64}"
    href_text = f"data:text/plain;base64,{text_b64}"

    st.markdown(
        f"""
        <div style="display:flex; gap:12px; align-items:center;">
          <a download="planmyberlin_plan.json" href="{href_json}"
             style="background-color:#e5534b; color:white; padding:0.55rem 1rem; border-radius:0.5rem;
                    font-weight:600; text-decoration:none; border:1px solid #e5534b; display:inline-block;">
            Download as JSON
          </a>
          <a download="planmyberlin_plan.txt" href="{href_text}"
             style="background-color:transparent; color:#222; padding:0.55rem 1rem; border-radius:0.5rem;
                    font-weight:600; text-decoration:none; border:1px solid #d0d0d0; display:inline-block;">
            Download as text
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Getting around
    st.subheader("Getting around (transport)")
    transport_summary = (transport.get("summary") or "").strip()
    if transport_summary:
        st.markdown(transport_summary)
    else:
        st.caption("Transport guidance is not available yet.")

    # Sources
    st.caption(
        f"Plan built from {context.get('sights_count', 0)} sight snippets and {context.get('restaurants_count', 0)} restaurant snippets in the Berlin knowledge base."
    )


if __name__ == "__main__":
    main()
