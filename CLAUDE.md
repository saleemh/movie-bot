# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that provides scripts for enhancing Notion databases with AI-generated content, images, and automated data entry using various APIs. The project consists of multiple specialized scripts for different database enhancement tasks.

This project is licensed under the MIT License - see the LICENSE file for details.

## Core Scripts and Architecture

### Main Scripts
- `property-text-enricher.py` - Enriches Notion database pages with AI-generated text using OpenAI's Responses API
- `photo-enricher.py` - Automatically adds relevant images to Notion database pages by searching Unsplash
- `add-new-row.py` - Creates new Notion database entries or updates existing ones using AI-generated structured data
- `movie-bot.py` - Specialized script for enriching movie databases with TMDB API data (posters, runtime, synopsis, year)
- `tv-show-bot.py` - Similar to movie-bot but for TV shows
- `update-ranking.py` - Updates ranking/sorting information in databases

### Support Scripts
- `load_env.py` - Environment variable loading utility with security masking
- `test_env.py` - Environment variable validation and testing

## Dependencies and Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Environment Variables
Create a `.env` file with the following variables:

```env
# Required for all scripts
NOTION_KEY=your_notion_integration_token

# Required for property-text-enricher.py and add-new-row.py
OPENAI_API_KEY=your_openai_api_key
SINGLE_FILL_PROMPT_ID=your_custom_prompt_id
SINGLE_FILL_PROMPT_VERSION=your_prompt_version
OPENAI_ENDPOINT=https://api.openai.com/v1/responses

# Required for photo-enricher.py
UNSPLASH_ACCESS_KEY=your_unsplash_access_key

# Required for movie-bot.py
TMDB_KEY=your_tmdb_api_key
NOTION_DB=your_notion_database_id

# Required for add-new-row.py (database-specific custom prompts)
# Format: {DATABASE_NAME}_PROMPT_ID and {DATABASE_NAME}_PROMPT_VERSION
```

## Common Development Commands

### Running Scripts
```bash
# Property text enricher
python property-text-enricher.py "Database Name" "Input Property" "Output Property" "Prompt Text"

# Photo enricher
python photo-enricher.py "Database Name" "Input Property" "Output Property"

# Add new row
python add-new-row.py "Database Name" "Key Property" "Input Text"

# Movie bot (runs automatically on all movies in configured database)
python movie-bot.py

# Test environment setup
python test_env.py

# Load and display environment variables
python load_env.py
```

### Testing Environment Setup
```bash
python test_env.py
```

## Key Architecture Patterns

### Environment Variable Management
- All scripts use `python-dotenv` to load `.env` files
- Environment variables are loaded at script startup with `load_dotenv()`
- Sensitive values are masked when displayed for security

### Notion API Integration
- Uses `notion-client` library for all Notion interactions
- Database searches are performed by title matching (case-insensitive)
- Property type validation ensures data is formatted correctly for each Notion property type
- Scripts skip processing items that already have data (configurable with `--skip-existing`)

### External API Integrations
- **OpenAI Responses API**: Used for AI-generated content with custom prompts
- **TMDB API**: Movie and TV show metadata retrieval
- **Unsplash API**: Image search and retrieval

### Error Handling and Logging
- Scripts provide verbose console output with emoji indicators
- Progress tracking shows current item being processed
- API errors are caught and displayed with helpful messages
- Missing environment variables are detected early with clear setup instructions

### Database-Specific Custom Prompts
For `add-new-row.py`, custom prompts are configured per database:
- Database names are normalized to environment variable format (uppercase, special chars to underscores)
- Example: "My Movies" → `MY_MOVIES_PROMPT_ID`, `MY_MOVIES_PROMPT_VERSION`

## Important Notes

- Scripts are designed to be idempotent - they skip items that already have data
- All scripts validate Notion database access and property existence before processing
- API rate limiting is handled gracefully with appropriate error messages
- No test framework is currently configured - scripts include basic validation and error handling