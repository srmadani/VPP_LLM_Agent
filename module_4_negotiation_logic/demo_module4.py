"""
Demo Script for Module 4: Core Negotiation Logic & Optimization

This script demonstrates the complete functionality of Module 4,
showing the LLM-powered negotiation and optimization capabilities.
"""

import sys
import os
from datetime import datetime, timedelta

# Add paths
sys.path.append('../module_1_data_simulation')
sys.path.append('../module_2_asset_modeling')
sys.path.append('../module_3_agentic_framework')

# Import components
from integrated_system import IntegratedNegotiationSystem
import pandas as pd
from dotenv import load_dotenv

# Test data structures
class DemoMarketOpportunity:
    """Demo market opportunity."""
    def __init__(self):
        self.opportunity_id = "demo_energy_20230815_1200"
        self.market_type = "energy"  # String instead of enum for compatibility
        self.timestamp = datetime(2023, 8, 15, 12, 0, 0)
        self.duration_hours = 1.0
        self.required_capacity_mw = 0.025  # 25 kW needed (realistic for demo fleet)
        self.market_price_mwh = 85.0
        self.deadline = datetime(2023, 8, 15, 11, 45, 0)

class DemoProsumer:
    """Demo prosumer with BESS."""
    def __init__(self, prosumer_id: str, soc: float = 60.0, preferences: dict = None):
        self.prosumer_id = prosumer_id
        self.bess = DemoBESS(soc)
        self.user_preferences = preferences or {
            'backup_power_percent': 25.0,
            'risk_tolerance': 'medium'
        }

class DemoBESS:
    """Demo BESS for testing."""
    def __init__(self, soc: float = 60.0):
        self.capacity_kwh = 13.5
        self.current_soc_percent = soc
        self.min_soc_percent = 20.0
        self.max_power_kw = 5.0
    
    def get_available_discharge_capacity_kw(self) -> float:
        available_energy = (self.current_soc_percent - self.min_soc_percent) / 100.0 * self.capacity_kwh
        return min(self.max_power_kw, available_energy * 4)
    
    def get_available_charge_capacity_kw(self) -> float:
        available_space = (95.0 - self.current_soc_percent) / 100.0 * self.capacity_kwh
        return min(self.max_power_kw, available_space * 4)


