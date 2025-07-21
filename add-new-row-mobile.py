import os
import sys
import json
import requests

# Try to import Pythonista-specific modules
try:
    import dialogs
    import keychain
    PYTHONISTA_AVAILABLE = True
except ImportError:
    PYTHONISTA_AVAILABLE = False
    print("⚠️  Pythonista modules not available - running in desktop mode")

# Try to import notion_client
try:
    from notion_client import Client as NotionClient
    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False
    print("❌ notion_client not installed")
    print("📱 To install on Pythonista:")
    print("   1. Open Pythonista")
    print("   2. Go to Settings > External Modules")
    print("   3. Install 'notion-client'")
    print("   4. Or use: pip install notion-client")

# Configuration - Replace these with your actual values or set them securely
CONFIG = {
    "NOTION_KEY": "",
    "OPENAI_API_KEY": "",
    "OPENAI_ENDPOINT": "https://api.openai.com/v1/responses"
}

def get_config_value(key, description):
    """Get configuration value from keychain, config, or user input."""
    if PYTHONISTA_AVAILABLE:
        # Try to get from keychain first
        try:
            value = keychain.get_password("movie-bot", key)
            if value:
                return value
        except:
            pass
    
    # Try from CONFIG dictionary
    if CONFIG.get(key):
        return CONFIG[key]
    
    # Ask user for input
    if PYTHONISTA_AVAILABLE:
        value = dialogs.text_dialog(f"Enter {description}", placeholder=f"Your {description}")
        if value:
            # Save to keychain for future use
            try:
                keychain.set_password("movie-bot", key, value)
            except:
                pass
        return value
    else:
        # Desktop fallback
        return input(f"Enter {description}: ")

def setup_config():
    """Setup configuration values."""
    print("🔧 Setting up configuration...")
    
    notion_key = get_config_value("NOTION_KEY", "Notion Integration Token")
    openai_key = get_config_value("OPENAI_API_KEY", "OpenAI API Key")
    
    if not notion_key or not openai_key:
        print("❌ Required API keys not provided")
        return None, None
    
    return notion_key, openai_key

def get_user_inputs():
    """Get user inputs via dialog boxes or command line."""
    if PYTHONISTA_AVAILABLE:
        # Use Pythonista dialogs
        database_name = dialogs.text_dialog(
            "Database Name", 
            "Enter the name of your Notion database",
            placeholder="My Database"
        )
        
        if not database_name:
            return None, None, None
        
        key_property = dialogs.text_dialog(
            "Key Property", 
            "Enter the property name to use as the unique key",
            placeholder="Name"
        )
        
        if not key_property:
            return None, None, None
        
        input_text = dialogs.text_dialog(
            "Input Text", 
            "Enter the text to send to AI for processing",
            placeholder="Describe what you want to add..."
        )
        
        if not input_text:
            return None, None, None
            
        return database_name, key_property, input_text
        
    else:
        # Desktop fallback
        print("\n📝 Please provide the following information:")
        database_name = input("Database name: ")
        key_property = input("Key property name: ")
        input_text = input("Input text: ")
        return database_name, key_property, input_text

def get_custom_prompt_config(database_name):
    """Get custom prompt ID and version for the specified database."""
    import re
    db_env_name = re.sub(r'[^A-Za-z0-9]', '_', database_name.upper())
    db_env_name = re.sub(r'_+', '_', db_env_name)
    db_env_name = db_env_name.strip('_')
    
    # Try to get from keychain or ask user
    prompt_id_key = f"{db_env_name}_PROMPT_ID"
    prompt_version_key = f"{db_env_name}_PROMPT_VERSION"
    
    prompt_id = get_config_value(prompt_id_key, f"Prompt ID for {database_name}")
    prompt_version = get_config_value(prompt_version_key, f"Prompt Version for {database_name}")
    
    if not prompt_id or not prompt_version:
        print(f"❌ Custom prompt configuration not found for database '{database_name}'")
        print(f"   Database name '{database_name}' maps to keys: '{prompt_id_key}', '{prompt_version_key}'")
        return None, None
    
    print(f"🎯 Using custom prompt for '{database_name}'")
    print(f"   ID: {prompt_id}, Version: {prompt_version}")
    return prompt_id, prompt_version

