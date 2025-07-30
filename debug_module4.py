#!/usr/bin/env python3
"""
Debug Module 4 step by step
"""

import sys
import os
from pathlib import Path

# Add project paths
base_path = Path(__file__).parent
sys.path.extend([
    str(base_path / 'module_4_negotiation_logic'),
    str(base_path / 'module_3_agentic_framework'),
    str(base_path / 'module_2_asset_modeling'),
])

def debug_module4():
    print("🔍 Debugging Module 4 Step by Step")
    print("=" * 50)
    
    try:
        from main_negotiation import CoreNegotiationEngine
        from fleet_generator import FleetGenerator
        from schemas import MarketOpportunity, MarketOpportunityType
        from datetime import datetime, timedelta
        
        # Create a fleet
        module_1_data_path = str(base_path / 'module_1_data_simulation' / 'data')
        fleet_gen = FleetGenerator(data_path=module_1_data_path)
        fleet = fleet_gen.create_prosumer_fleet(40)
        print(f"📊 Created fleet of {len(fleet)} prosumers")
        
        # Analyze fleet composition
        bess_count = sum(1 for p in fleet if p.bess)
        ev_count = sum(1 for p in fleet if p.ev)
        solar_count = sum(1 for p in fleet if p.solar)
        print(f"🔋 Fleet composition: {bess_count} BESS, {ev_count} EV, {solar_count} Solar")
        
        # Check availability constraints
        available_count = 0
        low_soc_count = 0
        no_bess_count = 0
        
        for prosumer in fleet:
            if not prosumer.bess:
                no_bess_count += 1
                continue
                
            if prosumer.bess.current_soc_percent <= 20.0:
                low_soc_count += 1
                continue
                
            available_capacity = prosumer.bess.get_available_discharge_capacity_kw()
            if available_capacity > 1.0:
                available_count += 1
        
        print(f"⚡ Availability analysis:")
        print(f"   Available: {available_count}")
        print(f"   No BESS: {no_bess_count}")
        print(f"   Low SOC (<20%): {low_soc_count}")
        print(f"   Other constraints: {len(fleet) - available_count - no_bess_count - low_soc_count}")
        
        # Create negotiation engine
        engine = CoreNegotiationEngine()
        print(f"⚙️  Negotiation engine initialized")
        
        # Create opportunity
        opportunity = MarketOpportunity(
            opportunity_id="debug_test",
            market_type=MarketOpportunityType.ENERGY,
            timestamp=datetime.now(),
            duration_hours=1.0,
            required_capacity_mw=1.5,
            market_price_mwh=75.0,
            deadline=datetime.now() + timedelta(minutes=15)
        )
        print(f"🎯 Market opportunity: {opportunity.required_capacity_mw:.1f} MW @ ${opportunity.market_price_mwh:.2f}/MWh")
        
        # Step 1: Test initial bid collection
        initial_bids = engine._collect_initial_bids(opportunity, fleet)
        print(f"📥 Initial bids collected: {len(initial_bids)} from {len(fleet)} prosumers")
        
        for i, bid in enumerate(initial_bids[:5]):  # Show first 5 bids
            print(f"   Bid {i+1}: {bid.prosumer_id} - {bid.available_capacity_kw:.1f} kW @ ${bid.minimum_price_per_mwh:.2f}/MWh")
        
        if len(initial_bids) < len(fleet):
            unavailable = len(fleet) - len(initial_bids)
            print(f"   ⚠️  {unavailable} prosumers unavailable")
        
        # Step 2: Test bid ranking
        if initial_bids:
            ranked_bids = engine._evaluate_and_rank_bids(initial_bids, opportunity)
            print(f"📊 Ranked bids: {len(ranked_bids)}")
            
            # Step 3: Test counter-offers
            counter_offers = engine._generate_counter_offers(ranked_bids, opportunity)
            print(f"💰 Counter-offers generated: {len(counter_offers)}")
            
            # Step 4: Test responses
            responses = engine._collect_counter_responses(counter_offers, fleet)
            print(f"📩 Responses to counter-offers: {len(responses)}")
            
            accepted_responses = [r for r in responses if r.is_accepted]
            print(f"   ✅ Accepted: {len(accepted_responses)}")
            print(f"   ❌ Rejected: {len(responses) - len(accepted_responses)}")
            
            # Step 5: Test coalition formation
            final_coalition = engine._form_final_coalition(responses, opportunity)
            print(f"🤝 Final coalition size: {len(final_coalition)}")
            
            total_capacity = sum(m.committed_capacity_kw for m in final_coalition)
            print(f"⚡ Total capacity: {total_capacity:.1f} kW ({total_capacity/1000:.3f} MW)")
            print(f"🎯 Target capacity: {opportunity.required_capacity_mw:.1f} MW")
            print(f"📈 Coverage: {(total_capacity/1000)/opportunity.required_capacity_mw*100:.1f}%")
            
            # Step 6: Test price calculation
            if final_coalition:
                final_price = engine._calculate_optimal_bid_price(final_coalition, opportunity)
                print(f"💵 Final bid price: ${final_price:.2f}/MWh")
                
                # Debug price calculation
                print("\n🔍 Price Calculation Debug:")
                for i, member in enumerate(final_coalition[:3]):  # Show first 3 members
                    price = getattr(member, 'agreed_price_per_mwh', 'NOT_SET')
                    print(f"   Member {i+1}: {member.prosumer_id} - {member.committed_capacity_kw:.1f} kW @ ${price}/MWh")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_module4()
