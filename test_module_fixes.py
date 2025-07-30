#!/usr/bin/env python3
"""
Test script to verify Module 3 and Module 4 fixes
"""

import sys
import os
from pathlib import Path

# Add project paths
base_path = Path(__file__).parent
sys.path.extend([
    str(base_path / 'module_6_visualization_dashboard'),
    str(base_path / 'module_3_agentic_framework'),
    str(base_path / 'module_4_negotiation_logic'),
    str(base_path / 'module_2_asset_modeling'),
])

def test_module3_capacity_calculation():
    """Test Module 3 with different fleet sizes to verify capacity calculation"""
    print("🧪 Testing Module 3 Capacity Calculation")
    print("=" * 50)
    
    try:
        from dashboard import ModuleRunner
        
        module_runner = ModuleRunner(base_path)
        
        # Test different fleet sizes
        fleet_sizes = [10, 25, 50]
        
        for fleet_size in fleet_sizes:
            print(f"\n📊 Testing fleet size: {fleet_size}")
            result = module_runner.run_module_3(fleet_size=fleet_size)
            
            if result['status'] == 'success':
                print(f"   ✅ Negotiation Success: {'Yes' if result['success'] else 'No'}")
                print(f"   👥 Coalition Size: {result['coalition_size']}")
                print(f"   📈 Coalition Coverage: {result['coalition_size']/result['participants']*100:.1f}%")
                print(f"   💰 Final Price: ${result['final_price']:.2f}/MWh")
                
                # Calculate expected capacity requirement
                realistic_capacity = max(0.05, fleet_size * 0.008)
                print(f"   🎯 Expected Capacity Requirement: {realistic_capacity:.3f} MW")
                print(f"   🔋 Required for Success (80%): {realistic_capacity * 0.8:.3f} MW")
            else:
                print(f"   ❌ Module failed: {result['message']}")
                
    except Exception as e:
        print(f"❌ Error testing Module 3: {e}")
        import traceback
        traceback.print_exc()

def test_module4_attribute_fix():
    """Test Module 4 attribute fix"""
    print("\n🧪 Testing Module 4 Attribute Fix")
    print("=" * 50)
    
    try:
        from dashboard import ModuleRunner
        
        module_runner = ModuleRunner(base_path)
        
        # Test Module 4
        print(f"\n📊 Testing Module 4 with 15 prosumers")
        result = module_runner.run_module_4(fleet_size=15)
        
        if result['status'] == 'success':
            print(f"   ✅ Module 4 Success!")
            print(f"   👥 Coalition Size: {result['coalition_size']}")
            print(f"   🔋 Total Capacity: {result['total_capacity']:.1f} kW")
            print(f"   💰 Agreed Price: ${result['agreed_price']:.2f}/MWh")
            print(f"   😊 Satisfaction Score: {result['satisfaction_score']:.1f}/10")
            print(f"   ⏱️  Negotiation Time: {result['negotiation_time']:.3f}s")
        else:
            print(f"   ❌ Module failed: {result['message']}")
            if 'traceback' in result:
                print("   📜 Error details:")
                print(result['traceback'])
                
    except Exception as e:
        print(f"❌ Error testing Module 4: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing VPP Module Fixes")
    print("=" * 60)
    
    test_module3_capacity_calculation()
    test_module4_attribute_fix()
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