def call_openai_custom_prompt(openai_api_key, prompt_id, prompt_version, input_text):
    """Call OpenAI Responses API with custom prompt to generate JSON output."""
    print(f"🤖 Calling custom prompt for: {input_text[:50]}...")
    
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.openai.com/v1/responses"
    payload = {
        "prompt": {"id": prompt_id, "version": prompt_version},
        "input": f"Return JSON only: {input_text}",
        "model": "gpt-4o",
        "text": {"format": {"type": "json_object"}}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code >= 400:
            print("==== OpenAI returned ====")
            print(response.status_code, response.text)
            response.raise_for_status()
        
        data = response.json()
        
        if "output" in data:
            output_items = data["output"]
            if not output_items:
                print("❌ Empty output list")
                return None

            first_item = output_items[0]
            txt = ""
            for part in first_item.get("content", []):
                if part.get("type") == "output_text":
                    txt += part.get("text", "")

            if not txt:
                print("❌ No output_text found in first message")
                return None

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

def get_database_by_name(notion, database_name):
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

def find_existing_page(notion, database_id, key_property, key_value):
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
            page = pages[0]
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

def create_or_update_page(notion, database_id, page_id, json_data, database_properties, key_property):
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
    
    if skipped_properties:
        print("\n⚠️  Skipped properties:")
        for key, value, reason in skipped_properties:
            print(f"   ❌ {key} = '{value}' ({reason})")
    
    try:
        if page_id:
            print(f"\n🔄 Updating existing page...")
            notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            print(f"✅ Successfully updated page")
        else:
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

def show_success_dialog():
    """Show success message."""
    if PYTHONISTA_AVAILABLE:
        dialogs.alert("Success! ✅", "Page created/updated successfully", "OK")
    else:
        print("\n🎉 Page created/updated successfully!")

def show_error_dialog(message):
    """Show error message."""
    if PYTHONISTA_AVAILABLE:
        dialogs.alert("Error ❌", message, "OK")
    else:
        print(f"\n❌ {message}")

def main():
    print("🚀 Notion Row Creator - Mobile Edition")
    print("=" * 40)
    
    # Check dependencies
    if not NOTION_CLIENT_AVAILABLE:
        show_error_dialog("notion_client library not installed. Please install it first.")
        return 1
    
    # Setup configuration
    notion_key, openai_key = setup_config()
    if not notion_key or not openai_key:
        show_error_dialog("Required API keys not provided")
        return 1
    
    # Initialize Notion client
    notion = NotionClient(auth=notion_key)
    
    # Get user inputs
    database_name, key_property, input_text = get_user_inputs()
    if not all([database_name, key_property, input_text]):
        show_error_dialog("All inputs are required")
        return 1
    
    print(f"🎯 Database: {database_name}")
    print(f"🔑 Key Property: {key_property}")
    print(f"📝 Input Text: {input_text}")
    print("")
    
    # Get custom prompt configuration
    prompt_id, prompt_version = get_custom_prompt_config(database_name)
    if not prompt_id or not prompt_version:
        show_error_dialog("Custom prompt configuration not found")
        return 1
    
    # Find the database
    database_id, database = get_database_by_name(notion, database_name)
    if not database_id:
        show_error_dialog(f"Database '{database_name}' not found")
        return 1
    
    # Get database properties
    database_properties = get_database_properties(database)
    
    # Validate key property exists
    if key_property not in database_properties:
        show_error_dialog(f"Key property '{key_property}' not found in database")
        return 1
    
    print("=" * 60)
    
    # Call OpenAI with custom prompt
    json_data = call_openai_custom_prompt(openai_key, prompt_id, prompt_version, input_text)
    if not json_data:
        show_error_dialog("Failed to get response from OpenAI")
        return 1
    
    # Validate key property exists in JSON response
    if key_property not in json_data:
        show_error_dialog(f"Key property '{key_property}' not found in AI response")
        return 1
    
    key_value = json_data[key_property]
    print(f"🔑 Key value from AI: {key_value}")
    
    # Check for existing page
    existing_page_id = find_existing_page(notion, database_id, key_property, key_value)
    
    # Create or update page
    success = create_or_update_page(
        notion, 
        database_id, 
        existing_page_id, 
        json_data, 
        database_properties, 
        key_property
    )
    
    if success:
        show_success_dialog()
        return 0
    else:
        show_error_dialog("Failed to create/update page")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        show_error_dialog(error_msg)
        print(f"❌ {error_msg}")
        sys.exit(1) 