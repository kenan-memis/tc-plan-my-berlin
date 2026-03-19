"""Transport guidance tool: static tips (no real-time routing)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRANSPORT_DOC_PATH = PROJECT_ROOT / "data" / "raw" / "transport_overview.md"


def _read_transport_doc() -> str:
    if not TRANSPORT_DOC_PATH.exists():
        return ""
    return TRANSPORT_DOC_PATH.read_text(encoding="utf-8")


def _extract_landmark_block(transport_doc: str, landmark: str) -> str:
    """
    Extract a markdown block starting at:
      ### <landmark>
    and ending right before the next "### " heading.
    """
    if not transport_doc:
        return ""

    landmark_escaped = re.escape(landmark.strip())
    pattern = rf"^###\s+{landmark_escaped}\s*$"
    m = re.search(pattern, transport_doc, flags=re.MULTILINE)
    if not m:
        return ""

    start = m.start()
    # Next heading: another ### ... (stop at that boundary).
    m2 = re.search(r"^###\s+", transport_doc[m.end() :], flags=re.MULTILINE)
    end = m.end() + m2.start() if m2 else len(transport_doc)
    return transport_doc[start:end].strip()


def _extract_itinerary_landmarks(itinerary: Dict[str, Any]) -> List[str]:
    """
    Collect landmark names from the itinerary using simple string matching.
    """
    days = (itinerary or {}).get("days") or []
    texts: List[str] = []
    for day in days:
        for seg in (day.get("segments") or []):
            texts.append(str(seg.get("name") or ""))
            texts.append(str(seg.get("citation") or ""))

    haystack = "\n".join(texts).lower()

    candidates = [
        "Brandenburg Gate",
        "Alexanderplatz",
        "East Side Gallery",
    ]

    found: List[str] = []
    for c in candidates:
        if c.lower() in haystack:
            found.append(c)
    return found


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

    # If the itinerary includes known landmarks, append their specific transport connections.
    landmark_names = _extract_itinerary_landmarks(itinerary or {})
    if landmark_names and transport_doc:
        landmark_blocks: List[str] = []
        for ln in landmark_names:
            block = _extract_landmark_block(transport_doc, ln)
            if block:
                landmark_blocks.append(block)

        if landmark_blocks:
            guidance = (
                guidance
                + "\n\n## Example connections to key landmarks\n"
                + "\n\n".join(landmark_blocks)
            )

    return {
        "summary": guidance,
        "ticket_suggestion": ticket_suggestion,
        "mode_notes": " ".join(mode_hint_parts).strip(),
        "zones_hint": zones_hint,
    }

