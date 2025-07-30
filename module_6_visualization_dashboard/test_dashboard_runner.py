#!/usr/bin/env python3
"""
Test the actual dashboard Module 1 runner functionality.
"""

import sys
from pathlib import Path

# Add dashboard parent path
sys.path.insert(0, str(Path(__file__).parent))

# Import the dashboard module runner
from dashboard import ModuleRunner

print("=" * 60)
print("DASHBOARD MODULE 1 RUNNER TEST")
print("=" * 60)

try:
    # Initialize module runner
    base_path = Path(__file__).parent.parent
    runner = ModuleRunner(base_path)
    print("✅ ModuleRunner initialized successfully")
    
    # Test Module 1 execution
    print("\n🔄 Running Module 1 through dashboard runner...")
    result = runner.run_module_1(
        start_date='2023-08-01',
        end_date='2023-08-02',
        num_profiles=10
    )
    
    # Check result
    if result['status'] == 'success':
        print("✅ Module 1 executed successfully!")
        print(f"   Market records: {result['market_records']}")
        print(f"   Solar records: {result['solar_records']}")
        print(f"   Load profiles: {result['load_profiles_generated']}")
        print(f"   Message: {result['message']}")
    else:
        print(f"❌ Module 1 failed: {result['message']}")
        if 'traceback' in result:
            print("Traceback:")
            print(result['traceback'])
    
    print("\n" + "=" * 60)
    if result['status'] == 'success':
        print("✅ DASHBOARD MODULE 1 RUNNER TEST PASSED")
        print("The dashboard should now work correctly for Module 1!")
    else:
        print("❌ DASHBOARD MODULE 1 RUNNER TEST FAILED")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Runner test failed: {e}")
    import traceback
    traceback.print_exc()
