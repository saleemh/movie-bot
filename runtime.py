#!/usr/bin/env python3
import os
import requests
from notion_client import Client
from dotenv import load_dotenv

# Load your secrets from .env
load_dotenv()
TMDB_KEY   = os.getenv("TMDB_KEY")
NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DB  = os.getenv("NOTION_DB")

# Base URLs
TMDB_BASE = "https://api.themoviedb.org/3"

# Initialize Notion client
notion = Client(auth=NOTION_KEY)

def fetch_runtime(title: str, year: int) -> int | None:
    """Return the movie runtime in minutes, or None if not found."""
    # 1) Search for the movie on TMDb
    resp = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={"api_key": TMDB_KEY, "query": title, "year": year}
    ).json().get("results", [])
    if not resp:
        return None

    tmdb_id = resp[0]["id"]
    # 2) Fetch full movie details
    details = requests.get(
        f"{TMDB_BASE}/movie/{tmdb_id}",
        params={"api_key": TMDB_KEY}
    ).json()
    return details.get("runtime")

def main():
    # Pull up to 100 pages from your database
    result = notion.databases.query(database_id=NOTION_DB, page_size=100)
    for page in result.get("results", []):
        page_id = page["id"]
        props   = page["properties"]

        # Extract Title from the "Name" property
        title_block = props["Name"]["title"]
        if not title_block:
            continue
        title = title_block[0]["plain_text"]

        # Extract Year from the "# Year" property
        year = props["Year"]["number"]
        if not year:
            continue

        # Look up runtime
        runtime = fetch_runtime(title, int(year))
        if runtime is None:
            print(f"⚠️  No runtime found for {title} ({year})")
            continue

        # Update the "Runtime" Number property
        notion.pages.update(
            page_id=page_id,
            properties={
                "Runtime": {"number": runtime}
            }
        )
        print(f"✅  {title}: {runtime} min")

if __name__ == "__main__":
    main()