def run_demo():
    """Run the complete Module 4 demonstration."""
    
    print("=" * 70)
    print("          VPP LLM Agent - Module 4 Demonstration")
    print("          Core Negotiation Logic & Optimization")
    print("=" * 70)
    
    # Check environment
    load_dotenv()
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("Please add your Gemini API key to continue.")
        return
    
    print("✅ Environment configured successfully")
    print()
    
    # Initialize system
    print("🚀 Initializing Integrated Negotiation System...")
    try:
        system = IntegratedNegotiationSystem()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return
    
    print()
    
    # Create demo scenario
    print("📋 Setting up demonstration scenario...")
    
    # Market opportunity
    opportunity = DemoMarketOpportunity()
    print(f"   Market Opportunity: {opportunity.opportunity_id}")
    print(f"   Type: {opportunity.market_type.upper()}")
    print(f"   Required Capacity: {opportunity.required_capacity_mw:.1f} MW")
    print(f"   Market Price: ${opportunity.market_price_mwh:.2f}/MWh")
    print()
    
    # Prosumer fleet
    prosumer_fleet = []
    prosumer_configs = [
        ("Tesla Powerwall Owner", 70.0, {'backup_power_percent': 30.0, 'risk_tolerance': 'low'}),
        ("Solar Enthusiast", 85.0, {'backup_power_percent': 20.0, 'risk_tolerance': 'high'}),
        ("Tech-Savvy User", 45.0, {'backup_power_percent': 35.0, 'risk_tolerance': 'medium'}),
        ("Green Energy Advocate", 60.0, {'backup_power_percent': 25.0, 'risk_tolerance': 'high'}),
        ("Smart Home Owner", 55.0, {'backup_power_percent': 40.0, 'risk_tolerance': 'low'}),
        ("EV Owner", 75.0, {'backup_power_percent': 25.0, 'risk_tolerance': 'medium'}),
    ]
    
    for i, (description, soc, prefs) in enumerate(prosumer_configs):
        prosumer = DemoProsumer(f"prosumer_{i+1:03d}", soc, prefs)
        prosumer_fleet.append(prosumer)
        available_kw = prosumer.bess.get_available_discharge_capacity_kw()
        print(f"   Prosumer {i+1}: {description}")
        print(f"      SOC: {soc:.1f}% | Available: {available_kw:.1f} kW | Risk: {prefs['risk_tolerance']}")
    
    print(f"\n   Total Fleet Size: {len(prosumer_fleet)} prosumers")
    print()
    
    # Market data
    market_data = pd.DataFrame({
        'timestamp': [datetime(2023, 8, 15, 12, 0, 0)],
        'lmp': [85.0],
        'spin_price': [12.5],
        'nonspin_price': [7.0]
    })
    
    # Run negotiation
    print("🤝 Starting Multi-Round Negotiation Process...")
    print("-" * 50)
    
    try:
        result = system.run_complete_negotiation_cycle(
            opportunity, prosumer_fleet, market_data
        )
        
        # Display results
        print("\n📊 NEGOTIATION RESULTS:")
        print("=" * 30)
        
        if result['success']:
            print("✅ Negotiation Status: SUCCESS")
            
            # Negotiation summary
            neg = result['negotiation']
            print(f"\n🤝 Coalition Formation:")
            print(f"   Coalition Size: {neg['coalition_size']} prosumers")
            print(f"   Total Capacity: {neg['total_capacity_mw']:.2f} MW")
            print(f"   Average Satisfaction: {neg['avg_satisfaction']:.1f}/10")
            print(f"   Negotiation Rounds: {neg['negotiation_rounds']}")
            
            # Coalition members
            print(f"\n👥 Coalition Members:")
            for member in neg['coalition_members']:
                print(f"   • {member['prosumer_id']}: {member['capacity_kw']:.1f} kW @ ${member['price_mwh']:.2f}/MWh (Satisfaction: {member['satisfaction']:.1f})")
            
            # Optimization results
            opt = result['optimization']
            print(f"\n⚡ Optimization Results:")
            print(f"   Method: {opt['method'].replace('_', ' ').title()}")
            print(f"   Bid Capacity: {opt['bid_capacity_mw']:.2f} MW")
            print(f"   Bid Price: ${opt['bid_price_mwh']:.2f}/MWh")
            print(f"   Expected Profit: ${opt['expected_profit']:.2f}")
            
            # Final bid
            bid = result['final_bid']
            print(f"\n📝 Final VPP Bid:")
            print(f"   Bid ID: {bid['bid_id']}")
            print(f"   Capacity: {bid['total_capacity_mw']:.2f} MW")
            print(f"   Price: ${bid['bid_price_mwh']:.2f}/MWh")
            print(f"   Profit Margin: {bid['profit_margin']:.1%}")
            print(f"   Reliability Score: {bid['reliability_score']:.2f}")
            
            # Performance metrics
            metrics = result['metrics']
            print(f"\n📈 Performance Metrics:")
            print(f"   Capacity Utilization: {metrics['capacity_utilization']:.1%}")
            print(f"   Economic Efficiency: {metrics['economic_efficiency']:.1%}")
            print(f"   Prosumer Satisfaction: {metrics['prosumer_satisfaction']:.1%}")
            print(f"   Bid Competitiveness: {metrics['bid_competitiveness']:.1%}")
            
            # Economics breakdown
            total_cost = sum(opt['prosumer_payments'].values())
            revenue = bid['total_capacity_mw'] * bid['bid_price_mwh']
            
            print(f"\n💰 Economic Breakdown:")
            print(f"   Expected Revenue: ${revenue:.2f}")
            print(f"   Total Prosumer Costs: ${total_cost:.2f}")
            print(f"   VPP Profit: ${revenue - total_cost:.2f}")
            print(f"   Market Competitiveness: {((opportunity.market_price_mwh - bid['bid_price_mwh']) / opportunity.market_price_mwh) * 100:.1f}% below market")
            
        else:
            print("❌ Negotiation Status: FAILED")
            print(f"   Reason: {result.get('failure_reason', 'Unknown')}")
        
        # Execution log
        print(f"\n📋 Execution Summary:")
        log_entries = result['execution_log'][-8:]  # Last 8 entries
        for entry in log_entries:
            print(f"   • {entry}")
        
    except Exception as e:
        print(f"❌ Negotiation failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("                    Demo Completed")
    print("=" * 70)


def run_performance_comparison():
    """Run a performance comparison between different scenarios."""
    
    print("\n" + "=" * 70)
    print("               PERFORMANCE COMPARISON")
    print("=" * 70)
    
    scenarios = [
        ("High Market Price", 120.0),
        ("Medium Market Price", 80.0), 
        ("Low Market Price", 45.0)
    ]
    
    system = IntegratedNegotiationSystem()
    
    for scenario_name, market_price in scenarios:
        print(f"\n🔍 Testing Scenario: {scenario_name} (${market_price:.0f}/MWh)")
        print("-" * 40)
        
        # Create opportunity
        opportunity = DemoMarketOpportunity()
        opportunity.market_price_mwh = market_price
        opportunity.opportunity_id = f"test_{scenario_name.lower().replace(' ', '_')}"
        opportunity.required_capacity_mw = 0.015  # 15 kW for smaller test fleet
        
        # Create fleet
        fleet = [DemoProsumer(f"test_{i:03d}", 60 + i*5) for i in range(4)]
        
        # Market data
        market_data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'lmp': [market_price],
            'spin_price': [market_price * 0.15],
            'nonspin_price': [market_price * 0.08]
        })
        
        try:
            result = system.run_complete_negotiation_cycle(
                opportunity, fleet, market_data
            )
            
            if result['success']:
                neg = result['negotiation']
                opt = result['optimization']
                metrics = result['metrics']
                
                print(f"   ✅ Coalition: {neg['coalition_size']} prosumers, {neg['total_capacity_mw']:.2f} MW")
                print(f"   ✅ Bid Price: ${opt['bid_price_mwh']:.2f}/MWh ({metrics['bid_competitiveness']:.1%} below market)")
                print(f"   ✅ Profit: ${opt['expected_profit']:.2f} (Margin: {metrics['economic_efficiency']:.1%})")
                print(f"   ✅ Satisfaction: {metrics['prosumer_satisfaction']:.1%}")
            else:
                print(f"   ❌ Failed: {result.get('failure_reason', 'Unknown')}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


if __name__ == "__main__":
    run_demo()
    run_performance_comparison()
