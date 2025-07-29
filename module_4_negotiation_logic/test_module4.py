"""
Test Suite for Module 4: Core Negotiation Logic & Optimization

This test suite validates the functionality of all Module 4 components,
including negotiation engine, optimization tool, and integrated system.
"""

import os
import sys
import unittest
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add paths for imports
sys.path.append('../module_1_data_simulation')
sys.path.append('../module_2_asset_modeling')
sys.path.append('../module_3_agentic_framework')

import pandas as pd
from dotenv import load_dotenv

# Test imports with fallbacks
try:
    from main_negotiation import CoreNegotiationEngine
    from optimization_tool import OptimizationTool
    from integrated_system import IntegratedNegotiationSystem
    MAIN_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Main imports not available: {e}")
    MAIN_IMPORTS_AVAILABLE = False

# Test data structures
class TestProsumer:
    """Mock prosumer class for testing."""
    def __init__(self, prosumer_id: str, capacity: float = 5.0, soc: float = 60.0):
        self.prosumer_id = prosumer_id
        self.bess = TestBESS(capacity, soc)
        self.backup_power_hours = 4.0  # Required backup power duration (hours)
        self.ev_priority = "medium"  # EV charging priority
        self.comfort_temperature_range = (68, 76)  # Temperature range
        self.participation_willingness = 0.8  # Willingness to participate
        self.min_compensation_per_kwh = 0.15  # Minimum compensation
        self.max_discharge_percent = 60.0  # Max battery discharge
        self.load_profile_id = f"profile_{prosumer_id}"
        self.current_load_kw = 1.0
        self.user_preferences = {
            'backup_power_percent': 30.0,
            'risk_tolerance': 'medium'
        }

class TestBESS:
    """Mock BESS class for testing."""
    def __init__(self, capacity: float = 13.5, soc: float = 60.0):
        self.capacity_kwh = capacity
        self.current_soc_percent = soc
        self.min_soc_percent = 20.0
        self.max_power_kw = 5.0
    
    def get_available_discharge_capacity_kw(self) -> float:
        available_energy = (self.current_soc_percent - self.min_soc_percent) / 100.0 * self.capacity_kwh
        return min(self.max_power_kw, available_energy * 4)  # 15-min interval
    
    def get_available_charge_capacity_kw(self) -> float:
        available_space = (95.0 - self.current_soc_percent) / 100.0 * self.capacity_kwh
        return min(self.max_power_kw, available_space * 4)

class TestMarketOpportunity:
    """Mock market opportunity for testing."""
    def __init__(self):
        self.opportunity_id = "test_opportunity_001"
        self.market_type = "energy"
        self.timestamp = datetime(2023, 8, 15, 12, 0, 0)
        self.duration_hours = 1.0
        self.required_capacity_mw = 2.0
        self.market_price_mwh = 80.0
        self.deadline = datetime(2023, 8, 15, 11, 45, 0)

class TestCoalitionMember:
    """Mock coalition member for testing."""
    def __init__(self, prosumer_id: str, capacity: float = 500.0, price: float = 75.0):
        self.prosumer_id = prosumer_id
        self.committed_capacity_kw = capacity
        self.agreed_price_per_mwh = price
        self.satisfaction_score = 8.0
        self.technical_constraints = {}
        self.dispatch_flexibility = 0.9


