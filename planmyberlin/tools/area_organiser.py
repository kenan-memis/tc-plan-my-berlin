"""Area/time organiser: group candidates by day and district."""

from __future__ import annotations

from typing import Any, Dict, List

from .parsing import parse_restaurants, parse_sights


# Berlin districts we know from the corpus (order for fallback)
DEFAULT_DISTRICTS = [
    "Mitte",
    "Kreuzberg",
    "Prenzlauer Berg",
    "Friedrichshain",
    "Neukölln",
    "Charlottenburg",
]


def build_daily_slots(
    profile: Dict[str, Any],
    sights_docs: List[Dict[str, Any]],
    restaurants_docs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Group sights and restaurants by day and area.
    Returns a list of day slots, each with district and candidate sights/restaurants.
    """
    sights = parse_sights(sights_docs)
    restaurants = parse_restaurants(restaurants_docs)

    num_days = max(1, min(10, int(profile.get("num_days") or 1)))
    district_prefs = profile.get("district_preferences") or []
    pace = profile.get("pace") or "balanced"

    # Which districts to use (preferred first, then fill from defaults)
    districts_order = [d for d in district_prefs if d in DEFAULT_DISTRICTS]
    for d in DEFAULT_DISTRICTS:
        if d not in districts_order:
            districts_order.append(d)

    # Assign 1–2 districts per day depending on pace
    districts_per_day = 1 if pace == "relaxed" else (2 if pace == "packed" else 1)
    day_districts: List[List[str]] = []
    for i in range(num_days):
        start = (i * districts_per_day) % len(districts_order)
        day_ds = []
        for j in range(districts_per_day):
            day_ds.append(districts_order[(start + j) % len(districts_order)])
        day_districts.append(day_ds)

    slots: List[Dict[str, Any]] = []
    for day_num, districts in enumerate(day_districts, start=1):
        day_sights: List[Dict[str, Any]] = []
        day_restaurants: List[Dict[str, Any]] = []
        for dist in districts:
            for s in sights:
                if (s.get("neighbourhood") or "").lower() == dist.lower():
                    day_sights.append(s)
            for r in restaurants:
                if (r.get("neighbourhood") or "").lower() == dist.lower():
                    day_restaurants.append(r)
        # If no district match, add all we have (fallback)
        if not day_sights and not day_restaurants:
            day_sights = sights[: 4 + (2 if pace == "packed" else 0)]
            day_restaurants = restaurants[: 4 + (2 if pace == "packed" else 0)]

        slots.append({
            "day": day_num,
            "districts": districts,
            "sights": day_sights[:8],
            "restaurants": day_restaurants[:8],
        })

    return slots
