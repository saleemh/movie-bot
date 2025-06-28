import os, requests
from notion_client import Client as NotionClient
from dotenv import load_dotenv
load_dotenv()

TMDB_KEY   = os.getenv("TMDB_KEY")
NOTION_KEY = os.getenv("NOTION_KEY")
DB_ID      = os.getenv("NOTION_DB")

notion = NotionClient(auth=NOTION_KEY)
TMDB_BASE = "https://api.themoviedb.org/3"

def get_poster_url(title, year):
    print(f"🔍 Searching for poster: {title} ({year})")
    q = f"{TMDB_BASE}/search/movie?api_key={TMDB_KEY}&query={title}&year={year}"
    res = requests.get(q).json()["results"]
    if not res:
        print(f"❌ No poster found for {title} ({year})")
        return None
    path = res[0]["poster_path"]
    url = f"https://image.tmdb.org/t/p/w500{path}"
    print(f"📸 Found poster for {title}: {url}")
    return url

def update_row(page_id, title, url):
    print(f"🔄 Updating poster for {title}...")
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
    print(f"✅ Poster updated for {title}")

def fetch_movie_details(title: str, year: int) -> tuple[int | None, str | None]:
    """Return the movie runtime and synopsis, or None if not found."""
    print(f"🎬 Searching for movie details: {title} ({year})")
    # 1) Search for the movie on TMDb
    resp = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={"api_key": TMDB_KEY, "query": title, "year": year}
    ).json().get("results", [])
    if not resp:
        print(f"❌ No movie found for details search: {title} ({year})")
        return None, None

    tmdb_id = resp[0]["id"]
    print(f"🎬 Found movie ID {tmdb_id} for {title}")
    
    # 2) Fetch full movie details
    details = requests.get(
        f"{TMDB_BASE}/movie/{tmdb_id}",
        params={"api_key": TMDB_KEY}
    ).json()
    
    runtime = details.get("runtime")
    synopsis = details.get("overview")
    
    if runtime:
        print(f"⏱️  Runtime found for {title}: {runtime} minutes")
    else:
        print(f"⚠️  No runtime data available for {title}")
        
    if synopsis:
        print(f"📝 Synopsis found for {title}: {synopsis[:100]}...")
    else:
        print(f"⚠️  No synopsis available for {title}")
        
    return runtime, synopsis

# 1. Read the DB
print("📚 Fetching movies from Notion database...")
rows = notion.databases.query(database_id=DB_ID).get("results")
print(f"📋 Found {len(rows)} movies to process")
print("=" * 50)

# 2. Loop through each movie
for i, row in enumerate(rows, 1):
    title = row["properties"]["Name"]["title"][0]["plain_text"]
    year = row["properties"]["Year"]["number"]
    page_id = row["id"]
    
    print(f"\n🎬 Processing movie {i}/{len(rows)}: {title} ({year})")
    print("-" * 40)
    
    # Check if poster already exists
    poster_property = row["properties"].get("Poster", {})
    poster_files = poster_property.get("files", [])
    has_poster = len(poster_files) > 0
    
    if has_poster:
        print(f"📸 Poster already exists for {title} - skipping poster update")
    else:
        # Process poster
        url = get_poster_url(title, year)
        if url:
            update_row(page_id, title, url)
        else:
            print(f"⚠️  Skipping poster update for {title} - no poster found")

    # Check if runtime already exists
    runtime_property = row["properties"].get("Runtime", {})
    existing_runtime = runtime_property.get("number")
    
    # Check if synopsis already exists
    synopsis_property = row["properties"].get("Synopsis", {})
    existing_synopsis = synopsis_property.get("rich_text", [])
    has_synopsis = len(existing_synopsis) > 0
    
    if existing_runtime is not None and has_synopsis:
        print(f"⏱️  Runtime already exists for {title}: {existing_runtime} min - skipping details update")
        print(f"📝 Synopsis already exists for {title} - skipping details update")
    else:
        # Fetch both runtime and synopsis in one API call
        runtime, synopsis = fetch_movie_details(title, int(year))
        
        # Update properties that need updating
        update_properties = {}
        
        if runtime is not None and existing_runtime is None:
            update_properties["Runtime"] = {"number": runtime}
            print(f"🔄 Updating runtime for {title}...")
            
        if synopsis and not has_synopsis:
            update_properties["Synopsis"] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": synopsis}
                    }
                ]
            }
            print(f"🔄 Updating synopsis for {title}...")
        
        # Update Notion if we have properties to update
        if update_properties:
            notion.pages.update(
                page_id=page_id,
                properties=update_properties
            )
            
            if runtime is not None and existing_runtime is None:
                print(f"✅ Runtime updated for {title}: {runtime} min")
            if synopsis and not has_synopsis:
                print(f"✅ Synopsis updated for {title}")
        else:
            print(f"⚠️  No new details to update for {title}")
    
    print(f"✅ Completed processing: {title}")

print("\n" + "=" * 50)
print("🎉 All movies processed!")