from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional, TypedDict, Any
import os

import json

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


BudgetLevel = Literal["low", "medium", "high"]
Pace = Literal["relaxed", "balanced", "packed"]
FoodStyle = Literal[
    "cheap_lunch_nicer_dinner",
    "always_budget",
    "mixed",
]


@dataclass
class TripProfile:
    """Structured representation of a user's trip request."""

    num_days: int
    budget_level: BudgetLevel
    daily_budget_food_eur: Optional[float] = None
    district_preferences: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    avoid: List[str] = field(default_factory=list)
    pace: Pace = "balanced"
    food_style: Optional[FoodStyle] = None
    notes: str = ""


class TripProfileDict(TypedDict, total=False):
    num_days: int
    budget_level: BudgetLevel
    daily_budget_food_eur: Optional[float]
    district_preferences: List[str]
    interests: List[str]
    avoid: List[str]
    pace: Pace
    food_style: Optional[FoodStyle]
    notes: str


def _normalise_profile_dict(raw: TripProfileDict) -> TripProfile:
    """Apply basic validation and defaults to LLM output."""
    num_days = int(raw.get("num_days") or 1)
    if num_days < 1:
        num_days = 1
    if num_days > 10:
        num_days = 10

    budget_level: BudgetLevel = raw.get("budget_level") or "medium"  # type: ignore[assignment]
    if budget_level not in ("low", "medium", "high"):
        budget_level = "medium"

    daily_budget_food_eur_raw = raw.get("daily_budget_food_eur")
    daily_budget_food_eur: Optional[float]
    try:
        daily_budget_food_eur = (
            float(daily_budget_food_eur_raw) if daily_budget_food_eur_raw is not None else None
        )
    except (TypeError, ValueError):
        daily_budget_food_eur = None

    districts = [d.strip() for d in raw.get("district_preferences", []) or [] if d.strip()]
    # Normalise common Berlin spellings a bit
    normalised_districts = []
    for d in districts:
        name = d.lower()
        if "mitte" in name:
            normalised_districts.append("Mitte")
        elif "kreuzberg" in name:
            normalised_districts.append("Kreuzberg")
        elif "prenzl" in name:
            normalised_districts.append("Prenzlauer Berg")
        elif "friedrichshain" in name:
            normalised_districts.append("Friedrichshain")
        elif "tiergarten" in name:
            normalised_districts.append("Tiergarten")
        elif "neukölln" in name or "neukolln" in name:
            normalised_districts.append("Neukölln")
        elif "charlottenburg" in name:
            normalised_districts.append("Charlottenburg")
        elif "schöneberg" in name or "schoeneberg" in name or "schoneberg" in name:
            normalised_districts.append("Schöneberg")
        elif "wedding" in name:
            normalised_districts.append("Wedding")
        else:
            normalised_districts.append(d)

    interests = [i.strip().lower() for i in raw.get("interests", []) or [] if i.strip()]
    avoid = [a.strip().lower() for a in raw.get("avoid", []) or [] if a.strip()]

    pace: Pace = raw.get("pace") or "balanced"  # type: ignore[assignment]
    if pace not in ("relaxed", "balanced", "packed"):
        pace = "balanced"

    food_style = raw.get("food_style")
    if food_style not in ("cheap_lunch_nicer_dinner", "always_budget", "mixed", None):
        food_style = None  # type: ignore[assignment]

    notes = raw.get("notes") or ""

    return TripProfile(
        num_days=num_days,
        budget_level=budget_level,
        daily_budget_food_eur=daily_budget_food_eur,
        district_preferences=normalised_districts,
        interests=interests,
        avoid=avoid,
        pace=pace,
        food_style=food_style,  # type: ignore[arg-type]
        notes=notes,
    )


def parse_trip_request(
    user_text: str,
    *,
    provider: str = "openai",
    model: Optional[str] = None,
) -> TripProfile:
    """Parse a natural-language trip request into a TripProfile using the LLM."""
    provider = (provider or "openai").lower()
    if provider == "openai":
        llm = ChatOpenAI(model=model or "gpt-4o-mini")
    elif provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            raise ValueError(
                "Missing Gemini API key. Set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in your environment."
            )
        llm = ChatGoogleGenerativeAI(
            model=model or "gemini-2.5-flash",
            api_key=gemini_key,
        )
    else:
        raise ValueError(f"Unsupported trip_profile provider: {provider}")

    system = (
        "You are a Berlin trip planning assistant. "
        "Your job is to read a user's free-text trip request and output a JSON object "
        "describing their trip as a structured profile.\n\n"
        "The JSON must have this shape (no extra top-level keys):\n"
        "{\n"
        '  "num_days": int,                     // length of stay in days (1-10)\n'
        '  "budget_level": "low" | "medium" | "high",\n'
        '  "daily_budget_food_eur": number | null,\n'
        '  "district_preferences": string[],    // e.g. ["Mitte", "Kreuzberg"] if mentioned, else []\n'
        '  "interests": string[],               // e.g. ["museums", "street food", "parks"]\n'
        '  "avoid": string[],                   // e.g. ["nightlife"]\n'
        '  "pace": "relaxed" | "balanced" | "packed",\n'
        '  "food_style": "cheap_lunch_nicer_dinner" | "always_budget" | "mixed" | null,\n'
        '  "notes": string\n'
        "}\n\n"
        "Rules:\n"
        "- If the user does not specify a field, choose a reasonable default.\n"
        "- Infer num_days from phrases like 'weekend', '2-day', '3 nights', etc.\n"
        "- Infer budget_level from hints like 'budget', 'cheap', 'luxury', 'nice dinner'.\n"
        "- If the user says something like 'mix cheap lunch + nicer dinner', set food_style to 'cheap_lunch_nicer_dinner'.\n"
        "- Only mention Berlin districts in district_preferences.\n"
        "- Respond with JSON only, no extra text.\n"
    )

    human = f"User trip request:\n{user_text}\n\nReturn only the JSON object."

    response = llm.invoke(
        [
            ("system", system),
            ("user", human),
        ]
    )

    try:
        data: Any = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback: simple default profile if parsing fails
        return TripProfile(
            num_days=2,
            budget_level="medium",
            notes="Fallback profile: could not parse JSON from model.",
        )

    if not isinstance(data, dict):
        return TripProfile(
            num_days=2,
            budget_level="medium",
            notes="Fallback profile: model did not return an object.",
        )

    # TypedDict for clearer intent; runtime still uses dict
    raw_profile: TripProfileDict = data  # type: ignore[assignment]
    return _normalise_profile_dict(raw_profile)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run python -m planmyberlin.rag.trip_profile \"Your trip request here\"")
        raise SystemExit(1)

    text = " ".join(sys.argv[1:])
    profile = parse_trip_request(text)
    print(profile)

