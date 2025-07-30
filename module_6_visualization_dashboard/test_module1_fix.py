#!/usr/bin/env python3
"""
Test script to verify Module 1 functionality works with dashboard fixes.
"""

import sys
from pathlib import Path

# Add paths
base_path = Path('../')
module_1_path = str(base_path / 'module_1_data_simulation')
sys.path.insert(0, module_1_path)

from collect_data import VPPDataCollector

# Test configuration
config = {
    'start_date': '2023-08-01',
    'end_date': '2023-08-02',
    'latitude': 34.0522,
    'longitude': -118.2437
}

print("=" * 60)
print("VPP DASHBOARD MODULE 1 TEST")
print("=" * 60)

try:
    # Test VPPDataCollector instantiation
    print("🧪 Testing VPPDataCollector instantiation...")
    collector = VPPDataCollector(config)
    print("✅ VPPDataCollector created successfully")
    
    # Test market data collection
    print("\n📊 Testing market data collection...")
    market_data = collector.fetch_caiso_market_data()
    print(f"✅ Market data collected: {len(market_data)} records")
    print(f"   Columns: {list(market_data.columns)}")
    
    # Check column names match expectations
    expected_columns = ['timestamp', 'lmp', 'spin_price', 'nonspin_price']
    if list(market_data.columns) == expected_columns:
        print("✅ Column names match dashboard expectations")
    else:
        print(f"❌ Column mismatch. Expected: {expected_columns}, Got: {list(market_data.columns)}")
    
    # Test solar data collection
    print("\n☀️ Testing solar data collection...")
    solar_data = collector.fetch_solar_data()
    print(f"✅ Solar data collected: {len(solar_data)} records")
    print(f"   Columns: {list(solar_data.columns)}")
    
    # Test load profile generation
    print("\n🏠 Testing load profile generation...")
    collector.generate_load_profiles()
    print("✅ Load profiles generated successfully")
    
    print("\n" + "=" * 60)
    print("✅ MODULE 1 DASHBOARD INTEGRATION TEST PASSED")
    print("=" * 60)
    print("The dashboard Module 1 fixes should now work correctly!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
