#!/usr/bin/env python3
"""
Script to demonstrate loading environment variables from .env file
"""

from dotenv import load_dotenv
import os

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
    
    # Display loaded environment variables
    print("\n📋 Loaded Environment Variables:")
    print("-" * 40)
    
    env_vars = [
        'NOTION_KEY',
        'NOTION_DB', 
        'TMDB_API_KEY',
        'OPENAI_API_KEY',
        'DEBUG',
        'ENVIRONMENT',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values for security
            if 'KEY' in var or 'SECRET' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
                print(f"{var}: {masked_value}")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: Not set")
    
    print("-" * 40)

def get_env_var(var_name, default=None):
    """Get an environment variable with optional default value"""
    return os.getenv(var_name, default)

if __name__ == "__main__":
    load_environment()
    
    # Example usage
    print(f"\n🔧 Example usage:")
    print(f"API Key available: {'Yes' if get_env_var('NOTION_KEY') else 'No'}")
    print(f"TMDB API Key available: {'Yes' if get_env_var('TMDB_KEY') else 'No'}")
    print(f"Debug mode: {get_env_var('DEBUG', 'False')}")
    print(f"Port: {get_env_var('PORT', '8000')}") 