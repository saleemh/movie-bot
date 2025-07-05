import os, requests
from notion_client import Client as NotionClient
from dotenv import load_dotenv
load_dotenv()

TMDB_KEY   = os.getenv("TMDB_KEY")
NOTION_KEY = os.getenv("NOTION_KEY")
DB_ID      = os.getenv("NOTION_SHOW_DB")

notion = NotionClient(auth=NOTION_KEY)
TMDB_BASE = "https://api.themoviedb.org/3"

def get_poster_url(title):
    print(f"🔍 Searching for poster: {title}")
    q = f"{TMDB_BASE}/search/tv?api_key={TMDB_KEY}&query={title}"
    res = requests.get(q).json()["results"]
    if not res:
        print(f"❌ No poster found for {title}")
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

def fetch_show_details(title: str) -> tuple[int | None, str | None]:
    """Return the show year and synopsis, or None if not found."""
    print(f"📺 Searching for TV show details: {title}")
    # 1) Search for the TV show on TMDb
    resp = requests.get(
        f"{TMDB_BASE}/search/tv",
        params={"api_key": TMDB_KEY, "query": title}
    ).json().get("results", [])
    if not resp:
        print(f"❌ No TV show found for details search: {title}")
        return None, None

    tmdb_id = resp[0]["id"]
    print(f"📺 Found TV show ID {tmdb_id} for {title}")
    
    # 2) Fetch full TV show details
    details = requests.get(
        f"{TMDB_BASE}/tv/{tmdb_id}",
        params={"api_key": TMDB_KEY}
    ).json()
    
    # Extract year from first_air_date
    first_air_date = details.get("first_air_date")
    year = None
    if first_air_date:
        year = int(first_air_date.split("-")[0])
    
    synopsis = details.get("overview")
    
    if year:
        print(f"📅 Year found for {title}: {year}")
    else:
        print(f"⚠️  No year data available for {title}")
        
    if synopsis:
        print(f"📝 Synopsis found for {title}: {synopsis[:100]}...")
    else:
        print(f"⚠️  No synopsis available for {title}")
        
    return year, synopsis

# 1. Read the DB
print("📚 Fetching TV shows from Notion database...")
rows = notion.databases.query(database_id=DB_ID).get("results")
print(f"📋 Found {len(rows)} TV shows to process")
print("=" * 50)

# 2. Loop through each TV show
for i, row in enumerate(rows, 1):
    # Check if title exists and is not empty
    title_list = row["properties"]["Name"]["title"]
    if not title_list:
        print(f"\n⚠️  Skipping TV show {i}/{len(rows)} - no title found")
        continue
        
    title = title_list[0]["plain_text"]
    page_id = row["id"]
    
    print(f"\n📺 Processing TV show {i}/{len(rows)}: {title}")
    print("-" * 40)
    
    # Check if poster already exists
    poster_property = row["properties"].get("Poster", {})
    poster_files = poster_property.get("files", [])
    has_poster = len(poster_files) > 0
    
    if has_poster:
        print(f"📸 Poster already exists for {title} - skipping poster update")
    else:
        # Process poster
        url = get_poster_url(title)
        if url:
            update_row(page_id, title, url)
        else:
            print(f"⚠️  Skipping poster update for {title} - no poster found")

    # Check if year already exists
    year_property = row["properties"].get("Year", {})
    existing_year = year_property.get("number")
    
    # Check if synopsis already exists
    synopsis_property = row["properties"].get("Synopsis", {})
    existing_synopsis = synopsis_property.get("rich_text", [])
    has_synopsis = len(existing_synopsis) > 0
    
    if existing_year is not None and has_synopsis:
        print(f"📅 Year already exists for {title}: {existing_year} - skipping details update")
        print(f"📝 Synopsis already exists for {title} - skipping details update")
    else:
        # Fetch both year and synopsis in one API call
        year, synopsis = fetch_show_details(title)
        
        # Update properties that need updating
        update_properties = {}
        
        if year is not None and existing_year is None:
            update_properties["Year"] = {"number": year}
            print(f"🔄 Updating year for {title}...")
            
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
            
            if year is not None and existing_year is None:
                print(f"✅ Year updated for {title}: {year}")
            if synopsis and not has_synopsis:
                print(f"✅ Synopsis updated for {title}")
        else:
            print(f"⚠️  No new details to update for {title}")
    
    print(f"✅ Completed processing: {title}")

print("\n" + "=" * 50)
print("🎉 All TV shows processed!") 