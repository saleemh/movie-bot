#!/bin/bash

# setup.sh - Project initialization script
# Run this script after cloning the repository to set up the project

echo "🚀 Setting up Notion Database Enhancement Scripts..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip and try again."
    exit 1
fi

echo "✅ pip found"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully in virtual environment"
    else
        echo "❌ Failed to install dependencies in virtual environment"
        exit 1
    fi
elif [ -d "venv" ]; then
    echo "📁 Found existing virtual environment in ./venv"
    echo "🔄 Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully in ./venv"
        echo "💡 To use the scripts, activate the virtual environment with: source venv/bin/activate"
    else
        echo "❌ Failed to install dependencies in virtual environment"
        exit 1
    fi
else
    echo "🐍 Setting up new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    
    echo "🔄 Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully in new virtual environment"
        echo "💡 To use the scripts, activate the virtual environment with: source venv/bin/activate"
    else
        echo "❌ Failed to install dependencies in virtual environment"
        exit 1
    fi
fi

# Make scripts executable
echo ""
echo "🔧 Setting up executable permissions for scripts..."

# Make the Paris attraction script executable
if [ -f "add-paris-attraction" ]; then
    chmod +x add-paris-attraction
    echo "✅ Made add-paris-attraction executable"
else
    echo "⚠️  add-paris-attraction script not found"
fi

# Make this setup script executable for future use
chmod +x setup.sh
echo "✅ Made setup.sh executable"

# Check for .env file
echo ""
echo "🔍 Checking for environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  .env file not found"
    echo "   You'll need to create a .env file with your API keys."
    echo "   See the README.md for detailed instructions."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Create a .env file with your API keys (see README.md)"
echo "   2. Configure your Notion integration permissions"
echo "   3. Test the scripts with your databases"
echo ""
echo "💡 Quick start with Paris trip script:"
echo "   ./add-paris-attraction \"Eiffel Tower\""
echo "" 