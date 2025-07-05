#!/usr/bin/env python3
"""
Script to update movie or TV show rankings in Notion database
Pulls "Name" and "Saleem Ranking" columns, sorts by ranking, and writes back integer rankings

Usage:
    python update-movie-ranking.py                    # Update movies database (default)
    python update-movie-ranking.py --tv               # Update TV shows database
    python update-movie-ranking.py --execute          # Actually update (default is dry-run)
    python update-movie-ranking.py --tv --execute     # Update TV shows database with execution
"""

import os
import argparse
from notion_client import Client as NotionClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DB = os.getenv("NOTION_DB")
NOTION_SHOW_DB = os.getenv("NOTION_SHOW_DB")

def validate_environment(use_tv_db=False):
    """Validate that required environment variables are set"""
    if not NOTION_KEY:
        print("❌ Error: NOTION_KEY environment variable not set")
        return False
    
    if use_tv_db:
        if not NOTION_SHOW_DB:
            print("❌ Error: NOTION_SHOW_DB environment variable not set")
            return False
    else:
        if not NOTION_DB:
            print("❌ Error: NOTION_DB environment variable not set")
            return False
    
    return True

def fetch_movie_data(notion_client, database_id, content_type="movies"):
    """Fetch movie/show names and rankings from Notion database"""
    print(f"📚 Fetching {content_type} from Notion database...")
    
    try:
        # Query the database with explicit parameters to get all results
        movies = []
        has_more = True
        next_cursor = None
        page_count = 0
        
        while has_more:
            page_count += 1
            print(f"📄 Fetching page {page_count}...")
            
            query_params = {
                "database_id": database_id,
                "page_size": 100  # Maximum allowed by Notion API
            }
            
            if next_cursor:
                query_params["start_cursor"] = next_cursor
            
            response = notion_client.databases.query(**query_params)
            
            print(f"📋 Page {page_count}: Found {len(response.get('results', []))} rows")
            
            for row in response.get("results", []):
                # Debug: Print available properties for first few rows
                if len(movies) < 3:
                    print(f"🔍 Debug - Available properties for row {len(movies) + 1}: {list(row['properties'].keys())}")
                
                # Extract movie name
                name_property = row["properties"].get("Name", {})
                if name_property.get("title") and len(name_property["title"]) > 0:
                    name = name_property["title"][0]["plain_text"]
                else:
                    print(f"⚠️  Skipping row with no name: {row['id']}")
                    if len(movies) < 5:  # Debug first few rows
                        print(f"🔍 Debug - Name property structure: {name_property}")
                    continue
                
                # Extract ranking
                ranking_property = row["properties"].get("Saleem Ranking", {})
                ranking = ranking_property.get("number")
                
                # Debug: Show ranking info for first few rows
                if len(movies) < 3:
                    print(f"🔍 Debug - '{name}' ranking: {ranking} (property: {ranking_property})")
                
                movies.append({
                    "page_id": row["id"],
                    "name": name,
                    "current_ranking": ranking
                })
            
            # Check if there are more pages
            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")
        
        print(f"📋 Total found: {len(movies)} {content_type} across {page_count} pages")
        
        # Additional debug: Show some stats
        movies_with_ranking = [m for m in movies if m["current_ranking"] is not None]
        movies_without_ranking = [m for m in movies if m["current_ranking"] is None]
        print(f"📊 {content_type.title()} with rankings: {len(movies_with_ranking)}")
        print(f"📊 {content_type.title()} without rankings: {len(movies_without_ranking)}")
        
        return movies
    
    except Exception as e:
        print(f"❌ Error fetching data from Notion: {e}")
        print(f"🔍 Debug - Exception type: {type(e)}")
        return []

def sort_and_assign_rankings(movies):
    """Sort movies by ranking and assign new integer rankings"""
    print("\n🔄 Processing rankings...")
    
    # Separate movies with and without rankings
    movies_with_ranking = [m for m in movies if m["current_ranking"] is not None]
    movies_without_ranking = [m for m in movies if m["current_ranking"] is None]
    
    # Sort movies with rankings by their current ranking (ascending)
    movies_with_ranking.sort(key=lambda x: x["current_ranking"])
    
    # Assign new integer rankings only to movies that already have rankings
    for i, movie in enumerate(movies_with_ranking, 1):
        movie["new_ranking"] = i
    
    # Movies without rankings remain without rankings (None/blank)
    for movie in movies_without_ranking:
        movie["new_ranking"] = None
    
    # Combine all movies (ranked first, then unranked)
    all_movies = movies_with_ranking + movies_without_ranking
    
    return all_movies

