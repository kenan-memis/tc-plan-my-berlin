"""Itinerary builder: turn daily slots into a day-by-day plan with time segments."""

from __future__ import annotations

from typing import Any, Dict, List


def _pick_restaurant(
    restaurants: List[Dict[str, Any]],
    meal: str,
    food_style: str | None,
    budget_level: str,
) -> Dict[str, Any] | None:
    """Choose one restaurant for a meal; respect food_style and budget."""
    if not restaurants:
        return None
    if meal == "lunch":
        if food_style == "cheap_lunch_nicer_dinner":
            for r in restaurants:
                if r.get("price_level") == "$":
                    return r
        elif budget_level == "low":
            for r in restaurants:
                if r.get("price_level") == "$":
                    return r
        return restaurants[0]
    if meal == "dinner":
        if food_style == "cheap_lunch_nicer_dinner":
            for r in restaurants:
                if r.get("price_level") in ("$$", "$$$"):
                    return r
        elif budget_level == "low":
            for r in restaurants:
                if r.get("price_level") == "$":
                    return r
        return restaurants[0] if restaurants else None
    return restaurants[0] if restaurants else None


def build_itinerary(
    profile: Dict[str, Any],
    slots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a day-by-day itinerary from daily slots.
    Each day has segments: morning (sight), lunch, afternoon (sight), dinner.
    """
    food_style = profile.get("food_style")
    budget_level = profile.get("budget_level") or "medium"
    pace = profile.get("pace") or "balanced"

    n_sights_per_day = 3 if pace == "packed" else 2
    days_out: List[Dict[str, Any]] = []

    for slot in slots:
        day_num = slot["day"]
        sights = list(slot.get("sights") or [])
        restaurants = list(slot.get("restaurants") or [])
        districts = slot.get("districts") or ["Berlin"]

        segments: List[Dict[str, Any]] = []

        # Morning: sight
        if sights:
            segments.append({
                "time_of_day": "morning",
                "activity_type": "sight",
                "name": sights[0].get("name", "Sight"),
                "neighbourhood": sights[0].get("neighbourhood", ""),
                "notes": sights[0].get("content_snippet", "")[:200],
            })
            sights = sights[1:]

        # Lunch
        lunch = _pick_restaurant(restaurants, "lunch", food_style, budget_level)
        if lunch:
            segments.append({
                "time_of_day": "lunch",
                "activity_type": "restaurant",
                "name": lunch.get("name", "Restaurant"),
                "neighbourhood": lunch.get("neighbourhood", ""),
                "price_level": lunch.get("price_level", "$$"),
                "notes": "Lunch",
            })
            restaurants = [r for r in restaurants if r.get("name") != lunch.get("name")]

        # Afternoon: sight(s)
        for _ in range(n_sights_per_day - 1):
            if not sights:
                break
            s = sights.pop(0)
            segments.append({
                "time_of_day": "afternoon",
                "activity_type": "sight",
                "name": s.get("name", "Sight"),
                "neighbourhood": s.get("neighbourhood", ""),
                "notes": (s.get("content_snippet") or "")[:200],
            })

        # Dinner
        dinner = _pick_restaurant(restaurants, "dinner", food_style, budget_level)
        if dinner:
            segments.append({
                "time_of_day": "dinner",
                "activity_type": "restaurant",
                "name": dinner.get("name", "Restaurant"),
                "neighbourhood": dinner.get("neighbourhood", ""),
                "price_level": dinner.get("price_level", "$$"),
                "notes": "Dinner",
            })

        days_out.append({
            "day": day_num,
            "focus_areas": districts,
            "segments": segments,
        })

    return {
        "days": days_out,
        "num_days": len(days_out),
    }
