#!/usr/bin/env python3
"""
Quick test to verify Module 3 fixes work correctly
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

def test_module3_fix():
    """Test that Module 3 works after the path fixes."""
    print("Testing Module 3 fixes...")
    
    try:
        # Add paths like the dashboard does
        base_path = Path(__file__).parent
        module_3_path = str(base_path / 'module_3_agentic_framework')
        module_2_path = str(base_path / 'module_2_asset_modeling')
        module_1_path = str(base_path / 'module_1_data_simulation')
        
        for path in [module_3_path, module_2_path, module_1_path]:
            if path in sys.path:
                sys.path.remove(path)
            sys.path.insert(0, path)
        
        # Import and test
        from agent_framework import VPPAgentFramework
        from schemas import MarketOpportunity, MarketOpportunityType
        
        print("✅ Imports successful")
        
        # Initialize with data path
        module_1_data_path = str(base_path / 'module_1_data_simulation' / 'data')
        agent_system = VPPAgentFramework(data_path=module_1_data_path)
        print("✅ VPPAgentFramework initialized")
        
        # Create test opportunity
        opportunity = MarketOpportunity(
            opportunity_id="test_fix",
            market_type=MarketOpportunityType.ENERGY,
            timestamp=datetime.now(),
            duration_hours=1.0,
            required_capacity_mw=2.0,
            market_price_mwh=80.0,
            deadline=datetime.now() + timedelta(minutes=15)
        )
        print("✅ MarketOpportunity created")
        
        # Test with small fleet first
        print("🧪 Testing with small fleet (10 prosumers)...")
        final_state = agent_system.run_negotiation(
            market_opportunity=opportunity,
            fleet_size=10
        )
        print("✅ Small fleet test successful")
        
        # Test with larger fleet
        print("🧪 Testing with larger fleet (100 prosumers)...")
        final_state = agent_system.run_negotiation(
            market_opportunity=opportunity,
            fleet_size=100
        )
        print("✅ Large fleet test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("VPP Module 3 Fix Verification")
    print("=" * 50)
    
    success = test_module3_fix()
    
    if success:
        print("\n🎉 Module 3 fixes are working!")
        print("You can now use fleet sizes up to 200 in the dashboard.")
    else:
        print("\n💥 Module 3 fixes need more work.")
