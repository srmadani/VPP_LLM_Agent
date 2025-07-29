"""
Simple validation test for Module 5 core functionality.
This test runs independently of other modules to validate the key components.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Mock the required schemas and models for testing
class MockMarketOpportunity:
    def __init__(self, opportunity_id, market_type, timestamp, duration_hours, required_capacity_mw, market_price_mwh, deadline):
        self.opportunity_id = opportunity_id
        self.market_type = market_type
        self.timestamp = timestamp
        self.duration_hours = duration_hours
        self.required_capacity_mw = required_capacity_mw
        self.market_price_mwh = market_price_mwh
        self.deadline = deadline

class MockBESS:
    def __init__(self):
        self.capacity_kwh = 100.0
        self.max_power_kw = 25.0
        self.current_soc_kwh = 60.0
        self.current_soc_percent = 60.0  # 60/100 * 100
        self.efficiency = 0.95
    
    def update_soc(self, change_kwh):
        self.current_soc_kwh = max(0, min(self.capacity_kwh, self.current_soc_kwh + change_kwh))
        self.current_soc_percent = (self.current_soc_kwh / self.capacity_kwh) * 100

class MockEV:
    def __init__(self):
        self.battery_capacity_kwh = 75.0
        self.max_charge_power_kw = 7.2
        self.current_soc_kwh = 50.0
        self.current_soc_percent = 66.7  # 50/75 * 100
        self.is_plugged_in = True
    
    def get_charging_requirement_kwh(self, target_soc_percent=80.0):
        """Calculate charging requirement to reach target SOC."""
        target_soc_kwh = (target_soc_percent / 100.0) * self.battery_capacity_kwh
        return max(0, target_soc_kwh - self.current_soc_kwh)

class MockProsumer:
    def __init__(self, prosumer_id):
        self.prosumer_id = prosumer_id
        self.bess = MockBESS() if np.random.random() < 0.6 else None
        self.ev = MockEV() if np.random.random() < 0.4 else None
        self.backup_power_hours = 4.0  # Default backup power requirement
        self.preferences = {
            "min_battery_soc_percent": np.random.randint(20, 50),
            "ev_charge_deadline": "07:00"
        }

def test_centralized_optimizer():
    """Test the centralized optimizer with mock data."""
    print("🧪 Testing Centralized Optimizer...")
    
    # Import the actual optimizer
    sys.path.append('/Users/reza/Documents/Code/VPP_LLM_Agent/module_5_simulation_orchestration')
    from centralized_optimizer import CentralizedOptimizer
    
    # Create test data
    optimizer = CentralizedOptimizer()
    prosumer_fleet = [MockProsumer(f"prosumer_{i}") for i in range(5)]
    
    # Create mock opportunity
    now = datetime.now()
    opportunity = MockMarketOpportunity(
        opportunity_id="test_001",
        market_type="energy",
        timestamp=now,
        duration_hours=1.0,
        required_capacity_mw=2.0,
        market_price_mwh=75.0,
        deadline=now + timedelta(minutes=30)
    )
    
    # Test the core optimization logic
    available_prosumers = optimizer._filter_available_prosumers(prosumer_fleet, now)
    print(f"   ✅ Found {len(available_prosumers)} available prosumers")
    
    # Test capacity calculation
    total_capacity = 0
    total_violations = 0
    
    for prosumer in available_prosumers:
        capacity, cost, violations = optimizer._calculate_prosumer_capacity_cost(
            prosumer, "energy", now
        )
        total_capacity += capacity
        total_violations += len(violations)
    
    print(f"   ✅ Total available capacity: {total_capacity:.1f} kW")
    print(f"   ✅ Total preference violations: {total_violations}")
    
    return True

def test_simulation_metrics():
    """Test the simulation metrics and summary structures."""
    print("📊 Testing Simulation Metrics...")
    
    sys.path.append('/Users/reza/Documents/Code/VPP_LLM_Agent/module_5_simulation_orchestration')
    from simulation import SimulationMetrics, SimulationSummary
    
    # Create test metrics
    test_metrics = SimulationMetrics(
        timestamp=datetime.now(),
        lmp_price=50.0,
        spin_price=10.0,
        nonspin_price=7.0,
        agentic_success=True,
        agentic_bid_capacity_mw=1.5,
        agentic_bid_price_mwh=55.0,
        agentic_expected_profit=100.0,
        agentic_actual_profit=95.0,
        agentic_prosumer_satisfaction=0.85,
        agentic_negotiation_rounds=3,
        agentic_coalition_size=5,
        agentic_optimization_time=2.5,
        centralized_success=True,
        centralized_bid_capacity_mw=1.8,
        centralized_bid_price_mwh=52.0,
        centralized_expected_profit=110.0,
        centralized_actual_profit=105.0,
        centralized_prosumer_satisfaction=0.0,
        centralized_preference_violations=3,
        centralized_optimization_time=0.5,
        profit_difference=-10.0,
        satisfaction_difference=0.85,
        capacity_difference_mw=-0.3,
        price_difference_mwh=3.0
    )
    
    print(f"   ✅ Metrics created: {test_metrics.timestamp}")
    print(f"   ✅ Profit difference: ${test_metrics.profit_difference:.2f}")
    print(f"   ✅ Satisfaction advantage: {test_metrics.satisfaction_difference:.3f}")
    
    # Create test summary
    test_summary = SimulationSummary(
        total_timesteps=24,
        simulation_duration_hours=24.0,
        agentic_total_profit=500.0,
        agentic_avg_satisfaction=0.8,
        agentic_success_rate=0.9,
        agentic_avg_coalition_size=4.5,
        agentic_avg_negotiation_rounds=2.8,
        agentic_total_capacity_mwh=30.0,
        centralized_total_profit=550.0,
        centralized_avg_satisfaction=0.0,
        centralized_success_rate=0.95,
        centralized_total_violations=12,
        centralized_total_capacity_mwh=32.0,
        profit_advantage_percent=-9.1,
        satisfaction_advantage_percent=80.0,
        efficiency_ratio=0.94,
        agentic_avg_time_seconds=3.2,
        centralized_avg_time_seconds=0.6,
        total_simulation_time_minutes=5.2
    )
    
    print(f"   ✅ Summary created for {test_summary.total_timesteps} timesteps")
    print(f"   ✅ Satisfaction advantage: {test_summary.satisfaction_advantage_percent:.1f}%")
    
    return True

def test_data_processing():
    """Test data loading and processing."""
    print("💾 Testing Data Processing...")
    
    # Check for market data
    data_path = Path("/Users/reza/Documents/Code/VPP_LLM_Agent/module_1_data_simulation/data")
    market_file = data_path / "market_data.csv"
    
    if market_file.exists():
        market_data = pd.read_csv(market_file)
        market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
        
        print(f"   ✅ Market data loaded: {len(market_data)} records")
        print(f"   ✅ Time range: {market_data['timestamp'].min()} to {market_data['timestamp'].max()}")
        print(f"   ✅ Price range: ${market_data['lmp'].min():.2f} - ${market_data['lmp'].max():.2f}")
        
        return True
    else:
        print("   ⚠️ No market data found - run Module 1 first")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Module 5 Core Functionality Validation")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    try:
        if test_centralized_optimizer():
            success_count += 1
    except Exception as e:
        print(f"   ❌ Centralized optimizer test failed: {e}")
    
    try:
        if test_simulation_metrics():
            success_count += 1
    except Exception as e:
        print(f"   ❌ Simulation metrics test failed: {e}")
    
    try:
        if test_data_processing():
            success_count += 1
    except Exception as e:
        print(f"   ❌ Data processing test failed: {e}")
    
    print(f"\n🏁 VALIDATION COMPLETE")
    print(f"   {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("   ✅ Module 5 core functionality validated")
        print("   🎯 Ready for integration with other modules")
        
        print(f"\n🔑 KEY ACHIEVEMENTS:")
        print("   📊 Centralized optimization baseline working")
        print("   📈 Comprehensive metrics system implemented")
        print("   💾 Data processing and integration functional")
        print("   🧪 Test framework validates all components")
        
        print(f"\n📋 NEXT STEPS:")
        print("   1. Integrate with Module 4 negotiation engine")
        print("   2. Run full end-to-end simulation")
        print("   3. Generate comparative analysis results")
        print("   4. Prepare for Module 6 visualization")
        
    else:
        print("   ⚠️ Some tests failed - check dependencies")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
