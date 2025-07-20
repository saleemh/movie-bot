import os
import sys
import json
import requests
import argparse
from notion_client import Client as NotionClient
from dotenv import load_dotenv

load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1/responses")

notion = NotionClient(auth=NOTION_KEY)

def get_custom_prompt_config(database_name):
    """Get custom prompt ID and version for the specified database."""
    # Convert database name to env var format (uppercase, normalize special characters)
    # Replace spaces, hyphens, and other special chars with underscores
    import re
    db_env_name = re.sub(r'[^A-Za-z0-9]', '_', database_name.upper())
    # Remove multiple consecutive underscores
    db_env_name = re.sub(r'_+', '_', db_env_name)
    # Remove leading/trailing underscores
    db_env_name = db_env_name.strip('_')
    
    prompt_id = os.getenv(f"{db_env_name}_PROMPT_ID")
    prompt_version = os.getenv(f"{db_env_name}_PROMPT_VERSION")
    
    if not prompt_id or not prompt_version:
        print(f"❌ Custom prompt configuration not found for database '{database_name}'")
        print(f"   Database name '{database_name}' maps to environment variable prefix: '{db_env_name}'")
        print(f"   Please add these environment variables to .env:")
        print(f"   {db_env_name}_PROMPT_ID=your_prompt_id")
        print(f"   {db_env_name}_PROMPT_VERSION=your_prompt_version")
        print(f"")
        print(f"   Examples for common database names:")
        print(f"   - 'My Movies' → MY_MOVIES_PROMPT_ID, MY_MOVIES_PROMPT_VERSION")
        print(f"   - 'TV Show Database' → TV_SHOW_DATABASE_PROMPT_ID, TV_SHOW_DATABASE_PROMPT_VERSION")
        print(f"   - 'Book Reviews (2024)' → BOOK_REVIEWS_2024_PROMPT_ID, BOOK_REVIEWS_2024_PROMPT_VERSION")
        return None, None
    
    print(f"🎯 Using custom prompt for '{database_name}' (env prefix: {db_env_name})")
    print(f"   ID: {prompt_id}, Version: {prompt_version}")
    return prompt_id, prompt_version

def call_openai_custom_prompt(prompt_id, prompt_version, input_text):
    """Call OpenAI Responses API with custom prompt to generate JSON output."""
    print(f"🤖 Calling custom prompt for: {input_text[:50]}...")
    
    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY not found in environment variables")
        return None
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construct payload for Responses API
    payload = {
        "prompt_id": prompt_id,
        "prompt_version": prompt_version,
        "inputs": {
            "input_text": input_text
        }
    }
    
    try:
        response = requests.post(
            OPENAI_ENDPOINT,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Responses API structure - check for 'output' field
        if "output" in data:
            output_content = data["output"]
            print(f"✅ Generated response: {str(output_content)[:200]}...")
            
            # If output is already a dict/JSON, return it directly
            if isinstance(output_content, dict):
                return output_content
            
            # If output is a string, try to parse it as JSON
            if isinstance(output_content, str):
                try:
                    parsed_json = json.loads(output_content)
                    return parsed_json
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing JSON response: {e}")
                    print(f"   Raw response: {output_content}")
                    return None
            
            # If output is neither dict nor string, return as-is and let caller handle
            return output_content
            
        else:
            print("❌ No 'output' field found in Responses API response")
            print(f"   Available fields: {list(data.keys())}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling OpenAI Responses API: {e}")
        return None

def get_database_by_name(database_name):
    """Find a database by its title/name."""
    print(f"🔍 Searching for database: {database_name}")
    
    try:
        response = notion.search(
            filter={"property": "object", "value": "database"}
        )
        
        databases = response.get("results", [])
        
        for db in databases:
            title_property = db.get("title", [])
            if title_property:
                db_title = title_property[0].get("plain_text", "")
                if db_title.lower() == database_name.lower():
                    print(f"🎯 Found database: {db_title} (ID: {db['id']})")
                    return db["id"], db
        
        print(f"❌ Database '{database_name}' not found")
        return None, None
        
    except Exception as e:
        print(f"❌ Error searching for database: {e}")
        return None, None

def get_database_properties(database):
    """Extract property names and types from database schema."""
    properties = database.get("properties", {})
    prop_info = {}
    
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type")
        prop_info[prop_name] = prop_type
    
    print(f"📋 Database properties found: {list(prop_info.keys())}")
    return prop_info

def find_existing_page(database_id, key_property, key_value):
    """Find an existing page in the database with the specified key property value."""
    print(f"🔍 Searching for existing page with {key_property} = '{key_value}'")
    
    try:
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": key_property,
                "rich_text": {
                    "equals": key_value
                }
            }
        )
        
        pages = response.get("results", [])
        
        if pages:
            page = pages[0]  # Take the first match
            print(f"✅ Found existing page: {page['id']}")
            return page["id"]
        else:
            print(f"📝 No existing page found with {key_property} = '{key_value}'")
            return None
            
    except Exception as e:
        print(f"❌ Error searching for existing page: {e}")
        return None

