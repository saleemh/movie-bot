import os
import sys
import json
import requests
import argparse

# Configuration - Set your API keys here for mobile use
# Option 1: Set directly here (replace with your actual keys)
MOBILE_CONFIG = {
    "NOTION_KEY": "",  # Put your Notion integration token here
    "OPENAI_API_KEY": "",  # Put your OpenAI API key here
    "OPENAI_ENDPOINT": "https://api.openai.com/v1/responses",
    
    # Add your custom prompts here (replace with actual values)
    "MY_MOVIES_PROMPT_ID": "",
    "MY_MOVIES_PROMPT_VERSION": "",
    # Add more prompt configs as needed:
    # "TV_SHOWS_PROMPT_ID": "",
    # "TV_SHOWS_PROMPT_VERSION": "",
}

def setup_environment():
    """Setup environment variables for mobile use."""
    # Try to load from .env file first (if it exists)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📁 Loaded .env file")
    except ImportError:
        print("📱 dotenv not available - using direct configuration")
    except:
        print("📱 .env file not found - using direct configuration")
    
    # Set up environment variables from MOBILE_CONFIG if not already set
    for key, value in MOBILE_CONFIG.items():
        if not os.getenv(key) and value:
            os.environ[key] = value
            print(f"✅ Set {key} from mobile config")

# Initialize environment
setup_environment()

# Get configuration values
NOTION_KEY = os.getenv("NOTION_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1/responses")

# Check if we have the required keys
if not NOTION_KEY:
    print("❌ NOTION_KEY not configured!")
    print("   Please set it in the MOBILE_CONFIG section of this script")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not configured!")
    print("   Please set it in the MOBILE_CONFIG section of this script")

def interactive_setup():
    """Interactive setup for first-time users."""
    print("🔧 Interactive Setup")
    print("=" * 40)
    
    # Check if running in Pythonista
    try:
        import console
        import dialogs
        pythonista_available = True
    except ImportError:
        pythonista_available = False
    
    if pythonista_available:
        # Use Pythonista dialogs for a better mobile experience
        notion_key = dialogs.text_dialog(
            "Notion Integration Token",
            "Get this from https://notion.so/my-integrations",
            placeholder="secret_..."
        )
        
        if notion_key:
            openai_key = dialogs.text_dialog(
                "OpenAI API Key", 
                "Get this from https://platform.openai.com/api-keys",
                placeholder="sk-..."
            )
            
            if openai_key:
                # Update the environment
                os.environ["NOTION_KEY"] = notion_key
                os.environ["OPENAI_API_KEY"] = openai_key
                
                print("✅ Configuration updated!")
                print("💡 To make this permanent, edit the MOBILE_CONFIG section in this script")
                return True
    else:
        # Fallback for desktop
        print("Enter your API keys:")
        notion_key = input("Notion Integration Token: ")
        openai_key = input("OpenAI API Key: ")
        
        if notion_key and openai_key:
            os.environ["NOTION_KEY"] = notion_key
            os.environ["OPENAI_API_KEY"] = openai_key
            return True
    
    return False

# If no keys configured, offer interactive setup
if not NOTION_KEY or not OPENAI_API_KEY:
    print("\n🚀 First time setup needed!")
    print("Run interactive_setup() to configure your API keys")
    print("Or edit the MOBILE_CONFIG section in this script")
    print()
    print("Example usage:")
    print("  interactive_setup()  # Run setup")
    print("  # Then run your script normally")

def test_configuration():
    """Test if the API keys are working."""
    print("🧪 Testing Configuration")
    print("=" * 30)
    
    # Test Notion API
    if NOTION_KEY:
        try:
            url = f"{NOTION_BASE_URL}/users/me"
            headers = get_notion_headers()
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print("✅ Notion API: Working!")
                user_data = response.json()
                print(f"   Connected as: {user_data.get('name', 'Unknown')}")
            else:
                print(f"❌ Notion API: Error {response.status_code}")
                print(f"   {response.text}")
        except Exception as e:
            print(f"❌ Notion API: {e}")
    else:
        print("❌ Notion API: No key configured")
    
    # Test OpenAI API (simple test)
    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            # Just test authentication with a simple request
            url = "https://api.openai.com/v1/models"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print("✅ OpenAI API: Working!")
            else:
                print(f"❌ OpenAI API: Error {response.status_code}")
                print(f"   {response.text}")
        except Exception as e:
            print(f"❌ OpenAI API: {e}")
    else:
        print("❌ OpenAI API: No key configured")
    
    print("\n💡 If tests pass, you're ready to use the script!")

# Notion API configuration
NOTION_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

def get_notion_headers():
    """Get headers for Notion API requests."""
    return {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

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
    url = "https://api.openai.com/v1/responses"
    payload = {
        "prompt": {"id": prompt_id, "version": prompt_version},
        "input": f"Return JSON only: {input_text}",
        "model": "gpt-4o",
        "text": {"format": {"type": "json_object"}}
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        #  --- temporary debug -------------
        if response.status_code >= 400:
            print("==== OpenAI returned ====")
            print(response.status_code, response.text)   # <-- see the real reason
            response.raise_for_status()
        #  ---------------------------------
        
        data = response.json()
        
        # Responses API structure - check for 'output' field
        if "output" in data:
            output_items = data["output"]          # <- this is a list
            if not output_items:
                print("❌ Empty output list")
                return None

            # grab the first message's text
            first_item = output_items[0]
            txt = ""
            for part in first_item.get("content", []):
                if part.get("type") == "output_text":
                    txt += part.get("text", "")

            if not txt:
                print("❌ No output_text found in first message")
                return None

            # try to parse the text as JSON
            try:
                parsed = json.loads(txt)
                return parsed
            except json.JSONDecodeError:
                print("⚠️  Output wasn't valid JSON, returning raw text")
                return txt
            
        else:
            print("❌ No 'output' field found in Responses API response")
            print(f"   Available fields: {list(data.keys())}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling OpenAI Responses API: {e}")
        return None

def get_database_by_name(database_name):
    """Find a database by its title/name using direct API calls."""
    print(f"🔍 Searching for database: {database_name}")
    
    try:
        url = f"{NOTION_BASE_URL}/search"
        payload = {
            "filter": {
                "property": "object",
                "value": "database"
            }
        }
        
        response = requests.post(url, headers=get_notion_headers(), json=payload)
        response.raise_for_status()
        
        data = response.json()
        databases = data.get("results", [])
        
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
        url = f"{NOTION_BASE_URL}/databases/{database_id}/query"
        payload = {
            "filter": {
                "property": key_property,
                "rich_text": {
                    "equals": key_value
                }
            }
        }
        
        response = requests.post(url, headers=get_notion_headers(), json=payload)
        response.raise_for_status()
        
        data = response.json()
        pages = data.get("results", [])
        
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
    """Create a new page or update existing page with JSON data using direct API calls."""
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
            url = f"{NOTION_BASE_URL}/pages/{page_id}"
            payload = {"properties": properties}
            response = requests.patch(url, headers=get_notion_headers(), json=payload)
            response.raise_for_status()
            print(f"✅ Successfully updated page")
        else:
            # Create new page
            print(f"\n📝 Creating new page...")
            url = f"{NOTION_BASE_URL}/pages"
            payload = {
                "parent": {"database_id": database_id},
                "properties": properties
            }
            response = requests.post(url, headers=get_notion_headers(), json=payload)
            response.raise_for_status()
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