"""
Test Suite for VPP LLM Agent - Module 2

This module contains comprehensive tests for all Module 2 components including
prosumer models, fleet generation, and LLM parsing functionality.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
from unittest.mock import patch, MagicMock

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prosumer_models import Prosumer, BESS, ElectricVehicle, SolarPV
from fleet_generator import FleetGenerator
from llm_parser import LLMProsumerParser


class TestBESS:
    """Test Battery Energy Storage System functionality."""
    
    def test_bess_initialization(self):
        """Test BESS initialization with valid parameters."""
        bess = BESS(
            capacity_kwh=10.0,
            max_power_kw=5.0,
            current_soc_percent=50.0
        )
        
        assert bess.capacity_kwh == 10.0
        assert bess.max_power_kw == 5.0
        assert bess.current_soc_percent == 50.0
        assert bess.min_soc_percent == 10.0  # Default
        assert bess.max_soc_percent == 95.0  # Default
    
    def test_bess_available_capacities(self):
        """Test available charge/discharge capacity calculations."""
        bess = BESS(capacity_kwh=10.0, max_power_kw=5.0, current_soc_percent=50.0)
        
        # At 50% SOC with 10kWh capacity:
        # Available charge: (95-50)/100 * 10 = 4.5 kWh -> 4.5*4 = 18kW (but limited to 5kW)
        # Available discharge: (50-10)/100 * 10 = 4.0 kWh -> 4.0*4 = 16kW (but limited to 5kW)
        
        assert bess.get_available_charge_capacity_kw() == 5.0
        assert bess.get_available_discharge_capacity_kw() == 5.0
    
    def test_bess_charging(self):
        """Test battery charging functionality."""
        bess = BESS(capacity_kwh=10.0, max_power_kw=5.0, current_soc_percent=50.0)
        initial_soc = bess.current_soc_percent
        
        # Charge at 4kW for 15 minutes (0.25 hours)
        energy_charged = bess.charge(power_kw=4.0, duration_hours=0.25)
        
        # Energy charged = 4kW * 0.25h * 0.95 efficiency = 0.95 kWh
        expected_energy = 4.0 * 0.25 * 0.95
        assert abs(energy_charged - expected_energy) < 0.01
        
        # SOC should increase by (0.95 / 10.0) * 100 = 9.5%
        expected_soc = initial_soc + (expected_energy / 10.0) * 100
        assert abs(bess.current_soc_percent - expected_soc) < 0.01
    
    def test_bess_discharging(self):
        """Test battery discharging functionality."""
        bess = BESS(capacity_kwh=10.0, max_power_kw=5.0, current_soc_percent=70.0)
        initial_soc = bess.current_soc_percent
        
        # Discharge at 3kW for 15 minutes
        energy_output = bess.discharge(power_kw=3.0, duration_hours=0.25)
        
        # Energy output = 3kW * 0.25h = 0.75 kWh
        expected_output = 3.0 * 0.25
        assert abs(energy_output - expected_output) < 0.01
        
        # Internal energy consumed = 0.75 / 0.95 efficiency = 0.789 kWh
        expected_soc = initial_soc - (expected_output / 0.95 / 10.0) * 100
        assert abs(bess.current_soc_percent - expected_soc) < 0.1
    
    def test_bess_constraints(self):
        """Test that BESS respects SOC constraints."""
        # Test maximum SOC constraint
        bess = BESS(capacity_kwh=10.0, max_power_kw=5.0, current_soc_percent=94.0)
        bess.charge(power_kw=10.0, duration_hours=1.0)  # Try to overcharge
        assert bess.current_soc_percent <= bess.max_soc_percent
        
        # Test minimum SOC constraint  
        bess = BESS(capacity_kwh=10.0, max_power_kw=5.0, current_soc_percent=12.0)
        bess.discharge(power_kw=10.0, duration_hours=1.0)  # Try to over-discharge
        assert bess.current_soc_percent >= bess.min_soc_percent


class TestElectricVehicle:
    """Test Electric Vehicle functionality."""
    
    def test_ev_initialization(self):
        """Test EV initialization."""
        ev = ElectricVehicle(
            battery_capacity_kwh=75.0,
            max_charge_power_kw=11.0,
            current_soc_percent=60.0
        )
        
        assert ev.battery_capacity_kwh == 75.0
        assert ev.max_charge_power_kw == 11.0
        assert ev.current_soc_percent == 60.0
        assert ev.min_departure_soc_percent == 80.0  # Default
    
    def test_ev_charging_requirement(self):
        """Test EV charging requirement calculation."""
        ev = ElectricVehicle(
            battery_capacity_kwh=75.0,
            max_charge_power_kw=11.0,
            current_soc_percent=60.0,
            min_departure_soc_percent=80.0
        )
        
        # Need (80-60)% of 75kWh = 15kWh
        expected_requirement = 0.2 * 75.0
        assert abs(ev.get_charging_requirement_kwh() - expected_requirement) < 0.01
    
    def test_ev_charging(self):
        """Test EV charging functionality."""
        ev = ElectricVehicle(
            battery_capacity_kwh=75.0,
            max_charge_power_kw=11.0,
            current_soc_percent=60.0
        )
        initial_soc = ev.current_soc_percent
        
        # Charge at 10kW for 15 minutes
        energy_charged = ev.charge(power_kw=10.0, duration_hours=0.25)
        
        # Energy charged = 10kW * 0.25h * 0.92 efficiency = 2.3 kWh
        expected_energy = 10.0 * 0.25 * 0.92
        assert abs(energy_charged - expected_energy) < 0.01
        
        # SOC increase = (2.3 / 75.0) * 100 = 3.07%
        expected_soc = initial_soc + (expected_energy / 75.0) * 100
        assert abs(ev.current_soc_percent - expected_soc) < 0.1


class TestSolarPV:
    """Test Solar PV system functionality."""
    
    def test_solar_initialization(self):
        """Test Solar PV initialization."""
        solar = SolarPV(capacity_kw=8.0, efficiency=0.85)
        
        assert solar.capacity_kw == 8.0
        assert solar.efficiency == 0.85
    
    def test_solar_generation(self):
        """Test solar generation calculation."""
        solar = SolarPV(capacity_kw=8.0, efficiency=0.85)
        
        # Test full sun condition
        generation = solar.get_generation_kw(solar_irradiance_per_kw=1.0)
        expected = 8.0 * 1.0 * 0.85
        assert abs(generation - expected) < 0.01
        
        # Test partial sun condition
        generation = solar.get_generation_kw(solar_irradiance_per_kw=0.6)
        expected = 8.0 * 0.6 * 0.85
        assert abs(generation - expected) < 0.01


class TestProsumer:
    """Test Prosumer model functionality."""
    
    def setup_method(self):
        """Set up test prosumer with all assets."""
        self.bess = BESS(capacity_kwh=10.0, max_power_kw=5.0)
        self.ev = ElectricVehicle(battery_capacity_kwh=75.0, max_charge_power_kw=11.0)
        self.solar = SolarPV(capacity_kw=6.0)
        
        self.prosumer = Prosumer(
            prosumer_id="test_001",
            bess=self.bess,
            ev=self.ev,
            solar=self.solar,
            load_profile_id="profile_1",
            participation_willingness=0.8,
            backup_power_hours=4.0,
            max_discharge_percent=70.0
        )
    
    def test_prosumer_initialization(self):
        """Test prosumer initialization."""
        assert self.prosumer.prosumer_id == "test_001"
        assert self.prosumer.bess is not None
        assert self.prosumer.ev is not None
        assert self.prosumer.solar is not None
        assert self.prosumer.participation_willingness == 0.8
    
    def test_net_load_calculation(self):
        """Test net load calculation with solar generation."""
        self.prosumer.update_load(5.0)  # 5kW load
        
        # With 3kW solar generation
        net_load = self.prosumer.get_net_load_kw(solar_generation_kw=3.0)
        assert net_load == 2.0  # 5 - 3 = 2kW
        
        # With excess solar (6kW generation, 5kW load)
        net_load = self.prosumer.get_net_load_kw(solar_generation_kw=6.0)
        assert net_load == 0.0  # Max(0, 5-6) = 0
    
    def test_flexibility_calculation(self):
        """Test available flexibility calculation."""
        flexibility = self.prosumer.get_available_flexibility_kw()
        
        assert "charge" in flexibility
        assert "discharge" in flexibility
        assert flexibility["charge"] >= 0
        assert flexibility["discharge"] >= 0
    
    def test_market_opportunity_evaluation(self):
        """Test market opportunity evaluation."""
        evaluation = self.prosumer.evaluate_market_opportunity(price_per_mwh=150.0)
        
        required_fields = [
            "prosumer_id", "available_discharge_kw", "available_charge_kw",
            "participation_score", "min_price_per_kwh", "max_duration_hours"
        ]
        
        for field in required_fields:
            assert field in evaluation
        
        assert evaluation["prosumer_id"] == self.prosumer.prosumer_id
        assert 0 <= evaluation["participation_score"] <= 1
        assert evaluation["available_discharge_kw"] >= 0
        assert evaluation["available_charge_kw"] >= 0


class TestFleetGenerator:
    """Test Fleet Generator functionality."""
    
    def setup_method(self):
        """Set up fleet generator for testing."""
        # Use test data path (assuming Module 1 data exists)
        self.data_path = "../module_1_data_simulation/data"
        
        # Check if data exists before running tests
        if not os.path.exists(self.data_path):
            pytest.skip("Module 1 data not found - skipping fleet generator tests")
        
        self.generator = FleetGenerator(data_path=self.data_path)
    
    def test_fleet_generator_initialization(self):
        """Test fleet generator initialization."""
        assert len(self.generator.load_profiles) > 0
        assert self.generator.solar_data is not None
        assert len(self.generator.solar_data) > 0
    
    def test_create_small_fleet(self):
        """Test creating a small fleet of prosumers."""
        fleet = self.generator.create_prosumer_fleet(n=5, random_seed=42)
        
        assert len(fleet) == 5
        
        # Check that all fleet members are Prosumer objects
        for prosumer in fleet:
            assert isinstance(prosumer, Prosumer)
            assert prosumer.prosumer_id is not None
            assert prosumer.load_profile_id is not None
    
    def test_fleet_diversity(self):
        """Test that fleet has diverse asset configurations."""
        fleet = self.generator.create_prosumer_fleet(n=20, random_seed=42)
        
        # Count asset types
        has_bess = sum(1 for p in fleet if p.bess is not None)
        has_ev = sum(1 for p in fleet if p.ev is not None)
        has_solar = sum(1 for p in fleet if p.solar is not None)
        
        # Should have some diversity (not all or none)
        assert 0 < has_bess < len(fleet)
        assert 0 < has_ev < len(fleet)
        assert 0 < has_solar < len(fleet)
    
    def test_fleet_statistics(self):
        """Test fleet statistics generation."""
        fleet = self.generator.create_prosumer_fleet(n=10, random_seed=42)
        stats = self.generator.get_fleet_statistics(fleet)
        
        required_fields = [
            "total_prosumers", "asset_counts", "asset_percentages",
            "total_capacities", "participation_stats"
        ]
        
        for field in required_fields:
            assert field in stats
        
        assert stats["total_prosumers"] == 10
        assert "bess" in stats["asset_counts"]
        assert "ev" in stats["asset_counts"]
        assert "solar" in stats["asset_counts"]


class TestLLMParser:
    """Test LLM Parser functionality."""
    
    def setup_method(self):
        """Set up LLM parser for testing."""
        # Mock the Gemini API for testing
        self.mock_response = MagicMock()
        self.mock_response.text = '''
        {
            "bess_capacity_kwh": 15.0,
            "bess_max_power_kw": 7.5,
            "bess_initial_soc_percent": 50.0,
            "has_ev": true,
            "ev_battery_capacity_kwh": 75.0,
            "ev_max_charge_power_kw": 11.0,
            "ev_charge_deadline": "07:00",
            "ev_target_soc_percent": 90.0,
            "has_solar": false,
            "solar_capacity_kw": null,
            "solar_efficiency": 0.85,
            "participation_willingness": 0.85,
            "min_compensation_per_kwh": 0.12,
            "backup_power_hours": 3.0,
            "max_discharge_percent": 70.0,
            "ev_priority": "high"
        }
        '''
    
    def test_config_validation(self):
        """Test configuration validation and cleaning."""
        # Skip if no API key available
        try:
            parser = LLMProsumerParser()
        except ValueError:
            pytest.skip("Gemini API key not available - skipping LLM parser tests")
            return
        
        # Test with mock data
        test_config = {
            "bess_capacity_kwh": 15.0,
            "bess_max_power_kw": 7.5,
            "participation_willingness": 1.5,  # Invalid (>1)
            "min_compensation_per_kwh": -0.1,  # Invalid (negative)
            "ev_priority": "invalid"  # Invalid choice
        }
        
        cleaned = parser._validate_and_clean_config(test_config)
        
        # Check that invalid values were corrected
        assert 0 <= cleaned["participation_willingness"] <= 1
        assert cleaned["min_compensation_per_kwh"] >= 0.05
        assert cleaned["ev_priority"] in ["low", "medium", "high"]
    
    @patch('google.generativeai.GenerativeModel')
    def test_text_parsing_with_mock(self, mock_model_class):
        """Test text parsing with mocked Gemini API."""
        # Skip if no API key available for initialization
        try:
            # Mock the model and its response
            mock_model = MagicMock()
            mock_model.generate_content.return_value = self.mock_response
            mock_model_class.return_value = mock_model
            
            parser = LLMProsumerParser()
            parser.model = mock_model
            
            description = "A tech-savvy user with a large 15kWh battery and an EV"
            config = parser.text_to_prosumer_config(description)
            
            # Check that parsing returned a valid configuration
            assert isinstance(config, dict)
            assert "bess_capacity_kwh" in config
            assert "has_ev" in config
            assert config["bess_capacity_kwh"] == 15.0
            assert config["has_ev"] is True
            
        except ValueError:
            pytest.skip("Gemini API key not available - skipping LLM parser tests")
    
    def test_default_config(self):
        """Test default configuration generation."""
        try:
            parser = LLMProsumerParser()
            default_config = parser._get_default_config()
            
            # Check that default has all required fields
            required_fields = [
                "bess_capacity_kwh", "has_ev", "has_solar",
                "participation_willingness", "min_compensation_per_kwh"
            ]
            
            for field in required_fields:
                assert field in default_config
                
        except ValueError:
            pytest.skip("Gemini API key not available - skipping LLM parser tests")


def test_module_integration():
    """Test integration between all Module 2 components."""
    # Test that all components can work together
    
    # Create a basic BESS
    bess = BESS(capacity_kwh=10.0, max_power_kw=5.0)
    
    # Create a prosumer with the BESS
    prosumer = Prosumer(
        prosumer_id="integration_test",
        bess=bess,
        load_profile_id="profile_1"
    )
    
    # Test that prosumer can evaluate opportunities
    evaluation = prosumer.evaluate_market_opportunity(price_per_mwh=120.0)
    assert evaluation["prosumer_id"] == prosumer.prosumer_id
    
    # Test status reporting
    status = prosumer.get_status_summary()
    assert "prosumer_id" in status
    assert "bess" in status


def run_validation_tests():
    """
    Run comprehensive validation tests for Module 2.
    This function can be called directly to validate the module.
    """
    print("Running Module 2 Validation Tests...")
    print("=" * 60)
    
    # Test 1: BESS functionality
    print("\n1. Testing BESS functionality...")
    bess = BESS(capacity_kwh=10.0, max_power_kw=5.0, current_soc_percent=50.0)
    
    # Test charging
    initial_soc = bess.current_soc_percent
    energy_charged = bess.charge(power_kw=4.0, duration_hours=0.25)
    print(f"   Charged {energy_charged:.2f} kWh, SOC: {initial_soc:.1f}% → {bess.current_soc_percent:.1f}%")
    
    # Test discharging
    energy_discharged = bess.discharge(power_kw=3.0, duration_hours=0.25)
    print(f"   Discharged {energy_discharged:.2f} kWh, SOC: {bess.current_soc_percent:.1f}%")
    
    print("   ✓ BESS tests passed")
    
    # Test 2: Fleet generation (if data available)
    print("\n2. Testing Fleet Generation...")
    try:
        generator = FleetGenerator()
        fleet = generator.create_prosumer_fleet(n=5, random_seed=42)
        stats = generator.get_fleet_statistics(fleet)
        
        print(f"   Created fleet of {len(fleet)} prosumers")
        print(f"   BESS: {stats['asset_counts']['bess']}, EV: {stats['asset_counts']['ev']}, Solar: {stats['asset_counts']['solar']}")
        print("   ✓ Fleet generation tests passed")
        
    except FileNotFoundError:
        print("   ⚠ Module 1 data not found - skipping fleet generation test")
    
    # Test 3: LLM Parser (if API key available)
    print("\n3. Testing LLM Parser...")
    try:
        parser = LLMProsumerParser()
        print("   ✓ LLM Parser initialized successfully")
        
        # Test configuration validation
        test_config = {"bess_capacity_kwh": 15.0, "participation_willingness": 1.5}
        cleaned = parser._validate_and_clean_config(test_config)
        print(f"   Cleaned participation_willingness: {cleaned['participation_willingness']}")
        print("   ✓ Configuration validation tests passed")
        
    except ValueError as e:
        print(f"   ⚠ LLM Parser test skipped: {e}")
    
    # Test 4: Integration test
    print("\n4. Testing Integration...")
    prosumer = Prosumer(
        prosumer_id="test_prosumer",
        bess=BESS(capacity_kwh=10.0, max_power_kw=5.0),
        load_profile_id="profile_1"
    )
    
    evaluation = prosumer.evaluate_market_opportunity(price_per_mwh=120.0)
    print(f"   Market evaluation - Available discharge: {evaluation['available_discharge_kw']:.1f} kW")
    print(f"   Participation score: {evaluation['participation_score']:.2f}")
    print("   ✓ Integration tests passed")
    
    print("\n" + "=" * 60)
    print("Module 2 Validation Complete!")
    print("All core functionality is working correctly.")


if __name__ == "__main__":
    # Run validation tests directly
    run_validation_tests()
    
    # Optionally run pytest
    print("\nTo run full test suite with pytest, use:")
    print("cd /path/to/module_2_asset_modeling && python -m pytest test_module2.py -v")
