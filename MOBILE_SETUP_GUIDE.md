# 📱 Mobile Setup Guide for Notion Row Creator

This guide will help you set up and run the Notion Row Creator script on your iPhone using Pythonista.

## 📋 Prerequisites

Before you start, make sure you have:
- ✅ iPhone or iPad
- ✅ Notion account with integration access
- ✅ OpenAI API account
- ✅ Active internet connection

## 🚀 Step-by-Step Setup

### Step 1: Install Pythonista

1. **Download Pythonista from the App Store**
   - Search for "Pythonista 3" in the App Store
   - Purchase and install the app ($9.99)
   - Open Pythonista once installed

### Step 2: Install Required Libraries

1. **Open Pythonista**
2. **Tap the gear icon (⚙️) in the top-right corner**
3. **Select "External Modules"**
4. **Install the following packages:**
   - Type `notion-client` and tap "Install"
   - Wait for installation to complete
   - Type `requests` and tap "Install" (if not already installed)

**Alternative method using pip:**
1. **Create a new Python file in Pythonista**
2. **Run this code once to install packages:**
```python
import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
try:
    install_package("notion-client")
    install_package("requests")
    print("✅ All packages installed successfully!")
except Exception as e:
    print(f"❌ Error installing packages: {e}")
```

### Step 3: Get Your API Keys

#### Notion API Key:
1. **Go to** https://www.notion.so/my-integrations
2. **Click "Create new integration"**
3. **Fill in the details:**
   - Name: "Mobile Movie Bot"
   - Workspace: Select your workspace
   - Type: Internal
4. **Click "Submit"**
5. **Copy the "Internal Integration Token"** (starts with `secret_`)
6. **Share your database with the integration:**
   - Go to your Notion database
   - Click "Share" in the top-right
   - Add your integration by name

#### OpenAI API Key:
1. **Go to** https://platform.openai.com/api-keys
2. **Click "Create new secret key"**
3. **Name it** "Mobile Notion Bot"
4. **Copy the API key** (starts with `sk-`)

#### OpenAI Custom Prompt Setup:
1. **Go to** https://platform.openai.com/prompts
2. **Create a custom prompt** for your database
3. **Note down the Prompt ID and Version** (you'll need these)

### Step 4: Add the Script to Pythonista

1. **Open Pythonista**
2. **Tap the "+" icon to create a new file**
3. **Name it** `notion_mobile.py`
4. **Copy and paste the entire `add-new-row-mobile.py` script** into this file
5. **Save the file** (⌘+S or tap "Done")

### Step 5: Configure Your API Keys

**Option A: Direct Configuration (Less Secure)**
1. **Edit the CONFIG dictionary** at the top of the script:
```python
CONFIG = {
    "NOTION_KEY": "secret_your_notion_token_here",
    "OPENAI_API_KEY": "sk-your_openai_key_here",
    "OPENAI_ENDPOINT": "https://api.openai.com/v1/responses"
}
```

**Option B: Secure Keychain Storage (Recommended)**
1. **Leave CONFIG empty** - the script will prompt you for keys
2. **Run the script once** - it will ask for your API keys
3. **Enter your keys** - they'll be saved securely in iOS Keychain
4. **Future runs** will automatically use saved keys

### Step 6: Test the Setup

1. **Run the script** by tapping the play button (▶️)
2. **Follow the prompts:**
   - Enter your database name
   - Enter the key property name (usually "Name" or "Title")
   - Enter some text to process
   - Enter your prompt configuration when asked
3. **Check your Notion database** to see if a new row was created

## 📱 How to Use the Script

### Running the Script:
1. **Open Pythonista**
2. **Find your** `notion_mobile.py` **file**
3. **Tap the play button** (▶️)
4. **Fill in the dialog boxes:**
   - **Database Name**: Exact name of your Notion database
   - **Key Property**: Property name to use as unique identifier
   - **Input Text**: Description of what you want to add

### Example Usage:
- **Database Name**: "My Movies"
- **Key Property**: "Name"
- **Input Text**: "The Matrix - a sci-fi movie about reality and simulation"

The AI will generate a JSON response and create/update a row in your database.

## 🔧 Troubleshooting

### ❌ "notion_client not installed"
- Go to Pythonista Settings > External Modules
- Install `notion-client`
- Restart Pythonista

### ❌ "Database not found"
- Check the exact spelling of your database name
- Make sure you've shared the database with your Notion integration
- Verify the integration has the correct permissions

### ❌ "API key errors"
- Verify your API keys are correct
- Check that your OpenAI account has credits
- Ensure your Notion integration has access to the workspace

### ❌ "Custom prompt not found"
- Make sure you've created a custom prompt in OpenAI
- Verify the Prompt ID and Version are correct
- The script will ask for these when you first run it

### ❌ Network errors
- Check your internet connection
- Try switching between WiFi and cellular data
- Some corporate networks may block API calls

## 🎯 Advanced Tips

### Creating Shortcuts:
1. **Open iOS Shortcuts app**
2. **Create a new shortcut**
3. **Add "Run Script" action**
4. **Select your Pythonista script**
5. **Add to home screen** for quick access

### Siri Integration:
1. **In Shortcuts, add "Siri Phrase"**
2. **Set phrase like "Add to Notion"**
3. **Now you can use voice commands**

### Widget Setup:
1. **Add Pythonista widget to home screen**
2. **Configure it to run your script**
3. **Quick access without opening the app**

## 🔐 Security Notes

- **Never share your API keys**
- **Use keychain storage** when possible
- **Keep your OpenAI account secure**
- **Monitor your API usage** for unexpected charges

## 📞 Support

If you encounter issues:
1. **Check the Pythonista console** for error messages
2. **Verify all prerequisites** are met
3. **Test each API key individually**
4. **Check Notion integration permissions**

The script includes detailed error messages to help diagnose problems.

## 🎉 You're Ready!

Once set up, you can quickly add entries to your Notion database from anywhere using your phone. The AI will intelligently parse your input and populate the appropriate fields in your database.

**Happy organizing! 📝✨** 