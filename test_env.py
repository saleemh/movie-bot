#!/usr/bin/env python3
"""
Test script to verify the required environment variables for movie-bot
"""

import os
from dotenv import load_dotenv
import sys

def test_environment():
    """Test loading and displaying required environment variables"""
    load_dotenv()
    required_vars = [
        'NOTION_KEY',
        'NOTION_DB',
        'TMDB_KEY'
    ]
    print("\n📋 Checking required environment variables:")
    print("-" * 40)
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set.")
        else:
            print(f"❌ {var} is NOT set!")
            all_ok = False
    print("-" * 40)
    if all_ok:
        print("🎉 All required environment variables are set!")
        sys.exit(0)
    else:
        print("⚠️  One or more required environment variables are missing.")
        sys.exit(1)

if __name__ == "__main__":
    test_environment() 