import os
import sys
import requests
import argparse
from notion_client import Client as NotionClient
from dotenv import load_dotenv

load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SINGLE_FILL_PROMPT_ID = os.getenv("SINGLE_FILL_PROMPT_ID")
SINGLE_FILL_PROMPT_VERSION = os.getenv("SINGLE_FILL_PROMPT_VERSION")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1/responses")

notion = NotionClient(auth=NOTION_KEY)

def call_openai_api(prompt_text, input_text, max_tokens=500):
    """Call OpenAI Responses API using a custom prompt with combined prompt and input text."""
    print(f"🤖 Generating text for: {input_text[:50]}...")
    
    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY not found in environment variables")
        print("   Please add your OpenAI API key to .env")
        return None
    
    if not SINGLE_FILL_PROMPT_ID:
        print("⚠️  SINGLE_FILL_PROMPT_ID not found in environment variables")
        print("   Please add your custom prompt ID to .env")
        return None
    
    if not SINGLE_FILL_PROMPT_VERSION:
        print("⚠️  SINGLE_FILL_PROMPT_VERSION not found in environment variables")
        print("   Please add your custom prompt version to .env")
        return None
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Combine the prompt text with the input text
    combined_input = f"{prompt_text}\n\n{input_text}"
    
    payload = {
        "prompt": {
            "id": SINGLE_FILL_PROMPT_ID,
            "version": SINGLE_FILL_PROMPT_VERSION
        },
        "input": combined_input,
        "max_output_tokens": max_tokens,
        "temperature": 0.7,
        "store": False
    }
    
    try:
        response = requests.post(
            OPENAI_ENDPOINT,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Add debug output to see the actual response structure
        print(f"🔍 DEBUG: Full response keys: {list(data.keys())}")
        if "text" in data:
            print(f"🔍 DEBUG: Top-level text field: {data['text']}")
        if "output" in data and data["output"]:
            print(f"🔍 DEBUG: Output array has {len(data['output'])} items")
            for i, item in enumerate(data["output"][:2]):  # Show first 2 items
                print(f"🔍 DEBUG: Output item {i}: {item}")
        
        # Parse Responses API output - try simple format first, then complex format
        # Method 1: Simple text response (most common for text generation)
        if "output_text" in data and data["output_text"]:
            generated_text = data["output_text"].strip()
            if generated_text:
                print(f"✅ Generated text: {generated_text[:100]}...")
                return generated_text
        
        # Method 2: Complex output array format (for tool calls, multi-step responses)
        if "output" in data and data["output"]:
            # The output is an array of items, look for text content
            for item in data["output"]:
                print(f"🔍 DEBUG: Processing item: {item}")
                
                if item.get("type") == "text" and item.get("content"):
                    generated_text = item.get("content", "").strip()
                    if generated_text:
                        print(f"✅ Generated text: {generated_text[:100]}...")
                        return generated_text
                # Also check for direct text field in items
                elif item.get("type") == "message" and item.get("content"):
                    # Handle message type responses
                    content = item.get("content")
                    print(f"🔍 DEBUG: Message content: {content}")
                    if isinstance(content, list):
                        for content_item in content:
                            print(f"🔍 DEBUG: Content item: {content_item}")
                            # Fix: Check for "output_text" type and extract "text" field
                            if content_item.get("type") == "output_text" and content_item.get("text"):
                                print(f"🔍 DEBUG: Found output_text type item")
                                print(f"🔍 DEBUG: Raw text value: {repr(content_item.get('text'))}")
                                generated_text = content_item.get("text", "").strip()
                                print(f"🔍 DEBUG: After processing: {repr(generated_text)}")
                                if generated_text:
                                    print(f"✅ Generated text: {generated_text[:100]}...")
                                    return generated_text
                            # Also keep the original logic for "text" type
                            elif content_item.get("type") == "text" and content_item.get("text"):
                                generated_text = content_item.get("text", "").strip()
                                if generated_text:
                                    print(f"✅ Generated text: {generated_text[:100]}...")
                                    return generated_text
                    elif isinstance(content, str):
                        generated_text = content.strip()
                        if generated_text:
                            print(f"✅ Generated text: {generated_text[:100]}...")
                            return generated_text
        
        # Method 3: Fallback to check direct text field (only if nothing found above)
        print("🔍 DEBUG: No text found in output array, trying fallback methods...")
        if "text" in data and data["text"]:
            print(f"🔍 DEBUG: Trying fallback text field: {data['text']}")
            if isinstance(data["text"], dict) and "content" in data["text"]:
                generated_text = data["text"]["content"].strip()
            elif isinstance(data["text"], str):
                generated_text = data["text"].strip()
            else:
                generated_text = str(data["text"]).strip()
            
            if generated_text:
                print(f"✅ Generated text (fallback): {generated_text[:100]}...")
                return generated_text
        
        # If we get here, no text was found
        print("❌ No text content found in API response")
        print(f"Response keys: {list(data.keys())}")
        
        # Enhanced debugging - show structure of key fields
        if "output_text" in data:
            print(f"output_text: {data['output_text']}")
        if "output" in data:
            print(f"Output array length: {len(data['output']) if data['output'] else 0}")
            if data['output']:
                print(f"First output item: {data['output'][0]}")
        if "text" in data:
            print(f"Text field: {data['text']}")
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling OpenAI Responses API: {e}")
        # Print response content for debugging
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response content: {e.response.text}")
        return None

def get_database_by_name(database_name):
    """Find a database by its title/name."""
    print(f"🔍 Searching for database: {database_name}")
    
    try:
        # List ALL databases the integration has access to
        print("🔍 Listing all accessible databases...")
        all_response = notion.search(
            filter={"property": "object", "value": "database"}
        )
        
        all_databases = all_response.get("results", [])
        
        print(f"📋 Found {len(all_databases)} accessible databases:")
        
        if not all_databases:
            print("❌ No databases accessible to this integration!")
            print("\n🔧 To fix this:")
            print("1. Go to your Notion database")
            print("2. Click the '...' menu (top right)")
            print("3. Select 'Connect to' or 'Add connections'")
            print("4. Find and select your integration")
            print("5. Make sure it has 'Read' and 'Update' permissions")
            return None
        
        # List all accessible databases
        for db in all_databases:
            title_property = db.get("title", [])
            if title_property:
                db_title = title_property[0].get("plain_text", "")
                print(f"  ✅ {db_title}")
                
                # Check for exact match (case-insensitive)
                if db_title.lower() == database_name.lower():
                    print(f"🎯 Found matching database: {db_title} (ID: {db['id']})")
                    return db["id"]
        
        # If we get here, no exact match was found
        print(f"\n❌ Database '{database_name}' not found in accessible databases")
        print("💡 Make sure:")
        print("1. The database name matches exactly (case doesn't matter)")
        print("2. Your integration has access to this database")
        print("3. Try copying the exact name from the list above")
        
        return None
        
    except Exception as e:
        print(f"❌ Error searching for database: {e}")
        return None

def update_page_with_text(page_id, output_property, generated_text, page_title):
    """Update a Notion page with generated text in the specified property."""
    print(f"🔄 Updating {output_property} for: {page_title}")
    print(f"🔍 DEBUG: Value being sent to Notion: {repr(generated_text)}")
    print(f"🔍 DEBUG: Value type: {type(generated_text)}")
    
    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                output_property: {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": generated_text}
                        }
                    ]
                }
            }
        )
        print(f"✅ Text updated for: {page_title}")
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
    parser = argparse.ArgumentParser(description="Enrich Notion database pages with AI-generated text using custom prompts")
    parser.add_argument("database_name", help="Name of the Notion database")
    parser.add_argument("input_property", help="Name of the input property (text)")
    parser.add_argument("output_property", help="Name of the output property (text/rich_text)")
    parser.add_argument("prompt_text", help="Prompt text to combine with input property value")
    parser.add_argument("--skip-existing", action="store_true", 
                       help="Skip pages that already have text in the output property")
    parser.add_argument("--max-tokens", type=int, default=500,
                       help="Maximum tokens for AI response (default: 500)")
    
    args = parser.parse_args()
    
    if not NOTION_KEY:
        print("❌ NOTION_KEY not found in environment variables")
        print("   Please add your Notion integration token to .env")
        return 1
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Please add your OpenAI API key to .env")
        return 1
    
    if not SINGLE_FILL_PROMPT_ID:
        print("❌ SINGLE_FILL_PROMPT_ID not found in environment variables")
        print("   Please add your custom prompt ID to .env")
        return 1
    
    if not SINGLE_FILL_PROMPT_VERSION:
        print("❌ SINGLE_FILL_PROMPT_VERSION not found in environment variables")
        print("   Please add your custom prompt version to .env")
        return 1
    
    print(f"🤖 Using OpenAI Responses API with custom prompt: {SINGLE_FILL_PROMPT_ID} (v{SINGLE_FILL_PROMPT_VERSION})")
    print(f"📋 Processing database: {args.database_name}")
    print(f"📝 Input property: {args.input_property}")
    print(f"📄 Output property: {args.output_property}")
    print(f"💬 Prompt: {args.prompt_text}")
    print("")
    
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
        
        # Check if output property already has text (if skip-existing is enabled)
        if args.skip_existing:
            output_prop = properties.get(args.output_property, {})
            existing_text = output_prop.get("rich_text", [])
            if existing_text and existing_text[0].get("plain_text", "").strip():
                print(f"⏭️  Skipping {page_title} - already has text in {args.output_property}")
                skipped += 1
                continue
        
        # Get input property value
        input_value = get_property_value(properties, args.input_property)
        
        if not input_value:
            print(f"⚠️  No text found in {args.input_property} for: {page_title}")
            skipped += 1
            continue
        
        print(f"📝 Input text: {input_value}")
        
        # Generate text using AI
        generated_text = call_openai_api(args.prompt_text, input_value, args.max_tokens)
        
        if not generated_text:
            print(f"⚠️  No text generated for: {page_title}")
            errors += 1
            continue
        
        # Update page with generated text
        if update_page_with_text(page_id, args.output_property, generated_text, page_title):
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