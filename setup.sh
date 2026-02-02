#!/bin/bash

echo "========================================================================"
echo "Education RAG System - Quick Setup Script"
echo "========================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ All dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your ANTHROPIC_API_KEY"
    echo "   Get your API key from: https://console.anthropic.com/"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Run tests
echo "========================================================================"
echo "Running system tests..."
echo "========================================================================"
echo ""

python scripts/test_system.py

echo ""
echo "========================================================================"
echo "Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "2. Put your PDF textbooks in the ./uploads/ directory"
echo "3. Run: python scripts/main_pipeline.py --pdf uploads/your_file.pdf --class 8 --subject Math"
echo "4. Or start the API server: python api_server.py"
echo ""
echo "For detailed instructions, see README.md"
echo ""
echo "========================================================================"