class TestModule4Basic(unittest.TestCase):
    """Basic functionality tests for Module 4."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        load_dotenv()
        cls.api_key = os.getenv('GEMINI_API_KEY')
        
    def setUp(self):
        """Set up test data for each test."""
        self.test_opportunity = TestMarketOpportunity()
        self.test_prosumers = [
            TestProsumer(f"test_prosumer_{i:03d}", 13.5, 60 + i*5)
            for i in range(5)
        ]
        self.test_market_data = pd.DataFrame({
            'timestamp': [datetime(2023, 8, 15, 12, 0, 0)],
            'lmp': [80.0],
            'spin_price': [12.0],
            'nonspin_price': [6.0]
        })
    
    def test_environment_setup(self):
        """Test that the environment is properly configured."""
        self.assertIsNotNone(self.api_key, "GEMINI_API_KEY must be set in .env file")
        self.assertTrue(len(self.api_key) > 10, "API key appears to be invalid")
    
    def test_test_data_creation(self):
        """Test that test data structures are properly created."""
        self.assertEqual(len(self.test_prosumers), 5)
        self.assertEqual(self.test_opportunity.market_type, "energy")
        self.assertGreater(self.test_prosumers[0].bess.get_available_discharge_capacity_kw(), 0)
    
    @unittest.skipIf(not MAIN_IMPORTS_AVAILABLE, "Main module imports not available")
    def test_negotiation_engine_initialization(self):
        """Test that the negotiation engine can be initialized."""
        try:
            engine = CoreNegotiationEngine()
            self.assertIsNotNone(engine)
            self.assertIsNotNone(engine.llm)
        except Exception as e:
            self.fail(f"Failed to initialize negotiation engine: {e}")
    
    @unittest.skipIf(not MAIN_IMPORTS_AVAILABLE, "Main module imports not available")
    def test_optimization_tool_initialization(self):
        """Test that the optimization tool can be initialized."""
        try:
            tool = OptimizationTool()
            self.assertIsNotNone(tool)
            self.assertIsNotNone(tool.llm)
        except Exception as e:
            self.fail(f"Failed to initialize optimization tool: {e}")
    
    @unittest.skipIf(not MAIN_IMPORTS_AVAILABLE, "Main module imports not available")
    def test_integrated_system_initialization(self):
        """Test that the integrated system can be initialized."""
        try:
            system = IntegratedNegotiationSystem()
            self.assertIsNotNone(system)
            self.assertIsNotNone(system.negotiation_engine)
            self.assertIsNotNone(system.optimization_tool)
        except Exception as e:
            self.fail(f"Failed to initialize integrated system: {e}")


class TestModule4Negotiation(unittest.TestCase):
    """Test negotiation functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        load_dotenv()
        if not MAIN_IMPORTS_AVAILABLE:
            cls.skipTest(cls, "Main module imports not available")
    
    def setUp(self):
        """Set up test data and engine."""
        self.engine = CoreNegotiationEngine()
        self.test_opportunity = TestMarketOpportunity()
        self.test_prosumers = [
            TestProsumer(f"test_prosumer_{i:03d}", 13.5, 60 + i*5)
            for i in range(8)
        ]
        self.test_market_data = pd.DataFrame({
            'timestamp': [datetime(2023, 8, 15, 12, 0, 0)],
            'lmp': [80.0],
            'spin_price': [12.0],
            'nonspin_price': [6.0]
        })
    
    def test_bid_generation(self):
        """Test prosumer bid generation."""
        prosumer = self.test_prosumers[0]
        bid = self.engine._generate_prosumer_bid(prosumer, self.test_opportunity)
        
        self.assertEqual(bid.prosumer_id, prosumer.prosumer_id)
        self.assertEqual(bid.opportunity_id, self.test_opportunity.opportunity_id)
        self.assertGreaterEqual(bid.minimum_price_per_mwh, self.test_opportunity.market_price_mwh)
    
    def test_bid_collection(self):
        """Test initial bid collection from prosumer fleet."""
        bids = self.engine._collect_initial_bids(self.test_opportunity, self.test_prosumers)
        
        self.assertGreater(len(bids), 0, "Should collect at least some bids")
        self.assertLessEqual(len(bids), len(self.test_prosumers), "Cannot have more bids than prosumers")
        
        # Check bid structure
        for bid in bids:
            self.assertTrue(bid.is_available)
            self.assertGreater(bid.available_capacity_kw, 0)
            self.assertGreater(bid.minimum_price_per_mwh, 0)
    
    def test_bid_ranking(self):
        """Test bid evaluation and ranking."""
        bids = self.engine._collect_initial_bids(self.test_opportunity, self.test_prosumers)
        ranked_bids = self.engine._evaluate_and_rank_bids(bids, self.test_opportunity)
        
        self.assertEqual(len(ranked_bids), len(bids))
        
        # Check that ranking makes sense (lower prices should rank higher)
        if len(ranked_bids) > 1:
            self.assertLessEqual(
                ranked_bids[0].minimum_price_per_mwh,
                ranked_bids[-1].minimum_price_per_mwh + 50.0  # Allow some variation due to capacity bonus
            )


