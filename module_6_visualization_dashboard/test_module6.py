"""
Test Module 6: Visualization Dashboard

This script validates the dashboard functionality and data loading capabilities.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent / "module_2_asset_modeling"))

def test_data_loading():
    """Test that all required data files can be loaded."""
    print("Testing data loading...")
    
    base_path = Path(__file__).parent.parent
    
    # Test simulation results
    results_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_results.csv"
    assert results_path.exists(), f"Simulation results not found: {results_path}"
    
    results_df = pd.read_csv(results_path)
    assert not results_df.empty, "Simulation results are empty"
    print(f"✅ Loaded simulation results: {len(results_df)} timesteps")
    
    # Test simulation summary
    summary_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_summary.json"
    assert summary_path.exists(), f"Simulation summary not found: {summary_path}"
    
    with open(summary_path, 'r') as f:
        summary = json.load(f)
    assert summary, "Simulation summary is empty"
    print(f"✅ Loaded simulation summary: {len(summary)} metrics")
    
    # Test market data
    market_path = base_path / "module_1_data_simulation" / "data" / "market_data.csv"
    assert market_path.exists(), f"Market data not found: {market_path}"
    
    market_df = pd.read_csv(market_path)
    assert not market_df.empty, "Market data is empty"
    print(f"✅ Loaded market data: {len(market_df)} records")
    
    # Test LLM parser availability
    try:
        from llm_parser import LLMProsumerParser
        parser = LLMProsumerParser()
        print("✅ LLM parser available")
    except ImportError as e:
        print(f"⚠️  LLM parser not available: {e}")
    except Exception as e:
        print(f"⚠️  LLM parser error: {e}")
    
    return True

def test_dashboard_components():
    """Test dashboard component initialization."""
    print("\nTesting dashboard components...")
    
    try:
        # Import streamlit components (without running the app)
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        print("✅ All dashboard dependencies available")
    except ImportError as e:
        print(f"❌ Missing dashboard dependency: {e}")
        return False
    
    return True

def test_key_metrics():
    """Test that key metrics are available in the data."""
    print("\nTesting key metrics availability...")
    
    base_path = Path(__file__).parent.parent
    summary_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_summary.json"
    
    with open(summary_path, 'r') as f:
        summary = json.load(f)
    
    required_metrics = [
        'total_timesteps',
        'agentic_total_profit',
        'centralized_total_profit',
        'agentic_avg_satisfaction',
        'centralized_avg_satisfaction',
        'satisfaction_advantage_percent',
        'agentic_success_rate',
        'centralized_success_rate'
    ]
    
    missing_metrics = []
    for metric in required_metrics:
        if metric not in summary:
            missing_metrics.append(metric)
    
    if missing_metrics:
        print(f"❌ Missing metrics: {missing_metrics}")
        return False
    else:
        print("✅ All required metrics available")
    
    # Display key metrics
    print(f"  - Total Timesteps: {summary['total_timesteps']}")
    print(f"  - Agentic Profit: ${summary['agentic_total_profit']:.2f}")
    print(f"  - Centralized Profit: ${summary['centralized_total_profit']:.2f}")
    print(f"  - Satisfaction Advantage: {summary['satisfaction_advantage_percent']:.1f}%")
    
    return True

def run_all_tests():
    """Run all dashboard tests."""
    print("=" * 60)
    print("VPP DASHBOARD VALIDATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Data Loading", test_data_loading),
        ("Dashboard Components", test_dashboard_components),
        ("Key Metrics", test_key_metrics)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Dashboard is ready to run!")
        print("Run with: streamlit run dashboard.py")
    else:
        print("\n⚠️  Fix failing tests before running dashboard.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
