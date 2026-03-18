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
    context = result.get("context") or {}

    # Profile summary
    with st.expander("Trip profile (how we understood your request)", expanded=False):
        st.json(profile)

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
