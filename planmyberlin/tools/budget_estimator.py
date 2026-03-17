"""Budget estimator: per-day and total cost estimates from itinerary."""

from __future__ import annotations

from typing import Any, Dict, List

# Rough EUR estimates per price level (food)
PRICE_LEVEL_EUR = {"$": 10, "$$": 20, "$$$": 40}

# Optional: activity cost per segment (sights often free; museums could be ~10)
DEFAULT_ACTIVITY_EUR = 5


def estimate_budget(
    profile: Dict[str, Any],
    itinerary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Estimate daily and total costs from the itinerary.
    Returns per_day list and total, with a simple 'within_budget' flag.
    """
    daily_budget_food = profile.get("daily_budget_food_eur")
    budget_level = profile.get("budget_level") or "medium"

    per_day: List[Dict[str, Any]] = []
    total_food = 0.0
    total_activities = 0.0

    for day_data in itinerary.get("days") or []:
        day_num = day_data.get("day", 0)
        day_food = 0.0
        day_activities = 0.0
        for seg in day_data.get("segments") or []:
            if seg.get("activity_type") == "restaurant":
                pl = seg.get("price_level") or "$$"
                day_food += PRICE_LEVEL_EUR.get(pl, 20)
            else:
                day_activities += DEFAULT_ACTIVITY_EUR
        total_food += day_food
        total_activities += day_activities
        per_day.append({
            "day": day_num,
            "food_eur": round(day_food, 1),
            "activities_eur": round(day_activities, 1),
            "total_eur": round(day_food + day_activities, 1),
        })

    total = total_food + total_activities
    within_budget = True
    if daily_budget_food is not None and total_food > daily_budget_food * (itinerary.get("num_days") or 1):
        within_budget = False

    return {
        "per_day": per_day,
        "total": {
            "food_eur": round(total_food, 1),
            "activities_eur": round(total_activities, 1),
            "total_eur": round(total, 1),
        },
        "within_budget": within_budget,
        "daily_budget_food_eur": daily_budget_food,
    }
