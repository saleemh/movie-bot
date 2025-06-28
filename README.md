# Movie Bot

A Python application that integrates with The Movie Database (TMDB) API and Notion to manage movie information, including fetching movie posters and runtime data.

## Features

- 🔍 Search movies on TMDB API
- 🖼️ Fetch and update movie posters in Notion
- ⏱️ Retrieve and update movie runtime information
- 🔒 Secure environment variable management
- 📊 Notion database integration

## Prerequisites

- Python 3.7+
- TMDB API key
- Notion API key and database ID

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

## Usage

Run the main script:
```bash
python movie-bot.py
```

## Project Structure

- `movie-bot.py` - Main application script
- `load_env.py` - Environment variable loader
- `runtime.py` - Runtime fetching utilities
- `test_env.py` - Environment testing script

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License 