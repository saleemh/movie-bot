import os, requests
from notion_client import Client as NotionClient
from dotenv import load_dotenv
load_dotenv()

TMDB_KEY   = os.getenv("TMDB_KEY")
NOTION_KEY = os.getenv("NOTION_KEY")
DB_ID      = os.getenv("NOTION_DB")

notion = NotionClient(auth=NOTION_KEY)
TMDB_BASE = "https://api.themoviedb.org/3"

def get_poster_url(title, year=None):
    print(f"🔍 Searching for poster: {title}" + (f" ({year})" if year else ""))
    params = {"api_key": TMDB_KEY, "query": title}
    if year:
        params["year"] = year
    
    q = f"{TMDB_BASE}/search/movie"
    res = requests.get(q, params=params).json()["results"]
    if not res:
        print(f"❌ No poster found for {title}" + (f" ({year})" if year else ""))
        return None, None
    
    path = res[0]["poster_path"]
    url = f"https://image.tmdb.org/t/p/w500{path}"
    found_year = res[0].get("release_date", "")[:4] if res[0].get("release_date") else None
    found_year = int(found_year) if found_year and found_year.isdigit() else None
    
    print(f"📸 Found poster for {title}: {url}")
    if found_year:
        print(f"📅 Found year for {title}: {found_year}")
    
    return url, found_year

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

def fetch_movie_details(title: str, year: int = None) -> tuple[int | None, str | None, int | None]:
    """Return the movie runtime, synopsis, and year, or None if not found."""
    print(f"🎬 Searching for movie details: {title}" + (f" ({year})" if year else ""))
    
    # 1) Search for the movie on TMDb
    params = {"api_key": TMDB_KEY, "query": title}
    if year:
        params["year"] = year
        
    resp = requests.get(
        f"{TMDB_BASE}/search/movie",
        params=params
    ).json().get("results", [])
    
    if not resp:
        print(f"❌ No movie found for details search: {title}" + (f" ({year})" if year else ""))
        return None, None, None

    tmdb_id = resp[0]["id"]
    found_year = resp[0].get("release_date", "")[:4] if resp[0].get("release_date") else None
    found_year = int(found_year) if found_year and found_year.isdigit() else None
    
    print(f"🎬 Found movie ID {tmdb_id} for {title}")
    if found_year:
        print(f"📅 Found year for {title}: {found_year}")
    
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
        
    return runtime, synopsis, found_year

# 1. Read the DB
print("📚 Fetching movies from Notion database...")
rows = notion.databases.query(database_id=DB_ID).get("results")
print(f"📋 Found {len(rows)} movies to process")
print("=" * 50)

# 2. Loop through each movie
for i, row in enumerate(rows, 1):
    title = row["properties"]["Name"]["title"][0]["plain_text"]
    
    # Handle missing or None year
    year_property = row["properties"].get("Year", {})
    year = year_property.get("number") if year_property else None
    
    page_id = row["id"]
    
    print(f"\n🎬 Processing movie {i}/{len(rows)}: {title}" + (f" ({year})" if year else " (no year)"))
    print("-" * 40)
    
    # Check if poster already exists
    poster_property = row["properties"].get("Poster", {})
    poster_files = poster_property.get("files", [])
    has_poster = len(poster_files) > 0
    
    found_year = year  # Initialize with existing year
    
    if has_poster:
        print(f"📸 Poster already exists for {title} - skipping poster update")
    else:
        # Process poster
        url, poster_year = get_poster_url(title, year)
        if url:
            update_row(page_id, title, url)
            if poster_year and not found_year:
                found_year = poster_year
        else:
            print(f"⚠️  Skipping poster update for {title} - no poster found")

    # Check if runtime already exists
    runtime_property = row["properties"].get("Runtime", {})
    existing_runtime = runtime_property.get("number")
    
    # Check if synopsis already exists
    synopsis_property = row["properties"].get("Synopsis", {})
    existing_synopsis = synopsis_property.get("rich_text", [])
    has_synopsis = len(existing_synopsis) > 0
    
    # Check if we need to fetch details (runtime, synopsis, or year)
    need_runtime = existing_runtime is None
    need_synopsis = not has_synopsis
    need_year = year is None
    
    if not need_runtime and not need_synopsis and not need_year:
        print(f"⏱️  Runtime already exists for {title}: {existing_runtime} min")
        print(f"📝 Synopsis already exists for {title}")
        print(f"📅 Year already exists for {title}: {year}")
    else:
        # Fetch runtime, synopsis, and potentially year in one API call
        runtime, synopsis, details_year = fetch_movie_details(title, year)
        
        # Use the found year if we don't have one yet
        if details_year and not found_year:
            found_year = details_year
        
        # Update properties that need updating
        update_properties = {}
        
        if runtime is not None and need_runtime:
            update_properties["Runtime"] = {"number": runtime}
            print(f"🔄 Updating runtime for {title}...")
            
        if synopsis and need_synopsis:
            update_properties["Synopsis"] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": synopsis}
                    }
                ]
            }
            print(f"🔄 Updating synopsis for {title}...")
        
        if found_year and need_year:
            update_properties["Year"] = {"number": found_year}
            print(f"🔄 Updating year for {title}...")
        
        # Update Notion if we have properties to update
        if update_properties:
            notion.pages.update(
                page_id=page_id,
                properties=update_properties
            )
            
            if runtime is not None and need_runtime:
                print(f"✅ Runtime updated for {title}: {runtime} min")
            if synopsis and need_synopsis:
                print(f"✅ Synopsis updated for {title}")
            if found_year and need_year:
                print(f"✅ Year updated for {title}: {found_year}")
        else:
            print(f"⚠️  No new details to update for {title}")
    
    print(f"✅ Completed processing: {title}")

print("\n" + "=" * 50)
print("🎉 All movies processed!")