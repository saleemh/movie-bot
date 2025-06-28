#!/usr/bin/env python3
"""
Test script to verify the actual environment variables in .env file
"""

from dotenv import load_dotenv
import os

def test_environment():
    """Test loading and displaying actual environment variables"""
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
    
    # Check for the actual variables in your .env file
    actual_vars = [
        'NOTION_KEY',
        'NOTION_DB', 
        'TMDB_KEY'
    ]
    
    print("\n📋 Actual Environment Variables Found:")
    print("-" * 40)
    
    for var in actual_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values for security
            if 'KEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
                print(f"{var}: {masked_value}")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: Not set")
    
    print("-" * 40)
    
    # Test if we can access the variables
    print(f"\n🔧 Access Test:")
    print(f"NOTION_KEY available: {'Yes' if os.getenv('NOTION_KEY') else 'No'}")
    print(f"NOTION_DB available: {'Yes' if os.getenv('NOTION_DB') else 'No'}")
    print(f"TMDB_KEY available: {'Yes' if os.getenv('TMDB_KEY') else 'No'}")
    
    # Show the actual values (be careful with this in production!)
    print(f"\n🔑 Actual Values (for testing only):")
    print(f"NOTION_KEY: {os.getenv('NOTION_KEY', 'Not set')}")
    print(f"NOTION_DB: {os.getenv('NOTION_DB', 'Not set')}")
    print(f"TMDB_KEY: {os.getenv('TMDB_KEY', 'Not set')}")

if __name__ == "__main__":
    test_environment() 