# Movie Bot

A Python application that integrates with The Movie Database (TMDB) API and Notion to automatically enrich movie databases with comprehensive information including posters, runtime, and synopses.

## Features

- 🔍 **Smart Movie Search**: Search movies on TMDB API with title and year matching
- 🖼️ **Poster Management**: Fetch and update high-quality movie posters in Notion
- ⏱️ **Runtime Data**: Retrieve and update movie runtime information
- 📚 **Synopsis Support**: Fetch and store movie descriptions/synopses
- 🔒 **Smart Updates**: Skip processing for already populated data
- 📊 **Verbose Logging**: Detailed progress tracking and status messages
- 🔒 **Secure Environment**: Environment variable management for API keys
- 📚 **Batch Processing**: Process entire Notion databases efficiently

## Prerequisites

- Python 3.7+
- TMDB API key ([Get one here](https://www.themoviedb.org/settings/api))
- Notion API key and database ID ([Setup guide](https://developers.notion.com/docs/create-a-notion-integration))

## Installation

1. Clone the repository:
```bash
git clone <your-github-repo-url>
cd movie-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration

## Environment Variables

Create a `.env` file with the following variables:

```env
TMDB_KEY=your_tmdb_api_key_here
NOTION_KEY=your_notion_api_key_here
NOTION_DB=your_notion_database_id_here

# Optional Configuration
DEBUG=False
ENVIRONMENT=production
PORT=8000
```

## Notion Database Setup

Your Notion database should have the following properties:

- **Name** (Title) - Movie title
- **Year** (Number) - Release year
- **Poster** (Files & Media) - Movie poster images
- **Runtime** (Number) - Movie length in minutes
- **Synopsis** (Text) - Movie description

## Usage

Run the main script:
```bash
python movie-bot.py
```

### Sample Output

## Project Structure

- `movie-bot.py` - Main application script
- `load_env.py` - Environment variable loader

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License 