#!/usr/bin/env python3
"""
Quick test to verify Module 5 path fix works correctly
"""

import sys
import os
from pathlib import Path

def test_module5_fix():
    """Test that Module 5 works after the path fix."""
    print("Testing Module 5 path fix...")
    
    try:
        # Add paths like the dashboard does
        base_path = Path(__file__).parent
        module_5_path = str(base_path / 'module_5_simulation_orchestration')
        module_4_path = str(base_path / 'module_4_negotiation_logic')
        module_3_path = str(base_path / 'module_3_agentic_framework')
        module_2_path = str(base_path / 'module_2_asset_modeling')
        module_1_path = str(base_path / 'module_1_data_simulation')
        
        for path in [module_5_path, module_4_path, module_3_path, module_2_path, module_1_path]:
            if path in sys.path:
                sys.path.remove(path)
            sys.path.insert(0, path)
        
        # Import and test
        from simulation import VPPSimulationOrchestrator
        
        print("✅ Import successful")
        
        # Test with correct data path (like the dashboard now does)
        module_1_data_path = str(base_path / 'module_1_data_simulation' / 'data')
        print(f"Using data path: {module_1_data_path}")
        print(f"Data path exists: {os.path.exists(module_1_data_path)}")
        
        # Check if market_data.csv exists
        market_file = os.path.join(module_1_data_path, 'market_data.csv')
        print(f"Market data file: {market_file}")
        print(f"Market data exists: {os.path.exists(market_file)}")
        
        # Initialize orchestrator with explicit path
        orchestrator = VPPSimulationOrchestrator(data_path=module_1_data_path)
        print("✅ VPPSimulationOrchestrator initialized successfully!")
        
        # Check that market data loaded
        print(f"✅ Market data loaded: {len(orchestrator.market_data)} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("VPP Module 5 Path Fix Verification")
    print("=" * 50)
    
    success = test_module5_fix()
    
    if success:
        print("\n🎉 Module 5 path fix is working!")
        print("Dashboard should now be able to run Module 5 simulations.")
    else:
        print("\n💥 Module 5 still has issues.")
