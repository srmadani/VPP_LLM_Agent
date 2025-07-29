"""
Demo Module 6: VPP Visualization Dashboard

This script demonstrates the key features and capabilities of the dashboard.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import json

def demo_dashboard_features():
    """Demonstrate dashboard features with sample data."""
    print("=" * 60)
    print("VPP DASHBOARD FEATURES DEMONSTRATION")
    print("=" * 60)
    
    # Load and display sample data
    base_path = Path(__file__).parent.parent
    
    print("\n📊 LOADING SIMULATION DATA...")
    results_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_results.csv"
    results_df = pd.read_csv(results_path)
    
    summary_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_summary.json"
    with open(summary_path, 'r') as f:
        summary = json.load(f)
    
    market_path = base_path / "module_1_data_simulation" / "data" / "market_data.csv"
    market_df = pd.read_csv(market_path)
    
    print(f"✅ Simulation Results: {len(results_df)} timesteps")
    print(f"✅ Market Data: {len(market_df)} price points")
    print(f"✅ Summary Metrics: {len(summary)} KPIs")
    
    print("\n📈 KEY PERFORMANCE INDICATORS:")
    print("-" * 40)
    
    # Display key metrics
    agentic_profit = summary.get('agentic_total_profit', 0)
    centralized_profit = summary.get('centralized_total_profit', 0)
    satisfaction_advantage = summary.get('satisfaction_advantage_percent', 0)
    
    print(f"💰 Profit Comparison:")
    print(f"   Agentic Model:     ${agentic_profit:.2f}")
    print(f"   Centralized Model: ${centralized_profit:.2f}")
    print(f"   Difference:        ${agentic_profit - centralized_profit:.2f}")
    
    print(f"\n😊 Satisfaction Analysis:")
    agentic_satisfaction = summary.get('agentic_avg_satisfaction', 0)
    centralized_satisfaction = summary.get('centralized_avg_satisfaction', 0)
    
    print(f"   Agentic Satisfaction:     {agentic_satisfaction:.1f}/10")
    print(f"   Centralized Satisfaction: {centralized_satisfaction:.1f}/10")
    print(f"   Advantage:                {satisfaction_advantage:.0f}%")
    
    print(f"\n⚡ Efficiency Metrics:")
    print(f"   Success Rate (Agentic):    {summary.get('agentic_success_rate', 0)*100:.1f}%")
    print(f"   Success Rate (Centralized): {summary.get('centralized_success_rate', 0)*100:.1f}%")
    print(f"   Avg Coalition Size:        {summary.get('agentic_avg_coalition_size', 0):.1f} prosumers")
    print(f"   Avg Negotiation Rounds:    {summary.get('agentic_avg_negotiation_rounds', 0):.1f}")
    
    print("\n🏠 MARKET ANALYSIS:")
    print("-" * 40)
    
    print(f"💹 CAISO Market Prices:")
    print(f"   LMP Average:      ${market_df['lmp'].mean():.2f}/MWh")
    print(f"   LMP Range:        ${market_df['lmp'].min():.2f} - ${market_df['lmp'].max():.2f}")
    print(f"   SPIN Average:     ${market_df['spin_price'].mean():.2f}/MWh")
    print(f"   NONSPIN Average:  ${market_df['nonspin_price'].mean():.2f}/MWh")
    
    print("\n🎯 VALUE PROPOSITION:")
    print("-" * 40)
    
    print("✅ Prosumer Satisfaction: The agentic model achieved significantly")
    print("   higher satisfaction by respecting individual preferences")
    
    print("✅ Preference Handling: Zero preference violations vs multiple")
    print("   violations in the centralized approach")
    
    print("✅ Real-world Viability: The agentic model is superior for")
    print("   deployment despite slightly lower theoretical profits")
    
    print("✅ Negotiation Intelligence: Multi-round strategic negotiation")
    print("   with coalition formation capabilities")
    
    print("\n🚀 DASHBOARD FEATURES:")
    print("-" * 40)
    
    features = [
        "📊 Interactive Performance Comparison Charts",
        "💹 Real-time Market Price Analysis",
        "🤝 Negotiation Process Visualization",
        "🏠 Natural Language Prosumer Creator",
        "🤖 AI-Powered Results Analysis",
        "📋 Detailed Simulation Logs & Reports",
        "📈 Downloadable Data Exports",
        "⚡ Responsive Real-time Interface"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n🎉 READY TO LAUNCH!")
    print("-" * 40)
    print("To start the dashboard, run:")
    print("   cd module_6_visualization_dashboard")
    print("   streamlit run dashboard.py")
    print("\nThe dashboard will be available at: http://localhost:8501")

def demo_prosumer_parsing():
    """Demonstrate prosumer parsing functionality."""
    print("\n" + "=" * 60)
    print("PROSUMER PARSING DEMONSTRATION")
    print("=" * 60)
    
    sample_descriptions = [
        "A tech-savvy user with a 15kWh Tesla Powerwall and an EV that must be charged by 7 AM",
        "Environmentally conscious homeowner with 8kW solar panels and a small 5kWh home battery",
        "Family with two electric vehicles and a large 20kWh battery system for backup power",
        "Senior citizen with medical equipment requiring 24/7 power and minimal disruption"
    ]
    
    print("\n📝 Sample Prosumer Descriptions:")
    for i, desc in enumerate(sample_descriptions, 1):
        print(f"\n{i}. {desc}")
    
    print("\n🔧 Expected Parsing Output Format:")
    sample_config = {
        "prosumer_id": "prosumer_001",
        "bess_capacity_kwh": 15.0,
        "bess_max_power_kw": 7.0,
        "bess_efficiency": 0.95,
        "has_solar": True,
        "solar_capacity_kw": 8.0,
        "has_ev": True,
        "ev_capacity_kwh": 75.0,
        "ev_charge_deadline": "07:00",
        "ev_target_soc_percent": 80,
        "preferences": {
            "backup_reserve_percent": 30,
            "disruption_tolerance": "low",
            "environmental_priority": "high"
        }
    }
    
    print(json.dumps(sample_config, indent=2))
    
    print("\n💡 This demonstrates the LLM's ability to:")
    print("   - Parse natural language descriptions")
    print("   - Extract technical specifications")
    print("   - Identify user preferences and constraints")
    print("   - Convert to structured data for simulation")

if __name__ == "__main__":
    demo_dashboard_features()
    demo_prosumer_parsing()
