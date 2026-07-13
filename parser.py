"""
parser.py

Converts Bright Data SERP results into candidate objects
ready for database insertion.
"""

import re
from typing import List, Dict


def extract_name_and_headline(title: str):
    """
    Extract name and headline from SERP title.

    Example:
    John Doe - Senior AI Engineer - Google

    Returns:
        ("John Doe", "Senior AI Engineer")
    """

    if not title:
        return "", ""

    parts = [p.strip() for p in title.split("-")]

    if len(parts) >= 2:
        return parts[0], parts[1]

    return title.strip(), ""


def extract_company(description: str):
    """
    Very lightweight company extraction.

    Looks for:
        at Google
        @ Microsoft
    """

    if not description:
        return ""

    match = re.search(r"\bat\s+([A-Z][A-Za-z0-9& .-]+)", description)

    if match:
        return match.group(1).strip()

    return ""


def resolve_location(description: str, selected_location: str = "") -> str:
    """Return the selected location only when it appears as an exact match."""

    if not selected_location:
        return "India"

    normalized_selected = selected_location.strip().lower()

    if not normalized_selected:
        return "India"

    haystack = (description or "").lower()

    if re.search(rf"(?<!\\w){re.escape(normalized_selected)}(?!\\w)", haystack):
        return selected_location.strip()

    return "India"


def parse_profiles(
    serp_results: List[Dict],
    search_query: str,
    selected_location: str = ""
) -> List[Dict]:

    candidates = []

    for result in serp_results:

        title = result.get("title", "")
        description = result.get("description", "")
        url = result.get("url", "")

        full_name, headline = extract_name_and_headline(title)

        candidate = {

            "linkedin_url": url,

            "full_name": full_name,

            "headline": headline,

            "current_company": extract_company(description),

            "location": resolve_location(
                f"{title} {description}",
                selected_location
            ),

            "total_experience_years": 0,

            "skills": [],

            "search_query": search_query,

            "source": "linkedin",

            "raw_text": description,

            "raw_json": result

        }

        candidates.append(candidate)

    return candidates