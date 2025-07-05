#!/usr/bin/env python3
"""
Script to update Saleem Ranking column in Notion database to use integer values only
while maintaining the same sort order.
"""

import os
import argparse
from notion_client import Client as NotionClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DB = os.getenv("NOTION_DB")

# Initialize Notion client
notion = NotionClient(auth=NOTION_KEY)

def fetch_all_rankings():
    """Fetch all movies with their current Saleem Ranking values"""
    print("📚 Fetching all movies from Notion database...")
    
    try:
        response = notion.databases.query(database_id=NOTION_DB)
        rows = response.get("results", [])
        print(f"📋 Found {len(rows)} movies in database")
        
        movies_with_rankings = []
        movies_without_rankings = []
        
        for row in rows:
            # Get movie title
            title_property = row["properties"].get("Name", {})
            title_list = title_property.get("title", [])
            title = title_list[0]["plain_text"] if title_list else "Unknown Title"
            
            # Get current ranking
            ranking_property = row["properties"].get("Saleem Ranking", {})
            current_ranking = ranking_property.get("number")
            
            page_id = row["id"]
            
            if current_ranking is not None:
                movies_with_rankings.append({
                    "title": title,
                    "page_id": page_id,
                    "current_ranking": current_ranking
                })
                print(f"📊 {title}: Current ranking = {current_ranking}")
            else:
                movies_without_rankings.append({
                    "title": title,
                    "page_id": page_id,
                    "current_ranking": None
                })
                print(f"⚠️  {title}: No ranking set")
        
        print(f"\n📈 Movies with rankings: {len(movies_with_rankings)}")
        print(f"📉 Movies without rankings: {len(movies_without_rankings)}")
        
        return movies_with_rankings, movies_without_rankings
        
    except Exception as e:
        print(f"❌ Error fetching data from Notion: {e}")
        return [], []

def calculate_new_rankings(movies_with_rankings):
    """Calculate new integer rankings while preserving sort order"""
    print("\n🔄 Calculating new integer rankings...")
    
    if not movies_with_rankings:
        print("⚠️  No movies with rankings to process")
        return []
    
    # Sort movies by current ranking (ascending)
    sorted_movies = sorted(movies_with_rankings, key=lambda x: x["current_ranking"])
    
    print("📊 Current ranking order:")
    for i, movie in enumerate(sorted_movies):
        print(f"  {i+1}. {movie['title']}: {movie['current_ranking']}")
    
    # Assign new integer rankings (1, 2, 3, ...)
    ranking_updates = []
    for i, movie in enumerate(sorted_movies):
        new_ranking = i + 1
        ranking_updates.append({
            "title": movie["title"],
            "page_id": movie["page_id"],
            "old_ranking": movie["current_ranking"],
            "new_ranking": new_ranking
        })
    
    print(f"\n🎯 New integer rankings calculated:")
    for update in ranking_updates:
        if update["old_ranking"] != update["new_ranking"]:
            print(f"  📝 {update['title']}: {update['old_ranking']} → {update['new_ranking']}")
        else:
            print(f"  ✅ {update['title']}: {update['old_ranking']} (no change)")
    
    return ranking_updates

def update_rankings(ranking_updates, dry_run=True):
    """Update the rankings in Notion database"""
    if not ranking_updates:
        print("⚠️  No ranking updates to process")
        return
    
    changes_needed = [u for u in ranking_updates if u["old_ranking"] != u["new_ranking"]]
    no_changes = [u for u in ranking_updates if u["old_ranking"] == u["new_ranking"]]
    
    print(f"\n📊 Summary:")
    print(f"  🔄 Movies requiring updates: {len(changes_needed)}")
    print(f"  ✅ Movies with no changes: {len(no_changes)}")
    
    if dry_run:
        print(f"\n🔍 DRY RUN MODE - No actual changes will be made")
        print("=" * 60)
        
        if changes_needed:
            print("📝 Changes that WOULD be made:")
            for update in changes_needed:
                print(f"  🎬 {update['title']}")
                print(f"     Old ranking: {update['old_ranking']}")
                print(f"     New ranking: {update['new_ranking']}")
                print(f"     Page ID: {update['page_id'][:8]}...")
                print()
        else:
            print("✅ No changes needed - all rankings are already integers!")
        
        print("=" * 60)
        print("🚀 To apply these changes, run the script with --apply flag")
        
    else:
        print(f"\n🚀 APPLYING CHANGES...")
        print("=" * 60)
        
        if not changes_needed:
            print("✅ No changes needed - all rankings are already integers!")
            return
        
        success_count = 0
        error_count = 0
        
        for i, update in enumerate(changes_needed, 1):
            try:
                print(f"🔄 [{i}/{len(changes_needed)}] Updating {update['title']}...")
                print(f"   📊 {update['old_ranking']} → {update['new_ranking']}")
                
                notion.pages.update(
                    page_id=update["page_id"],
                    properties={
                        "Saleem Ranking": {
                            "number": update["new_ranking"]
                        }
                    }
                )
                
                print(f"   ✅ Successfully updated {update['title']}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating {update['title']}: {e}")
                error_count += 1
        
        print("=" * 60)
        print(f"📊 Update Results:")
        print(f"  ✅ Successful updates: {success_count}")
        print(f"  ❌ Failed updates: {error_count}")
        print(f"  📝 Total movies processed: {len(changes_needed)}")
        
        if error_count == 0:
            print("🎉 All ranking updates completed successfully!")
        else:
            print(f"⚠️  {error_count} updates failed - please check the errors above")

def main():
    parser = argparse.ArgumentParser(description="Update Saleem Ranking column to use integer values only")
    parser.add_argument("--apply", action="store_true", 
                       help="Apply the changes (default is dry-run mode)")
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    print("🎬 Saleem Ranking Integer Converter")
    print("=" * 50)
    
    if dry_run:
        print("🔍 Running in DRY RUN mode")
    else:
        print("🚀 Running in APPLY mode - changes will be made!")
    
    print()
    
    # Validate environment variables
    if not NOTION_KEY:
        print("❌ NOTION_KEY environment variable not set")
        return
    
    if not NOTION_DB:
        print("❌ NOTION_DB environment variable not set")
        return
    
    print("✅ Environment variables loaded successfully")
    print()
    
    # Step 1: Fetch all rankings
    movies_with_rankings, movies_without_rankings = fetch_all_rankings()
    
    if not movies_with_rankings:
        print("⚠️  No movies with rankings found. Nothing to update.")
        return
    
    # Step 2: Calculate new rankings
    ranking_updates = calculate_new_rankings(movies_with_rankings)
    
    # Step 3: Update rankings (dry run or apply)
    update_rankings(ranking_updates, dry_run=dry_run)
    
    print(f"\n✅ Script completed!")

if __name__ == "__main__":
    main() 