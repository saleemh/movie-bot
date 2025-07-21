#!/usr/bin/env python3
"""
Mobile Diagnostics Script for Notion Row Creator
This script helps diagnose common issues with the mobile setup.
"""

import sys
import os

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"🔍 {title}")
    print("=" * 50)

def test_python_version():
    """Test Python version compatibility."""
    print_header("Python Version Check")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version too old (need 3.7+)")
        return False

def test_pythonista_modules():
    """Test if Pythonista-specific modules are available."""
    print_header("Pythonista Modules Check")
    
    try:
        import dialogs
        print("✅ dialogs module available")
        dialog_available = True
    except ImportError:
        print("❌ dialogs module not available")
        dialog_available = False
    
    try:
        import keychain
        print("✅ keychain module available")
        keychain_available = True
    except ImportError:
        print("❌ keychain module not available")
        keychain_available = False
    
    if dialog_available and keychain_available:
        print("✅ Running in Pythonista environment")
        return True
    else:
        print("⚠️  Not running in Pythonista (desktop mode)")
        return False

def test_required_libraries():
    """Test if required external libraries are installed."""
    print_header("Required Libraries Check")
    
    libraries = {
        'requests': False,
        'json': False,
        'os': False,
        'sys': False,
        'notion_client': False
    }
    
    # Test built-in libraries
    try:
        import requests
        libraries['requests'] = True
        print("✅ requests library available")
    except ImportError:
        print("❌ requests library not available")
    
    try:
        import json
        libraries['json'] = True
        print("✅ json library available")
    except ImportError:
        print("❌ json library not available")
    
    try:
        import os
        libraries['os'] = True
        print("✅ os library available")
    except ImportError:
        print("❌ os library not available")
    
    try:
        import sys
        libraries['sys'] = True
        print("✅ sys library available")
    except ImportError:
        print("❌ sys library not available")
    
    # Test external libraries
    try:
        from notion_client import Client
        libraries['notion_client'] = True
        print("✅ notion_client library available")
    except ImportError:
        print("❌ notion_client library not available")
        print("   📱 To install: Go to Pythonista Settings > External Modules > Install 'notion-client'")
    
    all_available = all(libraries.values())
    
    if all_available:
        print("✅ All required libraries are available")
    else:
        missing = [lib for lib, available in libraries.items() if not available]
        print(f"❌ Missing libraries: {', '.join(missing)}")
    
    return all_available

def test_internet_connection():
    """Test internet connectivity."""
    print_header("Internet Connection Check")
    
    try:
        import requests
        response = requests.get("https://httpbin.org/status/200", timeout=10)
        if response.status_code == 200:
            print("✅ Internet connection working")
            return True
        else:
            print(f"❌ Internet connection issue (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Internet connection failed: {e}")
        print("   🔧 Try switching between WiFi and cellular data")
        return False

def test_api_endpoints():
    """Test if API endpoints are reachable."""
    print_header("API Endpoints Check")
    
    endpoints = {
        "OpenAI API": "https://api.openai.com/v1/models",
        "Notion API": "https://api.notion.com/v1/users"
    }
    
    results = {}
    
    try:
        import requests
        
        for name, url in endpoints.items():
            try:
                # Don't send auth headers, just test reachability
                response = requests.get(url, timeout=10)
                if response.status_code in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                    print(f"✅ {name} reachable")
                    results[name] = True
                else:
                    print(f"❌ {name} unreachable (status: {response.status_code})")
                    results[name] = False
            except Exception as e:
                print(f"❌ {name} failed: {e}")
                results[name] = False
    
    except ImportError:
        print("❌ requests library not available for testing")
        return False
    
    return all(results.values())

def test_keychain_access():
    """Test keychain functionality if available."""
    print_header("Keychain Access Check")
    
    try:
        import keychain
        
        # Test write and read
        test_key = "notion_mobile_test"
        test_service = "notion_mobile_diagnostics"
        test_value = "test_value_123"
        
        try:
            # Try to write
            keychain.set_password(test_service, test_key, test_value)
            print("✅ Keychain write access working")
            
            # Try to read
            retrieved = keychain.get_password(test_service, test_key)
            if retrieved == test_value:
                print("✅ Keychain read access working")
                
                # Clean up
                keychain.delete_password(test_service, test_key)
                print("✅ Keychain cleanup successful")
                return True
            else:
                print("❌ Keychain read returned wrong value")
                return False
                
        except Exception as e:
            print(f"❌ Keychain access failed: {e}")
            return False
            
    except ImportError:
        print("⚠️  Keychain not available (not running in Pythonista)")
        return True  # Not an error if not in Pythonista

def test_dialog_functionality():
    """Test dialog functionality if available."""
    print_header("Dialog Functionality Check")
    
    try:
        import dialogs
        print("✅ dialogs module available")
        
        # We won't actually show a dialog in diagnostics, just test import
        print("✅ Dialog functionality should work")
        return True
        
    except ImportError:
        print("⚠️  dialogs not available (not running in Pythonista)")
        return True  # Not an error if not in Pythonista

def run_full_diagnostics():
    """Run all diagnostic tests."""
    print("🏥 Notion Mobile Diagnostics")
    print("This script will test your setup for common issues.")
    
    tests = [
        ("Python Version", test_python_version),
        ("Pythonista Modules", test_pythonista_modules),
        ("Required Libraries", test_required_libraries),
        ("Internet Connection", test_internet_connection),
        ("API Endpoints", test_api_endpoints),
        ("Keychain Access", test_keychain_access),
        ("Dialog Functionality", test_dialog_functionality)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print_header("Diagnostics Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
        print("\n🔧 Common solutions:")
        print("   • Install missing libraries via Pythonista Settings > External Modules")
        print("   • Check your internet connection")
        print("   • Restart Pythonista and try again")
        print("   • Make sure you're running this in Pythonista app")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_full_diagnostics()
        if not success:
            print("\n📖 For detailed setup instructions, see MOBILE_SETUP_GUIDE.md")
    except KeyboardInterrupt:
        print("\n👋 Diagnostics cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during diagnostics: {e}")
        print("Please try running the diagnostics again or check your setup manually.") 