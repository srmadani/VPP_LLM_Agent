#!/usr/bin/env python3
"""
Quick test to verify that the path fix works for Module 2 FleetGenerator
"""

import sys
import os
from pathlib import Path

# Add module paths (simulating what the dashboard does)
base_path = Path(__file__).parent
module_2_path = str(base_path / 'module_2_asset_modeling')
module_1_path = str(base_path / 'module_1_data_simulation')

sys.path.insert(0, module_2_path)
sys.path.insert(0, module_1_path)

def test_fleet_generator_with_path():
    """Test FleetGenerator with explicit data path."""
    print("Testing FleetGenerator with explicit data path...")
    
    try:
        from fleet_generator import FleetGenerator
        
        # Use absolute path as the dashboard now does
        module_1_data_path = str(base_path / 'module_1_data_simulation' / 'data')
        print(f"Data path: {module_1_data_path}")
        print(f"Path exists: {os.path.exists(module_1_data_path)}")
        
        # Test load_profiles directory
        load_profiles_path = str(base_path / 'module_1_data_simulation' / 'data' / 'load_profiles')
        print(f"Load profiles path: {load_profiles_path}")
        print(f"Load profiles exists: {os.path.exists(load_profiles_path)}")
        
        # Initialize FleetGenerator with explicit path
        fleet_gen = FleetGenerator(data_path=module_1_data_path)
        print("✅ FleetGenerator initialized successfully!")
        
        # Test generating a small fleet
        fleet = fleet_gen.create_prosumer_fleet(5)
        print(f"✅ Generated fleet of {len(fleet)} prosumers!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fleet_generator_with_path()
    if success:
        print("\n🎉 Path fix successful! Module 2 should work in dashboard now.")
    else:
        print("\n💥 Path fix failed. Need to investigate further.")
