#!/bin/bash

# VPP Dashboard Launch Script
# This script launches the Streamlit dashboard for the VPP LLM Agent

echo "🚀 Starting VPP LLM Agent Dashboard..."
echo "========================================="

# Check if we're in the right directory
if [ ! -f "dashboard.py" ]; then
    echo "❌ Error: dashboard.py not found"
    echo "Please run this script from the module_6_visualization_dashboard directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    source ../venv/bin/activate
fi

# Check if required files exist
if [ ! -f "../module_5_simulation_orchestration/results/simulation_results.csv" ]; then
    echo "❌ Error: Simulation results not found"
    echo "Please run Module 5 simulation first"
    exit 1
fi

# Launch dashboard
echo "✅ All checks passed"
echo "🌐 Launching dashboard at http://localhost:8501"
echo "📊 Loading simulation data..."
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo "========================================="

# Start Streamlit
streamlit run dashboard.py
