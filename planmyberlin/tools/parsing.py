"""Parse RAG doc content into structured place/restaurant items."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from pathlib import Path


def _extract_field(content: str, key: str) -> str | None:
    """Get value after '- Key: value' or 'Key: value'."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            line = line[2:]
        if line.lower().startswith(key.lower() + ":"):
            return line.split(":", 1)[-1].strip()
    return None


def _extract_heading(content: str) -> str | None:
    """First ### Title in content."""
    m = re.search(r"^###\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else None


def parse_sight_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Turn a sight doc (content + metadata) into a structured item."""
    content = doc.get("content") or ""
    name = _extract_heading(content) or "Unknown"
    neighbourhood = _extract_field(content, "Neighbourhood") or ""
    source_path = (doc.get("metadata") or {}).get("source") or ""
    source_file = Path(source_path).name if source_path else "places_berlin.md"
    source_type = "places" if "places" in source_file else "sights"
    return {
        "name": name,
        "neighbourhood": neighbourhood,
        "type": "sight",
        "citation": f"{source_type}: {name}",
        "content_snippet": content[:400],
    }


def parse_restaurant_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Turn a restaurant doc into a structured item with price_level."""
    content = doc.get("content") or ""
    name = _extract_heading(content) or "Unknown"
    neighbourhood = _extract_field(content, "Neighbourhood") or ""
    price_raw = _extract_field(content, "Price level") or ""
    price_level = "$"
    if "$$$" in price_raw:
        price_level = "$$$"
    elif "$$" in price_raw:
        price_level = "$$"
    elif "$" in price_raw:
        price_level = "$"
    source_path = (doc.get("metadata") or {}).get("source") or ""
    source_file = Path(source_path).name if source_path else "restaurants_berlin.md"
    source_type = "restaurants" if "restaurants" in source_file else "restaurants"

    return {
        "name": name,
        "neighbourhood": neighbourhood,
        "type": "restaurant",
        "price_level": price_level,
        "citation": f"{source_type}: {name}",
        "content_snippet": content[:400],
    }


def parse_sights(sights_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse list of sight docs into structured list."""
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for d in sights_docs:
        item = parse_sight_doc(d)
        # Many retrieved chunks are higher-level section headings (e.g. a global header)
        # and don't contain a concrete "### <Place name>" entry. Skip those so the
        # itinerary doesn't end up with placeholder "Unknown" segments.
        if item.get("name") == "Unknown":
            continue
        key = (item["name"], item["neighbourhood"])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def parse_restaurants(restaurants_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse list of restaurant docs into structured list."""
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for d in restaurants_docs:
        item = parse_restaurant_doc(d)
        # Skip non-item chunks that don't contain a concrete "### <Restaurant name>" entry.
        if item.get("name") == "Unknown":
            continue
        key = (item["name"], item["neighbourhood"])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out
