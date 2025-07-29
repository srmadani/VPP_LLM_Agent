#!/bin/bash

# VPP Agent PoC - Module 1 Environment Setup Script
# This script sets up the shared Python environment for all modules

echo "🚀 VPP Agent Module 1 - Environment Setup"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Navigate to parent directory for shared environment
cd ..

# Create virtual environment in parent directory
echo "📦 Creating shared virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing dependencies..."
pip install -r module_1_data_simulation/requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found"
    echo "Please copy .env.example to .env and add your API keys:"
    echo ""
    echo "cp .env.example .env"
    echo ""
    echo "Then edit .env with your actual API keys:"
    echo "• NREL_API_KEY - Get from: https://developer.nrel.gov/signup/"
    echo "• GRIDSTATUS_API_KEY - Get from: https://www.gridstatus.io/"
    echo "• GEMINI_API_KEY - Get from: https://ai.google.dev/"
else
    echo "✅ Found .env file with API keys"
fi

# Return to module directory
cd module_1_data_simulation

# Create data directory if it doesn't exist
mkdir -p data
mkdir -p data/load_profiles

echo ""
echo "✅ Shared environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source ../venv/bin/activate"
echo "2. Run data collection: python collect_data.py"
echo "3. Run validation tests: python test_data.py"
echo "4. Generate dashboard: python create_dashboard.py"
echo ""
echo "For detailed instructions, see README.md"
