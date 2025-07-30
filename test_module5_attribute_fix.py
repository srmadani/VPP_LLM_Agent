#!/usr/bin/env python3
"""
Quick test to verify Module 5 attribute fix works correctly
"""

import sys
import os
from pathlib import Path

def test_module5_attribute_fix():
    """Test that Module 5 works after the attribute fix."""
    print("Testing Module 5 attribute fix...")
    
    try:
        # Add paths like the dashboard does
        base_path = Path(__file__).parent
        module_5_path = str(base_path / 'module_5_simulation_orchestration')
        module_4_path = str(base_path / 'module_4_negotiation_logic')
        module_3_path = str(base_path / 'module_3_agentic_framework')
        module_2_path = str(base_path / 'module_2_asset_modeling')
        module_1_path = str(base_path / 'module_1_data_simulation')
        
        for path in [module_5_path, module_4_path, module_3_path, module_2_path, module_1_path]:
            if path in sys.path:
                sys.path.remove(path)
            sys.path.insert(0, path)
        
        # Import and test
        from simulation import VPPSimulationOrchestrator
        
        print("✅ Import successful")
        
        # Test with correct data path (like the dashboard now does)
        module_1_data_path = str(base_path / 'module_1_data_simulation' / 'data')
        print(f"Using data path: {module_1_data_path}")
        
        # Initialize orchestrator with explicit path
        orchestrator = VPPSimulationOrchestrator(data_path=module_1_data_path)
        print("✅ VPPSimulationOrchestrator initialized successfully!")
        
        # Test a small simulation to verify the attributes work
        print("🧪 Testing small simulation (5 prosumers, 2 hours)...")
        summary = orchestrator.run_full_simulation(
            fleet_size=5,
            duration_hours=2,
            opportunity_frequency_hours=1
        )
        print("✅ Small simulation completed!")
        
        # Test the attributes that the dashboard accesses
        print("🔍 Testing SimulationSummary attributes...")
        test_attributes = [
            'total_timesteps',
            'agentic_total_profit',
            'centralized_total_profit', 
            'satisfaction_advantage_percent',
            'agentic_success_rate'
        ]
        
        for attr in test_attributes:
            if hasattr(summary, attr):
                value = getattr(summary, attr)
                print(f"   ✅ {attr}: {value}")
            else:
                print(f"   ❌ {attr}: MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("VPP Module 5 Attribute Fix Verification")
    print("=" * 50)
    
    success = test_module5_attribute_fix()
    
    if success:
        print("\n🎉 Module 5 attribute fix is working!")
        print("Dashboard should now be able to run Module 5 simulations without attribute errors.")
    else:
        print("\n💥 Module 5 still has issues.")
