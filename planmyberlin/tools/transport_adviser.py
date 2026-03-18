"""Transport guidance tool: static tips (no real-time routing)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRANSPORT_DOC_PATH = PROJECT_ROOT / "data" / "raw" / "transport_overview.md"


def _read_transport_doc() -> str:
    if not TRANSPORT_DOC_PATH.exists():
        return ""
    return TRANSPORT_DOC_PATH.read_text(encoding="utf-8")


def build_transport_guidance(profile: Dict[str, Any], itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a short 'getting around' section using the static transport overview plus
    the trip's districts and user constraints (e.g. 'only metro').
    """
    transport_doc = _read_transport_doc()
    districts: List[str] = profile.get("district_preferences") or []
    num_days = profile.get("num_days") or itinerary.get("num_days") or 1
    notes = (profile.get("notes") or "").lower()

    # Preference detection (very simple, based on user text that ended up in notes)
    wants_metro_only = "metro" in notes or "u-bahn" in notes or "ubahn" in notes
    wants_public_transport = wants_metro_only or ("public transport" in notes) or ("s-bahn" in notes)
    wants_walking = "walk" in notes or "walking" in notes

    # Ticket suggestion (simple heuristics, no prices)
    if int(num_days) <= 1:
        ticket_suggestion = "If you’ll take several rides in one day, consider a Day ticket (AB). Otherwise, a single ticket (AB) is fine for occasional rides."
    else:
        ticket_suggestion = "For 2+ days of sightseeing, a Day ticket (AB) each day (or a multi-day tourist pass) is usually convenient for unlimited rides."

    # District movement hints (no routes)
    if len(districts) >= 2:
        movement_hint = (
            "Try to group activities by district to reduce transfers. For cross-city moves, the S‑Bahn Ring (S41/S42) and major hubs like Alexanderplatz or Hauptbahnhof are useful."
        )
    else:
        movement_hint = (
            "Keep activities within the same district where possible to minimise travel time. For longer jumps, use the S‑Bahn/U‑Bahn network via a major hub (e.g. Alexanderplatz)."
        )

    mode_hint_parts: List[str] = []
    if wants_walking:
        mode_hint_parts.append("You mentioned walking—this plan tries to keep each day focused on one area.")
    if wants_metro_only:
        mode_hint_parts.append("You mentioned metro-only (U‑Bahn). Note: some district-to-district trips may be faster with S‑Bahn.")
    elif wants_public_transport:
        mode_hint_parts.append("You mentioned public transport—assume U‑Bahn/S‑Bahn/tram/bus as needed.")

    zones_hint = ""
    if transport_doc:
        zones_hint = "Berlin transport zones are A (inside the ring), B (outer city), C (surroundings like Potsdam/airport region). For most visitor itineraries, AB is enough."

    guidance_lines = [
        zones_hint,
        ticket_suggestion,
        movement_hint,
        " ".join(mode_hint_parts).strip(),
    ]
    guidance = "\n\n".join([g for g in guidance_lines if g])

    return {
        "summary": guidance,
        "ticket_suggestion": ticket_suggestion,
        "mode_notes": " ".join(mode_hint_parts).strip(),
        "zones_hint": zones_hint,
    }

