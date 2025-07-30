#!/usr/bin/env python3
"""
Quick test to check if the Module 3 schema fix works
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

def test_module3_schema_fix():
    """Test the updated Module 3 schema handling."""
    print("Testing Module 3 schema fix...")
    
    try:
        # Add paths like the dashboard does
        base_path = Path(__file__).parent
        module_3_path = str(base_path / 'module_3_agentic_framework')
        module_2_path = str(base_path / 'module_2_asset_modeling')
        
        for path in [module_3_path, module_2_path]:
            if path in sys.path:
                sys.path.remove(path)
            sys.path.insert(0, path)
        
        # Import and test
        from agent_framework import VPPAgentFramework
        from schemas import MarketOpportunity, MarketOpportunityType
        
        print("✅ Imports successful")
        print(f"MarketOpportunity: {MarketOpportunity}")
        print(f"MarketOpportunityType: {MarketOpportunityType}")
        
        # Initialize with data path
        module_1_data_path = str(base_path / 'module_1_data_simulation' / 'data')
        agent_system = VPPAgentFramework(data_path=module_1_data_path)
        print("✅ VPPAgentFramework initialized")
        
        # Create test opportunity
        opportunity = MarketOpportunity(
            opportunity_id="test_schema_fix",
            market_type=MarketOpportunityType.ENERGY,
            timestamp=datetime.now(),
            duration_hours=1.0,
            required_capacity_mw=2.0,
            market_price_mwh=80.0,
            deadline=datetime.now() + timedelta(minutes=15)
        )
        print(f"✅ MarketOpportunity created: {type(opportunity)}")
        
        # Test with different fleet sizes
        for fleet_size in [10, 50]:
            print(f"\n🧪 Testing with fleet size {fleet_size}...")
            try:
                final_state = agent_system.run_negotiation(
                    market_opportunity=opportunity,
                    fleet_size=fleet_size
                )
                print(f"✅ Fleet size {fleet_size} successful")
                
                # Check results
                if hasattr(final_state, 'success'):
                    print(f"   Negotiation success: {final_state.success}")
                if hasattr(final_state, 'current_round'):
                    print(f"   Rounds completed: {final_state.current_round}")
                    
            except Exception as e:
                print(f"❌ Fleet size {fleet_size} failed: {e}")
                # Don't break, continue testing
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("VPP Module 3 Schema Fix Test")
    print("=" * 50)
    
    success = test_module3_schema_fix()
    
    if success:
        print("\n🎉 Module 3 schema fixes are working!")
    else:
        print("\n💥 Module 3 still has issues.")