def format_property_value(value, prop_type):
    """Format a value according to Notion property type."""
    if prop_type == "title":
        return {
            "title": [
                {
                    "type": "text",
                    "text": {"content": str(value)}
                }
            ]
        }
    elif prop_type == "rich_text":
        return {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": str(value)}
                }
            ]
        }
    elif prop_type == "number":
        try:
            return {"number": float(value)}
        except (ValueError, TypeError):
            print(f"⚠️  Cannot convert '{value}' to number")
            return None
    elif prop_type == "checkbox":
        if isinstance(value, bool):
            return {"checkbox": value}
        elif str(value).lower() in ["true", "yes", "1"]:
            return {"checkbox": True}
        elif str(value).lower() in ["false", "no", "0"]:
            return {"checkbox": False}
        else:
            print(f"⚠️  Cannot convert '{value}' to checkbox")
            return None
    elif prop_type == "select":
        return {
            "select": {
                "name": str(value)
            }
        }
    elif prop_type == "multi_select":
        if isinstance(value, list):
            return {
                "multi_select": [{"name": str(v)} for v in value]
            }
        else:
            return {
                "multi_select": [{"name": str(value)}]
            }
    elif prop_type == "url":
        return {"url": str(value)}
    elif prop_type == "email":
        return {"email": str(value)}
    elif prop_type == "phone_number":
        return {"phone_number": str(value)}
    else:
        print(f"⚠️  Unsupported property type: {prop_type}")
        return None

def create_or_update_page(database_id, page_id, json_data, database_properties, key_property):
    """Create a new page or update existing page with JSON data."""
    properties = {}
    skipped_properties = []
    
    for key, value in json_data.items():
        if key in database_properties:
            prop_type = database_properties[key]
            formatted_value = format_property_value(value, prop_type)
            
            if formatted_value:
                properties[key] = formatted_value
                print(f"✅ Will set {key} = '{value}' (type: {prop_type})")
            else:
                skipped_properties.append((key, value, f"failed to format for {prop_type}"))
        else:
            skipped_properties.append((key, value, "property not found in database"))
    
    # Log skipped properties
    if skipped_properties:
        print("\n⚠️  Skipped properties:")
        for key, value, reason in skipped_properties:
            print(f"   ❌ {key} = '{value}' ({reason})")
    
    try:
        if page_id:
            # Update existing page
            print(f"\n🔄 Updating existing page...")
            notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            print(f"✅ Successfully updated page")
        else:
            # Create new page
            print(f"\n📝 Creating new page...")
            notion.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            print(f"✅ Successfully created new page")
        
        return True
        
    except Exception as e:
        print(f"❌ Error {'updating' if page_id else 'creating'} page: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Add or update Notion database rows using AI-generated JSON")
    parser.add_argument("database_name", help="Name of the Notion database")
    parser.add_argument("key_property", help="Name of the property to use as the key")
    parser.add_argument("input_text", help="Input text to send to the AI model")
    
    args = parser.parse_args()
    
    if not NOTION_KEY:
        print("❌ NOTION_KEY not found in environment variables")
        return 1
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return 1
    
    print(f"🎯 Database: {args.database_name}")
    print(f"🔑 Key Property: {args.key_property}")
    print(f"📝 Input Text: {args.input_text}")
    print("")
    
    # Get custom prompt configuration
    prompt_id, prompt_version = get_custom_prompt_config(args.database_name)
    if not prompt_id or not prompt_version:
        return 1
    
    # Find the database
    database_id, database = get_database_by_name(args.database_name)
    if not database_id:
        return 1
    
    # Get database properties
    database_properties = get_database_properties(database)
    
    # Validate key property exists
    if args.key_property not in database_properties:
        print(f"❌ Key property '{args.key_property}' not found in database")
        print(f"   Available properties: {list(database_properties.keys())}")
        return 1
    
    print("=" * 60)
    
    # Call OpenAI with custom prompt
    json_data = call_openai_custom_prompt(prompt_id, prompt_version, args.input_text)
    if not json_data:
        return 1
    
    # Validate key property exists in JSON response
    if args.key_property not in json_data:
        print(f"❌ Key property '{args.key_property}' not found in AI response")
        print(f"   Response keys: {list(json_data.keys())}")
        return 1
    
    key_value = json_data[args.key_property]
    print(f"🔑 Key value from AI: {key_value}")
    
    # Check for existing page
    existing_page_id = find_existing_page(database_id, args.key_property, key_value)
    
    # Create or update page
    success = create_or_update_page(
        database_id, 
        existing_page_id, 
        json_data, 
        database_properties, 
        args.key_property
    )
    
    if success:
        action = "Updated" if existing_page_id else "Created"
        print(f"\n🎉 {action} page successfully!")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 