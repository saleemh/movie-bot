# Movie Bot, Photo Enricher, and Property Text Enricher

This repository contains scripts for enriching Notion databases with movie data, images, and AI-generated text.

## Scripts

### movie-bot.py
Enriches a Notion movie database with posters, runtime, synopsis, and year information from TMDB.

### photo-enricher.py
Enriches any Notion database with images based on text properties using the Unsplash API.

### property-text-enricher.py
Enriches any Notion database with AI-generated text based on custom prompts using OpenAI's API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
NOTION_KEY=your_notion_integration_token
TMDB_KEY=your_tmdb_api_key
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_ENDPOINT=https://api.openai.com/v1/chat/completions
```

### Getting API Keys

- **Notion**: Create an integration at https://www.notion.so/my-integrations
- **TMDB**: Sign up at https://www.themoviedb.org/settings/api
- **Unsplash**: Create an app at https://unsplash.com/developers
- **OpenAI**: Get your API key at https://platform.openai.com/api-keys

## Usage

### Movie Bot
```bash
python movie-bot.py
```

### Photo Enricher
```bash
python photo-enricher.py "Database Name" "Input Property" "Output Property"
```

**Options:**
- `--skip-existing`: Skip pages that already have images in the output property

**Example:**
```bash
python photo-enricher.py "Travel Destinations" "Location" "Photo"
```

This will:
1. Find the "Travel Destinations" database
2. Read the "Location" property from each page
3. Search for relevant images on Unsplash
4. Add the images to the "Photo" property

### Property Text Enricher
```bash
python property-text-enricher.py "Database Name" "Input Property" "Output Property" "Your Prompt"
```

**Options:**
- `--skip-existing`: Skip pages that already have text in the output property
- `--max-tokens`: Maximum tokens for AI response (default: 500)

**Example:**
```bash
python property-text-enricher.py "Product Catalog" "Product Name" "Marketing Copy" "Write a compelling 2-sentence marketing description for this product that highlights its key benefits:"
```

This will:
1. Find the "Product Catalog" database
2. Read the "Product Name" property from each page
3. Send the product name + prompt to OpenAI
4. Add the generated marketing copy to the "Marketing Copy" property

## Property Types for Text Enricher

### Input Property (can be any of these):
- **Title** - Page title
- **Text** - Simple text property
- **Formula** - Computed text values

### Output Property (must be):
- **Text** - Rich text property in Notion

## Prompt Writing Guidelines

For best results with the Property Text Enricher:

### ✅ Good Prompts:
- **Be specific**: "Write a 50-word product description that emphasizes benefits"
- **Set format**: "Create a bullet-point list of 3 key features"
- **Include constraints**: "Summarize in 2 sentences, professional tone"
- **Specify style**: "Write in a casual, friendly tone for social media"

### 📝 Example Prompts:
```
"Summarize this location in 1-2 sentences for a travel brochure:"
"Create 3 hashtags for this product for Instagram marketing:"
"Write a professional email subject line for this topic:"
"Generate a brief company bio (50 words max) based on this description:"
"Create a compelling call-to-action for this service:"
```

### ⚠️ Notion Text Property Limits:
- Maximum 2,000 characters per text property
- Use `--max-tokens` to control output length
- Consider breaking long content into multiple properties

## Environment Variables

| Variable | Description | Required For | Default |
|----------|-------------|--------------|---------|
| `NOTION_KEY` | Notion integration token | All scripts | - |
| `TMDB_KEY` | The Movie Database API key | movie-bot.py | - |
| `UNSPLASH_ACCESS_KEY` | Unsplash API access key | photo-enricher.py | - |
| `OPENAI_API_KEY` | OpenAI API key | property-text-enricher.py | - |
| `OPENAI_MODEL` | OpenAI model to use | property-text-enricher.py | gpt-3.5-turbo |
| `OPENAI_ENDPOINT` | OpenAI API endpoint | property-text-enricher.py | https://api.openai.com/v1/chat/completions |

## Requirements

- Python 3.7+
- Active internet connection
- Proper API permissions for your Notion workspace
- Valid API keys for the services you want to use 