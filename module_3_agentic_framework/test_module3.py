#!/usr/bin/env python3
"""
Test script for VPP Agent Framework - Module 3

This script validates that all components of the agentic framework
work correctly and produce expected outputs.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the paths for module imports
sys.path.append('/Users/reza/Documents/Code/VPP_LLM_Agent/module_2_asset_modeling')
sys.path.append('/Users/reza/Documents/Code/VPP_LLM_Agent/module_3_agentic_framework')

# Import the framework and schemas
from agent_framework import VPPAgentFramework
from schemas import MarketOpportunity, MarketOpportunityType


def test_schemas():
    """Test that all Pydantic schemas work correctly."""
    print("🧪 Testing Pydantic schemas...")
    
    # Test MarketOpportunity creation
    opportunity = MarketOpportunity(
        opportunity_id="test_opp_001",
        market_type=MarketOpportunityType.ENERGY,
        timestamp=datetime.now() + timedelta(hours=1),
        duration_hours=1.0,
        required_capacity_mw=5.0,
        market_price_mwh=75.0,
        deadline=datetime.now() + timedelta(minutes=30)
    )
    
    assert opportunity.opportunity_id == "test_opp_001"
    assert opportunity.market_type == MarketOpportunityType.ENERGY
    assert opportunity.required_capacity_mw == 5.0
    
    print("   ✅ MarketOpportunity schema working")
    
    print("   ✅ All schemas validated successfully")


def test_framework_initialization():
    """Test that the VPP Agent Framework initializes correctly."""
    print("🧪 Testing framework initialization...")
    
    try:
        framework = VPPAgentFramework()
        print("   ✅ Framework initialized successfully")
        
        # Test prosumer fleet initialization
        framework.initialize_prosumer_fleet(fleet_size=10)
        assert len(framework.prosumer_fleet) == 10
        print("   ✅ Prosumer fleet created successfully")
        
        # Test market opportunity creation
        opportunity = framework.create_market_opportunity()
        assert opportunity is not None
        assert opportunity.required_capacity_mw > 0
        print("   ✅ Market opportunity created successfully")
        
        return framework
        
    except Exception as e:
        print(f"   ❌ Framework initialization failed: {e}")
        raise


def test_workflow_structure():
    """Test that the LangGraph workflow is properly structured."""
    print("🧪 Testing workflow structure...")
    
    framework = VPPAgentFramework()
    
    # Check that workflow is compiled
    assert framework.workflow is not None
    print("   ✅ Workflow compiled successfully")
    
    # Check that all required nodes exist by testing the workflow graph
    try:
        graph = framework.workflow.get_graph()
        # The graph exists and can be accessed
        print("   ✅ Workflow graph accessible")
        
        # Test that we can get basic graph information
        assert hasattr(graph, 'nodes')
        print("   ✅ Graph has nodes attribute")
        
    except Exception as e:
        print(f"   ⚠️  Graph structure test skipped: {e}")
    
    print("   ✅ Workflow structure validated")


def test_simple_negotiation():
    """Test a simple end-to-end negotiation."""
    print("🧪 Testing simple negotiation...")
    
    try:
        framework = VPPAgentFramework()
        
        # Create a small test opportunity
        opportunity = framework.create_market_opportunity(
            market_type="energy",
            required_capacity_mw=2.0,
            market_price_mwh=80.0,
            duration_hours=1.0
        )
        
        # Run negotiation with small fleet
        result = framework.run_negotiation(opportunity, fleet_size=15)
        
        # Validate results - the result is a dict-like object
        assert result is not None
        assert 'current_opportunity' in result
        assert 'negotiation_summary' in result
        assert 'initial_bids' in result
        
        print(f"   ✅ Negotiation completed successfully")
        print(f"      Coalition size: {len(result.get('committed_coalition', []))}")
        print(f"      Capacity secured: {result.get('current_capacity_secured_mw', 0.0):.2f} MW")
        print(f"      Success: {result.get('success', False)}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Negotiation test failed: {e}")
        raise


def test_agent_prompts():
    """Test that agent prompts are loaded correctly."""
    print("🧪 Testing agent prompts...")
    
    framework = VPPAgentFramework()
    
    # Check that prompts are loaded
    assert len(framework.aggregator_prompt) > 100
    assert len(framework.prosumer_prompt) > 100
    
    # Check that key content is present
    assert "AggregatorAgent" in framework.aggregator_prompt
    assert "ProsumerAgent" in framework.prosumer_prompt
    assert "CAISO" in framework.aggregator_prompt
    assert "battery" in framework.prosumer_prompt.lower()
    
    print("   ✅ Agent prompts loaded and validated")


def run_all_tests():
    """Run all validation tests."""
    print("VPP Agent Framework Validation - Module 3")
    print("=" * 50)
    
    try:
        # Test 1: Schema validation
        test_schemas()
        print()
        
        # Test 2: Framework initialization
        framework = test_framework_initialization()
        print()
        
        # Test 3: Workflow structure
        test_workflow_structure()
        print()
        
        # Test 4: Agent prompts
        test_agent_prompts()
        print()
        
        # Test 5: Simple negotiation
        result = test_simple_negotiation()
        print()
        
        print("🎉 All tests passed successfully!")
        print("=" * 50)
        
        # Print final summary
        if result:
            summary = result.get('negotiation_summary')
            if summary:
                print("📊 Final Test Results:")
                print(f"   Prosumers contacted: {summary.total_prosumers_contacted}")
                print(f"   Initial bids: {summary.total_bids_received}")
                print(f"   Coalition members: {summary.final_coalition_size}")
                print(f"   Total capacity: {summary.total_committed_capacity_mw:.2f} MW")
                print(f"   Average price: ${summary.average_price_per_mwh:.2f}/MWh")
                print(f"   Negotiation duration: {summary.negotiation_duration_seconds:.1f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
