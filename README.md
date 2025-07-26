# Notion Database Enhancement Scripts

This repository contains Python scripts for enhancing Notion databases with AI-generated content, images, and automated data entry using various APIs.

## Scripts Overview

### 1. property-text-enricher.py
Enriches Notion database pages with AI-generated text using OpenAI's Responses API and custom prompts. Perfect for generating descriptions, summaries, marketing copy, or any text content based on existing data.

### 2. photo-enricher.py
Automatically adds relevant images to Notion database pages by searching Unsplash based on text properties. Great for adding visual content to travel databases, product catalogs, or any content that benefits from imagery.

### 3. add-new-row.py
Creates new Notion database entries or updates existing ones using AI-generated structured data. Uses database-specific custom prompts to convert natural language input into properly formatted database rows.

### 4. add-paris-attraction (Convenience Script)
A ready-to-use executable script specifically designed for adding attractions to your "2025 Paris Trip Plans" Notion database. This script wraps `add-new-row.py` with pre-configured parameters for easy Paris trip planning.

## Quick Setup

### Option 1: Automated Setup (Recommended)
Run the initialization script to automatically set up the project:

```bash
# Clone the repository
git clone <repository-url>
cd movie-bot

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install Python dependencies
- Set executable permissions for scripts
- Check for required environment files
- Provide next steps guidance

### Option 2: Manual Setup

### 1. Install Dependencies

**Using Virtual Environment (Recommended):**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**System-wide Installation:**
```bash
pip install -r requirements.txt
```

**Make Scripts Executable:**
```bash
chmod +x setup.sh
chmod +x add-paris-attraction
```

### 2. Create Environment File
Create a `.env` file in the project root with your API keys:

```env
# Required for all scripts
NOTION_KEY=your_notion_integration_token

# Required for property-text-enricher.py
OPENAI_API_KEY=your_openai_api_key
SINGLE_FILL_PROMPT_ID=your_custom_prompt_id
SINGLE_FILL_PROMPT_VERSION=your_prompt_version
OPENAI_ENDPOINT=https://api.openai.com/v1/responses

# Required for photo-enricher.py
UNSPLASH_ACCESS_KEY=your_unsplash_access_key

# Required for add-new-row.py (database-specific custom prompts)
# Format: {DATABASE_NAME}_PROMPT_ID and {DATABASE_NAME}_PROMPT_VERSION
# Examples:
MY_MOVIES_PROMPT_ID=your_movies_prompt_id
MY_MOVIES_PROMPT_VERSION=your_movies_prompt_version
BOOK_REVIEWS_PROMPT_ID=your_books_prompt_id
BOOK_REVIEWS_PROMPT_VERSION=your_books_prompt_version
```

### 3. Get API Keys

- **Notion**: Create an integration at https://www.notion.so/my-integrations
- **OpenAI**: Get your API key at https://platform.openai.com/api-keys
- **Unsplash**: Create an app at https://unsplash.com/developers

### 4. Configure Notion Permissions
Make sure your Notion integration has access to your databases:
1. Go to your Notion database
2. Click the "..." menu (top right)
3. Select "Connect to" or "Add connections"
4. Find and select your integration
5. Grant "Read" and "Update" permissions

## Usage

### Property Text Enricher

Generate AI text content for database properties using custom prompts.

**Syntax:**
```bash
python property-text-enricher.py "Database Name" "Input Property" "Output Property" "Prompt Text"
```

**Options:**
- `--skip-existing`: Skip pages that already have text in the output property
- `--max-tokens`: Maximum tokens for AI response (default: 500)

**Examples:**

```bash
# Generate product descriptions
python property-text-enricher.py "Product Catalog" "Product Name" "Description" "Write a compelling 2-sentence product description that highlights key benefits:"

# Create social media captions
python property-text-enricher.py "Content Calendar" "Topic" "Caption" "Create an engaging Instagram caption with emojis and hashtags for this topic:"

# Generate meeting summaries
python property-text-enricher.py "Meeting Notes" "Agenda" "Summary" "Summarize the key discussion points and action items for this meeting agenda:"

# Create email subject lines
python property-text-enricher.py "Email Campaigns" "Campaign Topic" "Subject Line" "Write 3 compelling email subject lines for this campaign:"
```

**Supported Input Property Types:**
- Title properties
- Rich text properties
- Formula properties (that return text)

**Output Property Requirements:**
- Must be a rich text property in Notion

### Photo Enricher

Add relevant images from Unsplash to database pages based on text content.

**Syntax:**
```bash
python photo-enricher.py "Database Name" "Input Property" "Output Property"
```

**Options:**
- `--skip-existing`: Skip pages that already have images in the output property

**Examples:**

```bash
# Add photos to travel destinations
python photo-enricher.py "Travel Destinations" "Location" "Photo"

# Add product images to catalog
python photo-enricher.py "Product Catalog" "Product Name" "Image"

# Add restaurant photos
python photo-enricher.py "Restaurant Reviews" "Restaurant Name" "Photo"

# Add book cover images
python photo-enricher.py "Reading List" "Book Title" "Cover"
```

**Requirements:**
- Input property must contain text
- Output property must be a "Files & media" property type
- Images are sourced from Unsplash with proper attribution

### Add New Row

Create or update database entries using AI-generated structured data.

**Syntax:**
```bash
python add-new-row.py "Database Name" "Key Property" "Input Text"
```

**Examples:**

```bash
# Add a movie to your database
python add-new-row.py "My Movies" "Title" "Add Inception (2010) - a sci-fi thriller about dream manipulation directed by Christopher Nolan"

