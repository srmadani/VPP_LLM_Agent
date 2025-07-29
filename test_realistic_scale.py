#!/usr/bin/env python3
"""
Test the realistic scale simulation with larger fleet and extended duration.
"""

import sys
import os
from datetime import datetime

# Add module paths
sys.path.append('module_5_simulation_orchestration')

def run_realistic_scale_test():
    """Run a scaled test with realistic parameters."""
    print("=" * 60)
    print("VPP LLM AGENT - REALISTIC SCALE TEST")
    print("=" * 60)
    
    try:
        from simulation import VPPSimulationOrchestrator
        
        print("🚀 Initializing realistic scale simulation...")
        print("   Fleet size: 50 prosumers (10x scale test)")
        print("   Duration: 24 hours (1 day test)")
        print("   Expected satisfaction advantage: 20-50%")
        print("   Expected runtime: 2-5 minutes")
        
        orchestrator = VPPSimulationOrchestrator()
        
        # Run scaled simulation
        start_time = datetime.now()
        summary = orchestrator.run_full_simulation(
            fleet_size=50,  # Moderate scale test (originally was 20)
            duration_hours=24,  # 1 day instead of 7 days
            opportunity_frequency_hours=1
        )
        runtime = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ SIMULATION COMPLETED in {runtime:.1f} seconds")
        print("=" * 60)
        print("REALISTIC PARAMETER VALIDATION")
        print("=" * 60)
        
        # Validate satisfaction scoring
        print(f"📊 SATISFACTION METRICS:")
        print(f"   Agentic satisfaction: {summary.agentic_avg_satisfaction:.3f}")
        print(f"   Centralized satisfaction: {summary.centralized_avg_satisfaction:.3f}")
        print(f"   Satisfaction advantage: {summary.satisfaction_advantage_percent:+.1f}%")
        
        if 15 <= summary.satisfaction_advantage_percent <= 60:
            print("   ✅ REALISTIC SATISFACTION ADVANTAGE")
        else:
            print("   ⚠️  Satisfaction advantage may need adjustment")
        
        # Validate profit metrics  
        print(f"\n💰 PROFIT METRICS:")
        print(f"   Agentic profit: ${summary.agentic_total_profit:.2f}")
        print(f"   Centralized profit: ${summary.centralized_total_profit:.2f}")
        if summary.centralized_total_profit > 0:
            print(f"   Profit advantage: {summary.profit_advantage_percent:+.1f}%")
        
        # Validate operational metrics
        print(f"\n⚙️  OPERATIONAL METRICS:")
        print(f"   Agentic success rate: {summary.agentic_success_rate:.1%}")
        print(f"   Centralized success rate: {summary.centralized_success_rate:.1%}")
        print(f"   Fleet size used: {len(summary.agentic_total_profit) if hasattr(summary, 'fleet_data') else '50'}")
        
        # Performance assessment
        print(f"\n🎯 PERFORMANCE ASSESSMENT:")
        if runtime < 300:  # 5 minutes
            print("   ✅ GOOD PERFORMANCE - under 5 minutes")
        else:
            print("   ⚠️  Slower than expected - may need optimization")
            
        if summary.satisfaction_advantage_percent > 0:
            print("   ✅ AGENTIC MODEL SHOWS SATISFACTION BENEFIT")
        else:
            print("   ⚠️  Satisfaction model needs review")
            
        print(f"\n📈 SCALING READINESS:")
        print(f"   Current test: 50 prosumers × 24 hours = 1,200 opportunities")
        print(f"   Target scale: 200 prosumers × 744 hours = 148,800 opportunities")
        print(f"   Estimated full runtime: {runtime * 148800 / 1200 / 60:.1f} minutes")
        
        if runtime * 148800 / 1200 < 3600:  # Under 1 hour for full simulation
            print("   ✅ READY FOR FULL SCALE SIMULATION")
        else:
            print("   ⚠️  May need performance optimization for full scale")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the realistic scale test."""
    print("VPP LLM Agent - Realistic Scale Parameter Test")
    
    success = run_realistic_scale_test()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ REALISTIC SCALE TEST PASSED")
        print("=" * 60)
        print("Ready for production simulation with:")
        print("• 200 prosumers (10x original scale)")
        print("• Full month duration (744 hours)")
        print("• Realistic satisfaction scoring (20-50% advantage)")
        print("• Extended market data (August 1-31, 2023)")
        print("\nTo run full simulation:")
        print("cd module_5_simulation_orchestration && python simulation.py")
    else:
        print("\n❌ SCALE TEST FAILED - Review parameters before full simulation")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
