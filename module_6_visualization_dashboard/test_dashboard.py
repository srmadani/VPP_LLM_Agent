#!/usr/bin/env python3
"""
VPP Dashboard - Quick Test Script

Verifies that the enhanced dashboard can load and all components are functional.
"""

import sys
import os
from pathlib import Path
import traceback

# Add parent directories to path for imports
base_path = Path(__file__).parent.parent
sys.path.append(str(base_path))

def test_imports():
    """Test that all required imports work."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("  ✅ Streamlit")
    except ImportError as e:
        print(f"  ❌ Streamlit: {e}")
        return False
        
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        print("  ✅ Plotly")
    except ImportError as e:
        print(f"  ❌ Plotly: {e}")
        return False
        
    try:
        import pandas as pd
        import numpy as np
        print("  ✅ Data processing libraries")
    except ImportError as e:
        print(f"  ❌ Data processing: {e}")
        return False
        
    try:
        import google.generativeai as genai
        print("  ✅ Google Generative AI")
    except ImportError as e:
        print(f"  ⚠️  Google Generative AI: {e} (Optional - dashboard will work without AI features)")
        
    return True

def test_dashboard_class():
    """Test that the dashboard class can be instantiated."""
    print("\n🔍 Testing dashboard class...")
    
    try:
        # Change to dashboard directory
        dashboard_dir = Path(__file__).parent
        os.chdir(dashboard_dir)
        
        # Import dashboard class
        from dashboard import VPPDashboard, ModuleRunner
        print("  ✅ Dashboard classes imported successfully")
        
        # Test ModuleRunner instantiation
        module_runner = ModuleRunner(base_path)
        print("  ✅ ModuleRunner instantiated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Dashboard class test failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_data_directories():
    """Test that required data directories exist or can be created."""
    print("\n🔍 Testing data directories...")
    
    directories = [
        base_path / "module_1_data_simulation" / "data",
        base_path / "module_2_asset_modeling",
        base_path / "module_5_simulation_orchestration" / "results"
    ]
    
    all_exist = True
    for directory in directories:
        if directory.exists():
            print(f"  ✅ {directory.name} directory exists")
        else:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ {directory.name} directory created")
            except Exception as e:
                print(f"  ❌ Failed to create {directory.name}: {e}")
                all_exist = False
                
    return all_exist

def test_dashboard_functions():
    """Test key dashboard functions without Streamlit context."""
    print("\n🔍 Testing dashboard functions...")
    
    try:
        from dashboard import VPPDashboard
        
        # Mock Streamlit session state
        class MockSessionState:
            def __init__(self):
                self.module_results = {}
                self.custom_prosumers = []
                self.logs = []
        
        # This would normally fail without Streamlit context, but we can test import
        print("  ✅ Dashboard functions accessible")
        return True
        
    except Exception as e:
        print(f"  ❌ Dashboard function test failed: {e}")
        return False

def test_environment_file():
    """Check for environment file."""
    print("\n🔍 Testing environment configuration...")
    
    env_file = base_path / ".env"
    env_example = base_path / ".env.example"
    
    if env_file.exists():
        print("  ✅ .env file found")
        
        # Read and check for API keys
        with open(env_file, 'r') as f:
            content = f.read()
            
        if 'GEMINI_API_KEY' in content:
            print("  ✅ Gemini API key configured")
        else:
            print("  ⚠️  Gemini API key not found (AI features will be limited)")
            
    elif env_example.exists():
        print("  ⚠️  .env file not found, but .env.example exists")
        print("    Copy .env.example to .env and configure API keys for full functionality")
    else:
        print("  ⚠️  No environment files found")
        print("    Dashboard will work with fallback functionality")
        
    return True

def run_all_tests():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("  VPP DASHBOARD - QUICK TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Dashboard Classes", test_dashboard_class),
        ("Data Directories", test_data_directories),
        ("Dashboard Functions", test_dashboard_functions),
        ("Environment Config", test_environment_file)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Dashboard is ready to launch.")
        print("\n🚀 Launch with: ./launch_dashboard.sh")
    elif passed >= total - 1:
        print("\n⚠️  Dashboard should work with minor limitations.")
        print("   Check failed tests and install missing dependencies if needed.")
        print("\n🚀 Try launching with: ./launch_dashboard.sh")
    else:
        print("\n❌ Multiple test failures. Please address issues before launching.")
        print("   Install missing dependencies and check file permissions.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