def display_ranking_changes(movies):
    """Display the ranking changes that would be made"""
    print("\n📊 Ranking Changes:")
    print("=" * 80)
    print(f"{'Rank':<6} {'Name':<40} {'Current':<12} {'New':<12} {'Change'}")
    print("-" * 80)
    
    for movie in movies:
        current = movie["current_ranking"]
        new = movie["new_ranking"]
        
        # Format current and new rankings
        current_str = f"{current}" if current is not None else "None"
        new_str = f"{new}" if new is not None else "None"
        
        # Determine change
        if current is None and new is None:
            change = "No ranking"
        elif current is None:
            change = "New ranking"
        elif new is None:
            change = "Ranking removed"
        elif current == new:
            change = "No change"
        else:
            change = f"{current} → {new}"
        
        print(f"{new_str:<6} {movie['name']:<40} {current_str:<12} {new_str:<12} {change}")

def update_notion_rankings(notion_client, movies, dry_run=True, content_type="movies"):
    """Update the rankings in Notion (or show what would be updated if dry_run=True)"""
    
    # Filter movies that need updates (only those with rankings)
    movies_to_update = [m for m in movies if m["new_ranking"] is not None]
    movies_without_ranking = [m for m in movies if m["new_ranking"] is None]
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made to Notion")
        print(f"📊 {len(movies_to_update)} {content_type} would be updated")
        print(f"📊 {len(movies_without_ranking)} {content_type} would remain without rankings")
        print("Run with --execute flag to apply changes")
        return
    
    print("\n🔄 Updating rankings in Notion...")
    print(f"📊 Updating {len(movies_to_update)} {content_type} with rankings")
    print(f"📊 Leaving {len(movies_without_ranking)} {content_type} without rankings")
    
    success_count = 0
    error_count = 0
    
    for movie in movies_to_update:
        try:
            # Update the page with new ranking
            notion_client.pages.update(
                page_id=movie["page_id"],
                properties={
                    "Saleem Ranking": {
                        "number": movie["new_ranking"]
                    }
                }
            )
            print(f"✅ Updated {movie['name']}: {movie['new_ranking']}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error updating {movie['name']}: {e}")
            error_count += 1
    
    print(f"\n📊 Update Summary:")
    print(f"✅ Successfully updated: {success_count}")
    if error_count > 0:
        print(f"❌ Errors: {error_count}")
    print(f"📊 {content_type.title()} left without rankings: {len(movies_without_ranking)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Update movie/TV show rankings in Notion database")
    parser.add_argument("--execute", action="store_true", 
                       help="Actually update the database (default is dry-run)")
    parser.add_argument("--tv", "--shows", action="store_true", 
                       help="Use TV shows database instead of movies database")
    args = parser.parse_args()
    
    # Determine database and content type
    use_tv_db = args.tv
    content_type = "TV shows" if use_tv_db else "movies"
    database_id = NOTION_SHOW_DB if use_tv_db else NOTION_DB
    
    print(f"🎬 {content_type.title()} Ranking Update Script")
    print("=" * 50)
    print(f"📊 Target: {content_type}")
    
    # Validate environment
    if not validate_environment(use_tv_db):
        return 1
    
    # Initialize Notion client
    notion = NotionClient(auth=NOTION_KEY)
    
    # Fetch data
    movies = fetch_movie_data(notion, database_id, content_type)
    if not movies:
        print(f"❌ No {content_type} found or error fetching data")
        return 1
    
    # Sort and assign rankings
    movies = sort_and_assign_rankings(movies)
    
    # Display changes
    display_ranking_changes(movies)
    
    # Update Notion (or show what would be updated)
    update_notion_rankings(notion, movies, dry_run=not args.execute, content_type=content_type)
    
    print("\n✅ Script completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main()) 