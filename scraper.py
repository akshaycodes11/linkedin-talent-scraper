"""
scraper.py

Handles communication with the Bright Data SERP API.

Workflow:
Recruiter Query
        ↓
Google SERP Query
        ↓
Bright Data SERP API
        ↓
LinkedIn Search Results
"""

import json
import time
from typing import List, Dict
from urllib.parse import quote_plus

import requests

from config import (
    BRIGHTDATA_API_KEY,
    BRIGHTDATA_ENDPOINT,
    BRIGHTDATA_ZONE,
    TARGET_COUNTRY,
)

from utils.logger import get_logger

logger = get_logger(__name__)


# Skip non-India LinkedIn domains
NON_INDIA_DOMAINS = {
    "uk.linkedin.com",
    "au.linkedin.com",
    "ca.linkedin.com",
    "de.linkedin.com",
    "fr.linkedin.com",
    "jp.linkedin.com",
    "sg.linkedin.com",
    "hk.linkedin.com",
}


class BrightDataScraper:

    def __init__(self):

        if not BRIGHTDATA_API_KEY:
            raise ValueError("BRIGHTDATA_API_KEY is missing.")

        if not BRIGHTDATA_ENDPOINT:
            raise ValueError("BRIGHTDATA_ENDPOINT is missing.")

        if not BRIGHTDATA_ZONE:
            raise ValueError("BRIGHTDATA_ZONE is missing.")

        self.session = requests.Session()

        self.session.headers.update({
            "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
            "Content-Type": "application/json"
        })

    # -----------------------------------------------------
    # Build Google Query
    # -----------------------------------------------------

    def build_query(self, recruiter_query: str) -> str:
        recruiter_query = recruiter_query.strip()
        return f"site:linkedin.com/in {recruiter_query}"

    # -----------------------------------------------------
    # Call Bright Data
    # -----------------------------------------------------

    def call_api(self, google_query: str) -> str:

        google_url = (
            "https://www.google.com/search?q="
            f"{quote_plus(google_query)}&num=20"
        )

        payload = {
            "zone": BRIGHTDATA_ZONE,
            "url": google_url,
            "format": "json",
            "data_format": "parsed",
        }

        logger.info(f"Searching: {google_query}")

        for attempt in range(3):

            try:

                response = self.session.post(
                    BRIGHTDATA_ENDPOINT,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=60
                )

                print("Status:", response.status_code)

                if response.status_code != 200:
                    print(response.text)
                    response.raise_for_status()

                return response.json()

            except Exception as e:

                logger.warning(f"Attempt {attempt+1} failed: {e}")

                if attempt == 2:
                    raise

                time.sleep(2)
    # -----------------------------------------------------
    # Extract LinkedIn Profiles
    # -----------------------------------------------------

    def extract_results(
        self,
        response: Dict,
        limit: int
    ) -> List[Dict]:

        body = response.get("body")

        if not body:
            return []

        if isinstance(body, str):
            body = json.loads(body)

        organic = (
            body.get("organic")
            or body.get("results")
            or body.get("data")
            or []
        )

        candidates = []
        seen_urls = set()

        for item in organic:

            url = item.get("url") or item.get("link") or ""

            if not url:
                continue

            if "linkedin.com/in/" not in url:
                continue

            if any(domain in url for domain in NON_INDIA_DOMAINS):
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            candidate = {

                "title": item.get("title", ""),

                "url": url,

                "description": (
                    item.get("description")
                    or item.get("snippet")
                    or ""
                ),

                "raw_result": item

            }

            candidates.append(candidate)

            if len(candidates) >= limit:
                break

        logger.info(
            f"Found {len(candidates)} LinkedIn profiles."
        )

        return candidates

    # -----------------------------------------------------
    # Public Function
    # -----------------------------------------------------

    def search_profiles(
        self,
        recruiter_query: str,
        limit: int = 20
    ) -> List[Dict]:

        google_query = self.build_query(recruiter_query)

        response = self.call_api(google_query)

        return self.extract_results(
            response,
            limit
        )