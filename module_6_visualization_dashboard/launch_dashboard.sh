#!/bin/bash

# VPP Comprehensive Dashboard Launch Script
# This script launches the enhanced Streamlit dashboard for the VPP LLM Agent

echo "⚡ Starting VPP LLM Agent - Comprehensive Dashboard..."
echo "==========================================================="

# Check if we're in the right directory
if [ ! -f "dashboard.py" ]; then
    echo "❌ Error: dashboard.py not found"
    echo "Please run this script from the module_6_visualization_dashboard directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ required (found: $python_version)"
    echo "Please upgrade Python to 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -d "../venv" ]; then
    echo "🔄 Activating virtual environment..."
    source ../venv/bin/activate || {
        echo "❌ Failed to activate virtual environment"
        echo "Creating new virtual environment..."
        python3 -m venv ../venv
        source ../venv/bin/activate
    }
elif [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment detected. Creating one..."
    python3 -m venv ../venv
    source ../venv/bin/activate
fi

# Check and install requirements
echo "📦 Checking dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Install/upgrade requirements if needed
pip install -r requirements.txt --quiet || {
    echo "❌ Failed to install requirements"
    echo "Trying with --user flag..."
    pip install -r requirements.txt --user --quiet
}

# Check for environment file
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "../.env.example" ]; then
        cp ../.env.example ../.env
        echo "📝 Please edit ../.env with your API keys for full functionality"
    else
        echo "ℹ️  Dashboard will work with fallback data (no API keys required)"
    fi
fi

# Check for data directories and create if needed
echo "🗂️  Checking data directories..."
mkdir -p ../module_1_data_simulation/data/load_profiles
mkdir -p ../module_2_asset_modeling
mkdir -p ../module_5_simulation_orchestration/results

# Check for basic data files and provide guidance
data_status=""
if [ ! -f "../module_1_data_simulation/data/market_data.csv" ]; then
    data_status="${data_status}• Market data missing - Run Module 1 to collect\n"
fi

if [ ! -f "../module_2_asset_modeling/fleet_summary.csv" ]; then
    data_status="${data_status}• Fleet data missing - Run Module 2 to generate\n"
fi

if [ ! -f "../module_5_simulation_orchestration/results/simulation_results.csv" ]; then
    data_status="${data_status}• Simulation results missing - Run Module 5 for full analysis\n"
fi

if [ -n "$data_status" ]; then
    echo "ℹ️  Data Status:"
    echo -e "$data_status"
    echo "✅ Dashboard will work with available data and allow module testing"
else
    echo "✅ All data files found - Full functionality available"
fi

# Check if port 8501 is available
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8501 is already in use. Trying port 8502..."
    PORT=8502
else
    PORT=8501
fi

# Launch dashboard with enhanced features
echo ""
echo "🚀 All checks passed - Launching comprehensive dashboard"
echo "=========================================================="
echo "🌐 Dashboard URL: http://localhost:$PORT"
echo "📊 Features Available:"
echo "   • Module Testing & Validation"
echo "   • Prosumer Fleet Management"
echo "   • Performance Analysis & Visualization"
echo "   • Market Data Analysis"
echo "   • Real-time Logs & Monitoring"
echo "   • AI-Powered Insights (if API key configured)"
echo ""
echo "📱 Mobile-friendly responsive design"
echo "💾 Export capabilities for all data and results"
echo ""
echo "⌨️  Press Ctrl+C to stop the dashboard"
echo "=========================================================="

# Export environment variables for the session
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../"

# Start Streamlit with optimized settings
if [ "$PORT" = "8502" ]; then
    streamlit run dashboard.py --server.port 8502 \
        --theme.base "light" \
        --theme.primaryColor "#1f77b4" \
        --theme.backgroundColor "#ffffff" \
        --theme.secondaryBackgroundColor "#f0f2f6" \
        --server.maxUploadSize 200
else
    streamlit run dashboard.py \
        --theme.base "light" \
        --theme.primaryColor "#1f77b4" \
        --theme.backgroundColor "#ffffff" \
        --theme.secondaryBackgroundColor "#f0f2f6" \
        --server.maxUploadSize 200
fi
