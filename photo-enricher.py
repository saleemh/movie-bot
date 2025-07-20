import os
import sys
import requests
import argparse
from notion_client import Client as NotionClient
from dotenv import load_dotenv

load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

notion = NotionClient(auth=NOTION_KEY)

def search_image(query):
    """Search for an image using Unsplash API."""
    print(f"🔍 Searching for image: {query}")
    
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY not found in environment variables")
        print("   Please sign up at https://unsplash.com/developers and add your access key to .env")
        return None
    
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    params = {
        "query": query,
        "per_page": 1,
        "order_by": "relevant"
    }
    
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print(f"❌ No images found for: {query}")
            return None
        
        image_url = results[0]["urls"]["regular"]
        photographer = results[0]["user"]["name"]
        photo_link = results[0]["links"]["html"]
        
        print(f"📸 Found image by {photographer}: {image_url}")
        return {
            "url": image_url,
            "photographer": photographer,
            "source_link": photo_link
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error searching for image: {e}")
        return None

def get_database_by_name(database_name):
    """Find a database by its title/name."""
    print(f"🔍 Searching for database: {database_name}")
    
    try:
        # Search for databases
        response = notion.search(
            query=database_name,
            filter={"property": "object", "value": "database"}
        )
        
        results = response.get("results", [])
        
        for db in results:
            title_property = db.get("title", [])
            if title_property:
                db_title = title_property[0].get("plain_text", "")
                if db_title.lower() == database_name.lower():
                    print(f"✅ Found database: {db_title} (ID: {db['id']})")
                    return db["id"]
        
        print(f"❌ Database not found: {database_name}")
        print("Available databases:")
        for db in results:
            title_property = db.get("title", [])
            if title_property:
                db_title = title_property[0].get("plain_text", "")
                print(f"  - {db_title}")
        return None
        
    except Exception as e:
        print(f"❌ Error searching for database: {e}")
        return None

def update_page_with_image(page_id, output_property, image_data, page_title):
    """Update a Notion page with an image in the specified property."""
    print(f"🔄 Updating {output_property} for: {page_title}")
    
    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                output_property: {
                    "files": [
                        {
                            "name": f"{page_title} - Photo by {image_data['photographer']}",
                            "type": "external",
                            "external": {"url": image_data["url"]}
                        }
                    ]
                }
            }
        )
        print(f"✅ Image updated for: {page_title}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating page {page_title}: {e}")
        return False

def get_property_value(page_properties, property_name):
    """Extract text value from a Notion property."""
    prop = page_properties.get(property_name, {})
    prop_type = prop.get("type")
    
    if prop_type == "title":
        title_list = prop.get("title", [])
        if title_list:
            return title_list[0].get("plain_text", "")
    elif prop_type == "rich_text":
        rich_text_list = prop.get("rich_text", [])
        if rich_text_list:
            return rich_text_list[0].get("plain_text", "")
    elif prop_type == "plain_text":
        return prop.get("plain_text", "")
    elif prop_type == "formula":
        # Handle formula (Function) properties
        formula_data = prop.get("formula", {})
        formula_type = formula_data.get("type")
        
        if formula_type == "string":
            return formula_data.get("string", "")
        elif formula_type == "number":
            number_val = formula_data.get("number")
            return str(number_val) if number_val is not None else ""
        elif formula_type == "boolean":
            boolean_val = formula_data.get("boolean")
            return str(boolean_val) if boolean_val is not None else ""
        elif formula_type == "date":
            date_data = formula_data.get("date", {})
            if date_data:
                return date_data.get("start", "")
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Enrich Notion database pages with images")
    parser.add_argument("database_name", help="Name of the Notion database")
    parser.add_argument("input_property", help="Name of the input property (text)")
    parser.add_argument("output_property", help="Name of the output property (files)")
    parser.add_argument("--skip-existing", action="store_true", 
                       help="Skip pages that already have images in the output property")
    
    args = parser.parse_args()
    
    if not NOTION_KEY:
        print("❌ NOTION_KEY not found in environment variables")
        print("   Please add your Notion integration token to .env")
        return 1
    
    # Find the database
    database_id = get_database_by_name(args.database_name)
    if not database_id:
        return 1
    
    # Query the database
    print(f"📚 Fetching pages from database: {args.database_name}")
    try:
        response = notion.databases.query(database_id=database_id)
        pages = response.get("results", [])
        print(f"📋 Found {len(pages)} pages to process")
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        return 1
    
    if not pages:
        print("⚠️  No pages found in database")
        return 0
    
    print("=" * 60)
    
    # Process each page
    processed = 0
    skipped = 0
    errors = 0
    
    for i, page in enumerate(pages, 1):
        properties = page["properties"]
        page_id = page["id"]
        
        # Get page title for display
        page_title = "Untitled"
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_list = prop_data.get("title", [])
                if title_list:
                    page_title = title_list[0].get("plain_text", "Untitled")
                break
        
        print(f"\n🔄 Processing page {i}/{len(pages)}: {page_title}")
        print("-" * 40)
        
        # Check if output property already has images (if skip-existing is enabled)
        if args.skip_existing:
            output_prop = properties.get(args.output_property, {})
            existing_files = output_prop.get("files", [])
            if existing_files:
                print(f"⏭️  Skipping {page_title} - already has images in {args.output_property}")
                skipped += 1
                continue
        
        # Get input property value
        input_value = get_property_value(properties, args.input_property)
        
        if not input_value:
            print(f"⚠️  No text found in {args.input_property} for: {page_title}")
            skipped += 1
            continue
        
        print(f"📝 Input text: {input_value}")
        
        # Search for image
        image_data = search_image(input_value)
        
        if not image_data:
            print(f"⚠️  No image found for: {page_title}")
            errors += 1
            continue
        
        # Update page with image
        if update_page_with_image(page_id, args.output_property, image_data, page_title):
            processed += 1
        else:
            errors += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Processing complete!")
    print(f"✅ Successfully processed: {processed} pages")
    print(f"⏭️  Skipped: {skipped} pages")
    print(f"❌ Errors: {errors} pages")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 