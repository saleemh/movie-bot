import os, requests
from notion_client import Client as NotionClient
from dotenv import load_dotenv
load_dotenv()

TMDB_KEY   = os.getenv("TMDB_KEY")
NOTION_KEY = os.getenv("NOTION_KEY")
DB_ID      = os.getenv("NOTION_DB")

notion = NotionClient(auth=NOTION_KEY)
base   = "https://api.themoviedb.org/3"

def get_poster_url(title, year):
    q = f"{base}/search/movie?api_key={TMDB_KEY}&query={title}&year={year}"
    res = requests.get(q).json()["results"]
    if not res: return None
    path = res[0]["poster_path"]
    return f"https://image.tmdb.org/t/p/w500{path}"   # 500 px wide

def update_row(page_id, title, url):
    notion.pages.update(
        page_id=page_id,
        properties={
            "Poster": {
                "files": [
                    {
                        "name": f"{title} poster",       # ← required!
                        "type": "external",
                        "external": {"url": url}
                    }
                ]
            }
        }
    )

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

# 1. Read the DB
rows = notion.databases.query(database_id=DB_ID).get("results")

# 2. Loop through each movie
for row in rows:
    title = row["properties"]["Name"]["title"][0]["plain_text"]
    year = row["properties"]["Year"]["number"]
    page_id = row["id"]
    url = get_poster_url(title, year)
    if url:
        update_row(page_id, title, url)
        print(f"✅  {title}: {url}")

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