#!/usr/bin/env python3
"""
Test script to debug the schema validation issue in Module 3
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add module paths
base_path = Path(__file__).parent
sys.path.insert(0, str(base_path / 'module_3_agentic_framework'))
sys.path.insert(0, str(base_path / 'module_2_asset_modeling'))

def test_schema_issue():
    """Test the schema validation issue."""
    print("Testing schema validation issue...")
    
    try:
        from schemas import MarketOpportunity, MarketOpportunityType, AgentState
        
        # Create a MarketOpportunity
        opportunity = MarketOpportunity(
            opportunity_id="test_schema",
            market_type=MarketOpportunityType.ENERGY,
            timestamp=datetime.now(),
            duration_hours=1.0,
            required_capacity_mw=2.0,
            market_price_mwh=80.0,
            deadline=datetime.now() + timedelta(minutes=15)
        )
        print(f"✅ MarketOpportunity created: {opportunity.opportunity_id}")
        print(f"   Type: {type(opportunity)}")
        
        # Try to create AgentState with the MarketOpportunity
        print("\n🧪 Testing AgentState creation...")
        
        # Method 1: Direct assignment
        try:
            state = AgentState(current_opportunity=opportunity)
            print("✅ AgentState created successfully with direct assignment")
            print(f"   State type: {type(state)}")
            print(f"   Opportunity type: {type(state.current_opportunity)}")
        except Exception as e:
            print(f"❌ Direct assignment failed: {e}")
            
        # Method 2: Using dict() method
        try:
            state = AgentState(current_opportunity=opportunity.dict())
            print("✅ AgentState created successfully with dict() method")
        except Exception as e:
            print(f"❌ Dict method failed: {e}")
            
        # Method 3: Using model_dump() method (Pydantic v2)
        try:
            state = AgentState(current_opportunity=opportunity.model_dump())
            print("✅ AgentState created successfully with model_dump() method")
        except Exception as e:
            print(f"❌ model_dump method failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fleet_size_limit():
    """Test the fleet size limitation."""
    print("\n" + "="*60)
    print("Testing fleet size limitation...")
    
    try:
        from fleet_generator import FleetGenerator
        
        # Test with correct data path
        data_path = str(base_path / 'module_1_data_simulation' / 'data')
        fleet_gen = FleetGenerator(data_path=data_path)
        
        print(f"Available load profiles: {len(fleet_gen.load_profiles)}")
        
        # Test different fleet sizes
        for size in [10, 50, 100, 200, 250]:
            try:
                fleet = fleet_gen.create_prosumer_fleet(size)
                print(f"✅ Fleet size {size}: Created successfully")
            except ValueError as e:
                print(f"❌ Fleet size {size}: {e}")
                break
                
        return True
        
    except Exception as e:
        print(f"❌ Fleet test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("VPP Module 3 Schema Debug Test")
    print("=" * 60)
    
    schema_success = test_schema_issue()
    fleet_success = test_fleet_size_limit()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Schema validation: {'✅ PASS' if schema_success else '❌ FAIL'}")
    print(f"Fleet size test: {'✅ PASS' if fleet_success else '❌ FAIL'}")