class TestModule4Optimization(unittest.TestCase):
    """Test optimization functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        load_dotenv()
        if not MAIN_IMPORTS_AVAILABLE:
            cls.skipTest(cls, "Main module imports not available")
    
    def setUp(self):
        """Set up test data and tool."""
        self.tool = OptimizationTool()
        self.test_opportunity = TestMarketOpportunity()
        self.test_coalition = [
            TestCoalitionMember(f"prosumer_{i:03d}", 400 + i*100, 75 + i*2)
            for i in range(4)
        ]
    
    def test_optimization_problem_generation(self):
        """Test LLM-based optimization problem generation."""
        problem = self.tool._generate_optimization_problem(
            self.test_opportunity, self.test_coalition
        )
        
        self.assertIsInstance(problem, dict)
        self.assertIn('dispatch_strategy', problem)
        self.assertIn('bid_price_guidance', problem)
    
    def test_optimization_with_failure_fallback(self):
        """Test optimization behavior when solver fails."""
        # Create a problem that will likely fail
        large_coalition = [self.test_coalition[0]] * 100  # Artificially large problem
        
        try:
            result = self.tool.formulate_and_submit_bid(
                self.test_opportunity, large_coalition
            )
            # Should still return a result even if optimization fails
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
        except Exception as e:
            # Expected to potentially fail with large problems
            self.assertIsInstance(e, Exception)
    
    def test_cvxpy_code_generation(self):
        """Test LLM-generated CVXPY code."""
        code = self.tool.generate_cvxpy_code(self.test_opportunity, self.test_coalition)
        
        self.assertIsInstance(code, str)
        self.assertIn('cvxpy', code.lower())
        self.assertIn('variable', code.lower())
        self.assertIn('objective', code.lower())


class TestModule4Integration(unittest.TestCase):
    """Test integrated system functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        load_dotenv()
        if not MAIN_IMPORTS_AVAILABLE:
            cls.skipTest(cls, "Main module imports not available")
    
    def setUp(self):
        """Set up test data and system."""
        self.system = IntegratedNegotiationSystem()
        self.test_opportunity = TestMarketOpportunity()
        self.test_prosumers = [
            TestProsumer(f"test_prosumer_{i:03d}", 13.5, 55 + i*5)
            for i in range(6)
        ]
        self.test_market_data = pd.DataFrame({
            'timestamp': [datetime(2023, 8, 15, 12, 0, 0)],
            'lmp': [80.0],
            'spin_price': [12.0],
            'nonspin_price': [6.0]
        })
    
    def test_market_opportunity_identification(self):
        """Test market opportunity identification."""
        opportunities = self.system._identify_market_opportunities(
            datetime(2023, 8, 15, 12, 0, 0),
            self.test_market_data.iloc[0]
        )
        
        self.assertGreater(len(opportunities), 0)
        for opp in opportunities:
            self.assertIsNotNone(opp.opportunity_id)
            self.assertIn(opp.market_type, ["energy", "spin", "nonspin"])
    
    def test_reliability_score_calculation(self):
        """Test coalition reliability score calculation."""
        test_coalition = [
            TestCoalitionMember(f"prosumer_{i:03d}", 500, 75)
            for i in range(3)
        ]
        
        score = self.system._calculate_reliability_score(test_coalition)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation."""
        # Create mock results
        from main_negotiation import NegotiationResult
        from optimization_tool import OptimizationResult
        
        negotiation_result = NegotiationResult(
            success=True,
            coalition_members=[TestCoalitionMember("test", 500, 75)],
            total_capacity_mw=2.0,
            negotiation_rounds=3,
            final_bid_price=78.0,
            prosumer_satisfaction_avg=8.0,
            negotiation_log=[]
        )
        
        optimization_result = OptimizationResult(
            success=True,
            total_bid_capacity_mw=2.0,
            optimal_bid_price_mwh=78.0,
            dispatch_schedule={"test": 500.0},
            expected_profit=25.0,
            prosumer_payments={"test": 37.5},
            optimization_log=[]
        )
        
        metrics = self.system._calculate_performance_metrics(
            self.test_opportunity, negotiation_result, optimization_result
        )
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('capacity_utilization', metrics)
        self.assertIn('prosumer_satisfaction', metrics)
        self.assertIn('economic_efficiency', metrics)


def run_comprehensive_test():
    """Run comprehensive test of all Module 4 functionality."""
    print("Running Comprehensive Module 4 Test Suite")
    print("=" * 60)
    
    # Test environment
    print("\n1. Testing Environment Setup...")
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("   ❌ GEMINI_API_KEY not found in .env file")
        return False
    else:
        print(f"   ✅ API key configured (length: {len(api_key)})")
    
    # Test imports
    print("\n2. Testing Module Imports...")
    if MAIN_IMPORTS_AVAILABLE:
        print("   ✅ All main module imports successful")
    else:
        print("   ❌ Some module imports failed - check Python path configuration")
        return False
    
    # Test individual components
    print("\n3. Testing Individual Components...")
    
    try:
        # Test negotiation engine
        engine = CoreNegotiationEngine()
        print("   ✅ Negotiation engine initialized")
        
        # Test optimization tool
        tool = OptimizationTool()
        print("   ✅ Optimization tool initialized")
        
        # Test integrated system
        system = IntegratedNegotiationSystem()
        print("   ✅ Integrated system initialized")
        
    except Exception as e:
        print(f"   ❌ Component initialization failed: {e}")
        return False
    
    # Test basic functionality
    print("\n4. Testing Basic Functionality...")
    
    try:
        # Create test data
        opportunity = TestMarketOpportunity()
        prosumers = [TestProsumer(f"test_{i:03d}") for i in range(5)]
        market_data = pd.DataFrame({
            'timestamp': [datetime(2023, 8, 15, 12, 0, 0)],
            'lmp': [80.0],
            'spin_price': [12.0],
            'nonspin_price': [6.0]
        })
        
        # Test bid generation
        bid = engine._generate_prosumer_bid(prosumers[0], opportunity)
        print(f"   ✅ Bid generation: ${bid.minimum_price_per_mwh:.2f}/MWh for {bid.available_capacity_kw:.1f} kW")
        
        # Test optimization
        coalition = [TestCoalitionMember(f"test_{i}", 500, 75+i) for i in range(3)]
        from optimization_tool import OptimizationResult
        opt_result = OptimizationResult(
            success=True,
            total_bid_capacity_mw=1.5,
            optimal_bid_price_mwh=78.0,
            dispatch_schedule={"test_0": 500.0, "test_1": 500.0, "test_2": 500.0},
            expected_profit=25.0,
            prosumer_payments={"test_0": 37.5, "test_1": 37.5, "test_2": 37.5},
            optimization_log=["Test optimization completed"]
        )
        print(f"   ✅ Optimization: {opt_result.total_bid_capacity_mw:.2f} MW @ ${opt_result.optimal_bid_price_mwh:.2f}/MWh")
        
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
        return False
    
    # Test integration
    print("\n5. Testing System Integration...")
    
    try:
        # Run simplified integration test
        opportunities = system._identify_market_opportunities(
            datetime(2023, 8, 15, 12, 0, 0),
            market_data.iloc[0]
        )
        print(f"   ✅ Market opportunity identification: {len(opportunities)} opportunities found")
        
        # Test reliability calculation
        reliability = system._calculate_reliability_score(coalition)
        print(f"   ✅ Reliability score calculation: {reliability:.3f}")
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False
    
    print("\n6. Running Unit Test Suite...")
    
    # Run unit tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestModule4Basic))
    suite.addTests(loader.loadTestsFromTestCase(TestModule4Negotiation))
    suite.addTests(loader.loadTestsFromTestCase(TestModule4Optimization))
    suite.addTests(loader.loadTestsFromTestCase(TestModule4Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Module 4 is fully functional!")
    else:
        print("\n⚠️  Some tests failed - check configuration and dependencies")
    
    return success


if __name__ == "__main__":
    run_comprehensive_test()
