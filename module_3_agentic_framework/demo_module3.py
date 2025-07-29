#!/usr/bin/env python3
"""
Demo script for VPP Agent Framework - Module 3

This script demonstrates the key capabilities of the agentic framework
including different market scenarios and fleet configurations.
"""

import sys
import os
from datetime import datetime, timedelta

# Add paths for imports
sys.path.append('/Users/reza/Documents/Code/VPP_LLM_Agent/module_2_asset_modeling')
sys.path.append('/Users/reza/Documents/Code/VPP_LLM_Agent/module_3_agentic_framework')

from agent_framework import VPPAgentFramework
from schemas import MarketOpportunity, MarketOpportunityType


def demo_energy_market():
    """Demonstrate energy market negotiation."""
    print("🔋 Energy Market Negotiation Demo")
    print("-" * 40)
    
    framework = VPPAgentFramework()
    
    opportunity = framework.create_market_opportunity(
        market_type="energy",
        required_capacity_mw=3.0,
        market_price_mwh=85.0,
        duration_hours=2.0
    )
    
    print(f"Market Opportunity: {opportunity.market_type.upper()}")
    print(f"Required Capacity: {opportunity.required_capacity_mw} MW")
    print(f"Market Price: ${opportunity.market_price_mwh}/MWh")
    print(f"Duration: {opportunity.duration_hours} hours")
    print()
    
    result = framework.run_negotiation(opportunity, fleet_size=20)
    
    print(f"\n📊 Results Summary:")
    print(f"   Coalition Size: {len(result['committed_coalition'])} prosumers")
    print(f"   Capacity Secured: {result['current_capacity_secured_mw']:.3f} MW")
    print(f"   Success: {'✅' if result['success'] else '❌'}")
    
    return result


def demo_ancillary_services():
    """Demonstrate ancillary services market."""
    print("\n⚡ Ancillary Services Market Demo")
    print("-" * 40)
    
    framework = VPPAgentFramework()
    
    # Spinning reserves opportunity
    opportunity = MarketOpportunity(
        opportunity_id="spin_demo_001",
        market_type=MarketOpportunityType.SPIN,
        timestamp=datetime.now() + timedelta(hours=1),
        duration_hours=4.0,
        required_capacity_mw=2.0,
        market_price_mwh=150.0,
        deadline=datetime.now() + timedelta(minutes=20),
        ramp_rate_required=5.0,  # MW/min
        minimum_duration=1.0
    )
    
    print(f"Market Opportunity: {opportunity.market_type.upper()}")
    print(f"Required Capacity: {opportunity.required_capacity_mw} MW")
    print(f"Market Price: ${opportunity.market_price_mwh}/MWh")
    print(f"Ramp Rate: {opportunity.ramp_rate_required} MW/min")
    print()
    
    result = framework.run_negotiation(opportunity, fleet_size=15)
    
    print(f"\n📊 Results Summary:")
    print(f"   Coalition Size: {len(result['committed_coalition'])} prosumers")
    print(f"   Capacity Secured: {result['current_capacity_secured_mw']:.3f} MW")
    print(f"   Success: {'✅' if result['success'] else '❌'}")
    
    return result


def demo_large_fleet():
    """Demonstrate negotiation with large prosumer fleet."""
    print("\n🏢 Large Fleet Negotiation Demo")
    print("-" * 40)
    
    framework = VPPAgentFramework()
    
    opportunity = framework.create_market_opportunity(
        market_type="energy",
        required_capacity_mw=5.0,
        market_price_mwh=75.0,
        duration_hours=1.0
    )
    
    print(f"Market Opportunity: {opportunity.market_type.upper()}")
    print(f"Required Capacity: {opportunity.required_capacity_mw} MW")
    print(f"Fleet Size: 20 prosumers")
    print()
    
    result = framework.run_negotiation(opportunity, fleet_size=20)
    
    print(f"\n📊 Results Summary:")
    print(f"   Coalition Size: {len(result['committed_coalition'])} prosumers")
    print(f"   Capacity Secured: {result['current_capacity_secured_mw']:.3f} MW")
    print(f"   Success: {'✅' if result['success'] else '❌'}")
    
    # Analyze participation rates
    summary = result['negotiation_summary']
    participation_rate = (summary.total_bids_received / summary.total_prosumers_contacted) * 100
    print(f"   Participation Rate: {participation_rate:.1f}%")
    print(f"   Average Price: ${summary.average_price_per_mwh:.2f}/MWh")
    
    return result


def demo_schema_validation():
    """Demonstrate schema validation capabilities."""
    print("\n📋 Schema Validation Demo")
    print("-" * 40)
    
    from schemas import ProsumerBid, AggregatorOffer, ProsumerResponse
    
    # Create valid prosumer bid
    bid = ProsumerBid(
        prosumer_id="demo_prosumer_001",
        opportunity_id="demo_opp_001",
        is_available=True,
        available_capacity_kw=15.0,
        minimum_price_per_mwh=80.0,
        user_preferences={
            "backup_power_required": "30%",
            "ev_charge_by": "07:00",
            "participation_level": "moderate"
        }
    )
    
    print("✅ ProsumerBid created successfully")
    print(f"   Prosumer: {bid.prosumer_id}")
    print(f"   Capacity: {bid.available_capacity_kw} kW")
    print(f"   Min Price: ${bid.minimum_price_per_mwh}/MWh")
    
    # Create aggregator offer
    offer = AggregatorOffer(
        offer_id="demo_offer_001",
        opportunity_id="demo_opp_001",
        target_prosumer_ids=["demo_prosumer_001"],
        offered_price_per_mwh=85.0,
        requested_capacity_kw=15.0,
        round_number=2,
        total_rounds_planned=3,
        competing_offers=12,
        bonus_payment=5.0
    )
    
    print("✅ AggregatorOffer created successfully")
    print(f"   Offered Price: ${offer.offered_price_per_mwh}/MWh")
    print(f"   Bonus Payment: ${offer.bonus_payment}")
    print(f"   Round: {offer.round_number}/{offer.total_rounds_planned}")
    
    # Create response
    response = ProsumerResponse(
        response_id="demo_response_001",
        offer_id="demo_offer_001",
        prosumer_id="demo_prosumer_001",
        is_accepted=True,
        confidence_level=0.9
    )
    
    print("✅ ProsumerResponse created successfully")
    print(f"   Accepted: {response.is_accepted}")
    print(f"   Confidence: {response.confidence_level}")


def main():
    """Run all demo scenarios."""
    print("VPP Agent Framework Demo - Module 3")
    print("=" * 50)
    
    try:
        # Demo 1: Basic energy market
        demo_energy_market()
        
        # Demo 2: Ancillary services
        demo_ancillary_services()
        
        # Demo 3: Large fleet
        demo_large_fleet()
        
        # Demo 4: Schema validation
        demo_schema_validation()
        
        print("\n🎉 All demos completed successfully!")
        print("=" * 50)
        
        print("\n📋 Module 3 Key Features Demonstrated:")
        print("   ✅ Multi-agent workflow using LangGraph")
        print("   ✅ Pydantic schema validation for all communications")
        print("   ✅ Energy and ancillary services market support")
        print("   ✅ Scalable fleet management (10-100+ prosumers)")
        print("   ✅ Multi-round negotiation protocol")
        print("   ✅ Coalition formation and result summarization")
        
        print("\n🔮 Ready for Module 4 Integration:")
        print("   🚀 LLM-powered agent reasoning")
        print("   🚀 Advanced negotiation strategies")
        print("   🚀 Hybrid optimization (LLM-to-Solver)")
        print("   🚀 Real-time decision making")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