# Add a book review
python add-new-row.py "Book Reviews" "Title" "Add 1984 by George Orwell - dystopian novel about totalitarian surveillance, published 1949, 5 star rating"

# Add a restaurant entry
python add-new-row.py "Restaurants" "Name" "Add Joe's Pizza on Main Street - Italian cuisine, casual dining, great pepperoni pizza, 4 stars"

# Add a project task
python add-new-row.py "Project Tasks" "Task Name" "Create user authentication system - backend development, high priority, due next week"
```

**How it works:**
1. Uses database-specific custom prompts (configured in .env)
2. Converts natural language input into structured JSON
3. Maps JSON fields to Notion database properties
4. Creates new entries or updates existing ones (based on key property)

**Database-Specific Prompt Configuration:**
For each database you want to use with add-new-row.py, you need custom prompts:

```env
# For "My Movies" database
MY_MOVIES_PROMPT_ID=prompt_abc123
MY_MOVIES_PROMPT_VERSION=1

# For "Book Reviews" database  
BOOK_REVIEWS_PROMPT_ID=prompt_def456
BOOK_REVIEWS_PROMPT_VERSION=2
```

The script automatically converts database names to environment variable prefixes:
- "My Movies" → `MY_MOVIES_`
- "Book Reviews" → `BOOK_REVIEWS_`
- "Project Tasks (2024)" → `PROJECT_TASKS_2024_`

### Paris Trip Convenience Script

The `add-paris-attraction` script provides a simplified interface for adding attractions to your Paris trip plans.

**Syntax:**
```bash
./add-paris-attraction "attraction name"
```

**Examples:**
```bash
# Add famous landmarks
./add-paris-attraction "Eiffel Tower"
./add-paris-attraction "Arc de Triomphe"
./add-paris-attraction "Notre-Dame Cathedral"

# Add museums
./add-paris-attraction "Louvre Museum"
./add-paris-attraction "Musée d'Orsay"
./add-paris-attraction "Centre Pompidou"

# Add neighborhoods and areas
./add-paris-attraction "Montmartre District"
./add-paris-attraction "Latin Quarter"
./add-paris-attraction "Champs-Élysées"
```

**Requirements:**
- Must have a Notion database named "2025 Paris Trip Plans"
- Database must have an "ITEM" property (the key property for attractions)
- Requires the same environment variables as `add-new-row.py`
- Needs custom prompt configuration: `2025_PARIS_TRIP_PLANS_PROMPT_ID` and `2025_PARIS_TRIP_PLANS_PROMPT_VERSION`

**Error Handling:**
The script provides clear usage instructions when:
- No arguments are provided
- Too many arguments are provided
- The underlying Python script encounters errors

## Environment Variables Reference

| Variable | Purpose | Required For | Example |
|----------|---------|--------------|---------|
| `NOTION_KEY` | Notion integration token | All scripts | `secret_abc123...` |
| `OPENAI_API_KEY` | OpenAI API access | Text enricher, Add row | `sk-proj-abc123...` |
| `SINGLE_FILL_PROMPT_ID` | Custom prompt for text enricher | property-text-enricher.py | `prompt_abc123` |
| `SINGLE_FILL_PROMPT_VERSION` | Prompt version for text enricher | property-text-enricher.py | `1` |
| `OPENAI_ENDPOINT` | OpenAI API endpoint | Text enricher, Add row | `https://api.openai.com/v1/responses` |
| `UNSPLASH_ACCESS_KEY` | Unsplash API access | photo-enricher.py | `abc123def456...` |
| `{DB_NAME}_PROMPT_ID` | Database-specific prompt ID | add-new-row.py | `prompt_xyz789` |
| `{DB_NAME}_PROMPT_VERSION` | Database-specific prompt version | add-new-row.py | `1` |
| `2025_PARIS_TRIP_PLANS_PROMPT_ID` | Custom prompt for Paris trip script | add-paris-attraction | `prompt_paris123` |
| `2025_PARIS_TRIP_PLANS_PROMPT_VERSION` | Prompt version for Paris trip script | add-paris-attraction | `1` |

## Notion Property Type Support

### property-text-enricher.py
- **Input**: Title, Rich Text, Formula (text result)
- **Output**: Rich Text (required)

### photo-enricher.py
- **Input**: Title, Rich Text, Formula (text result)
- **Output**: Files & Media (required)

### add-new-row.py
Supports all common Notion property types:
- Title, Rich Text, Number, Checkbox
- Select, Multi-select, URL, Email, Phone
- Creates or updates based on key property match

## Troubleshooting

### Common Issues

**"Database not found"**
- Ensure your Notion integration has access to the database
- Check that the database name matches exactly (case-insensitive)

**"Property not found"**
- Verify property names match exactly (case-sensitive)
- Check that property types are compatible

**"No API key found"**
- Ensure all required environment variables are set in `.env`
- Check for typos in variable names

**"Custom prompt not found" (add-new-row.py)**
- Verify database name maps correctly to environment variables
- Ensure both `_PROMPT_ID` and `_PROMPT_VERSION` are set

### Getting Help

1. Run scripts with invalid arguments to see usage help
2. Check console output for detailed error messages
3. Verify API key permissions and quotas
4. Ensure database properties exist and have correct types

## Requirements

- Python 3.7+
- Active internet connection
- Valid API keys for required services
- Notion integration with proper database permissions 