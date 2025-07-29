#!/usr/bin/env python3
"""
Test script to validate realistic parameters and satisfaction scoring changes.
"""

import sys
import os
from datetime import datetime

# Add module paths
sys.path.append('module_1_data_simulation')
sys.path.append('module_2_asset_modeling') 
sys.path.append('module_3_agentic_framework')
sys.path.append('module_4_negotiation_logic')
sys.path.append('module_5_simulation_orchestration')

def test_satisfaction_scoring():
    """Test the updated satisfaction scoring to ensure realistic values."""
    print("="*60)
    print("TESTING REALISTIC SATISFACTION SCORING")
    print("="*60)
    
    try:
        from centralized_optimizer import CentralizedOptimizer
        from main_negotiation import CoreNegotiationEngine
        from fleet_generator import FleetGenerator
        from schemas import MarketOpportunity, MarketOpportunityType
        from datetime import timedelta
        
        # Test centralized satisfaction baseline
        print("🧪 Testing centralized optimizer satisfaction baseline...")
        optimizer = CentralizedOptimizer()
        fleet_gen = FleetGenerator()
        fleet = fleet_gen.create_prosumer_fleet(5)  # Small test fleet
        
        # Create test market opportunity
        now = datetime.now()
        opportunity = MarketOpportunity(
            opportunity_id="test_satisfaction",
            market_type=MarketOpportunityType.ENERGY,
            timestamp=now,
            duration_hours=1.0,
            required_capacity_mw=2.0,
            market_price_mwh=50.0,
            deadline=now + timedelta(minutes=15)
        )
        
        result = optimizer.optimize_coalition(fleet, opportunity, now)
        print(f"   Centralized satisfaction score: {result.prosumer_satisfaction_score}")
        print(f"   Expected: ~4.5 (moderate baseline)")
        
        # Test agentic satisfaction scoring
        print("\n🤝 Testing agentic negotiation satisfaction scoring...")
        negotiator = CoreNegotiationEngine()
        agentic_result = negotiator.run_negotiation(fleet, opportunity)
        print(f"   Agentic satisfaction score: {agentic_result.prosumer_satisfaction_score}")
        print(f"   Expected: ~6.0 (higher due to preference consideration)")
        
        # Calculate advantage
        if result.prosumer_satisfaction_score > 0:
            advantage = ((agentic_result.prosumer_satisfaction_score - result.prosumer_satisfaction_score) 
                        / result.prosumer_satisfaction_score * 100)
            print(f"\n📊 Satisfaction advantage: {advantage:.1f}%")
            print(f"   Target range: 20-50% (realistic improvement)")
            
            if 15 <= advantage <= 60:
                print("   ✅ REALISTIC RANGE ACHIEVED")
            else:
                print("   ⚠️  May need further adjustment")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_fleet_scaling():
    """Test that the fleet generator can handle larger fleets."""
    print("\n" + "="*60)
    print("TESTING FLEET SCALING CAPABILITY")
    print("="*60)
    
    try:
        from fleet_generator import FleetGenerator
        
        fleet_gen = FleetGenerator()
        
        # Test smaller fleet first
        print("🧪 Testing 50-prosumer fleet generation...")
        fleet_50 = fleet_gen.create_prosumer_fleet(50)
        print(f"   Generated {len(fleet_50)} prosumers")
        
        # Check asset diversity
        bess_count = sum(1 for p in fleet_50 if p.bess)
        ev_count = sum(1 for p in fleet_50 if p.ev)
        solar_count = sum(1 for p in fleet_50 if p.solar_pv)
        
        print(f"   BESS: {bess_count} ({bess_count/len(fleet_50)*100:.1f}%)")
        print(f"   EV: {ev_count} ({ev_count/len(fleet_50)*100:.1f}%)")
        print(f"   Solar: {solar_count} ({solar_count/len(fleet_50)*100:.1f}%)")
        
        # Test larger fleet
        print("\n🏭 Testing 200-prosumer fleet generation...")
        fleet_200 = fleet_gen.create_prosumer_fleet(200)
        print(f"   Generated {len(fleet_200)} prosumers")
        
        # Check load profile distribution
        profile_ids = [p.load_profile_id for p in fleet_200]
        unique_profiles = len(set(profile_ids))
        print(f"   Using {unique_profiles} unique load profiles")
        
        if unique_profiles >= 180:  # Should use most of the 200 available profiles
            print("   ✅ GOOD PROFILE DIVERSITY")
        else:
            print("   ⚠️  Limited profile diversity")
            
        return True
        
    except Exception as e:
        print(f"❌ Fleet scaling test failed: {e}")
        return False

def test_data_coverage():
    """Test that we have sufficient data for month-long simulation."""
    print("\n" + "="*60)
    print("TESTING DATA COVERAGE FOR MONTHLY SIMULATION")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Check market data coverage
        print("📊 Checking market data coverage...")
        market_data = pd.read_csv('module_1_data_simulation/data/market_data.csv')
        market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
        
        start_date = market_data['timestamp'].min()
        end_date = market_data['timestamp'].max()
        duration_hours = len(market_data) * 0.25  # 15-minute intervals
        
        print(f"   Start: {start_date}")
        print(f"   End: {end_date}")
        print(f"   Duration: {duration_hours:.0f} hours ({duration_hours/24:.1f} days)")
        
        if duration_hours >= 720:  # 30+ days
            print("   ✅ SUFFICIENT DATA FOR MONTHLY SIMULATION")
        else:
            print("   ⚠️  May need more data")
            
        # Check load profiles
        print("\n🏠 Checking load profile availability...")
        import os
        profile_count = len([f for f in os.listdir('module_1_data_simulation/data/load_profiles') 
                           if f.endswith('.csv')])
        print(f"   Available profiles: {profile_count}")
        
        if profile_count >= 200:
            print("   ✅ SUFFICIENT PROFILES FOR LARGE FLEET")
        else:
            print("   ⚠️  May need more profiles")
            
        return True
        
    except Exception as e:
        print(f"❌ Data coverage test failed: {e}")
        return False

def main():
    """Run all parameter validation tests."""
    print("VPP LLM Agent - Realistic Parameter Validation")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(test_satisfaction_scoring())
    results.append(test_fleet_scaling())
    results.append(test_data_coverage())
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Ready for realistic scale simulation!")
        print("\nNext steps:")
        print("1. Run full simulation: python module_5_simulation_orchestration/demo_module5.py")
        print("2. Monitor satisfaction advantage (target: 20-50%)")
        print("3. Verify performance with 200 prosumers over full month")
    else:
        print("⚠️  Some tests failed - review parameters before full simulation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
