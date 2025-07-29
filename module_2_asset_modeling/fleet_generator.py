"""
Fleet Generator for VPP LLM Agent - Module 2

This module generates realistic fleets of prosumers with diverse asset characteristics
and assigns load profiles from Module 1 data.
"""

import pandas as pd
import numpy as np
import random
import os
from typing import List, Dict, Any
from prosumer_models import Prosumer, BESS, ElectricVehicle, SolarPV


class FleetGenerator:
    """
    Generates diverse fleets of prosumers with realistic asset distributions.
    """
    
    def __init__(self, data_path: str = "../module_1_data_simulation/data"):
        """
        Initialize fleet generator with data from Module 1.
        
        Args:
            data_path: Path to Module 1 data directory
        """
        self.data_path = data_path
        self.load_profiles = self._load_profile_data()
        self.solar_data = self._load_solar_data()
        
        # Asset distribution parameters (based on California residential data)
        self.asset_probabilities = {
            "has_bess": 0.35,  # 35% have battery storage
            "has_ev": 0.45,    # 45% have electric vehicles
            "has_solar": 0.55  # 55% have solar panels
        }
        
        # BESS specifications (realistic residential systems)
        self.bess_configs = [
            {"capacity_kwh": 5.0, "max_power_kw": 3.0, "weight": 0.15},    # Small
            {"capacity_kwh": 10.0, "max_power_kw": 5.0, "weight": 0.35},   # Medium  
            {"capacity_kwh": 13.5, "max_power_kw": 7.0, "weight": 0.25},   # Tesla Powerwall 2
            {"capacity_kwh": 16.0, "max_power_kw": 8.0, "weight": 0.15},   # Large
            {"capacity_kwh": 20.0, "max_power_kw": 10.0, "weight": 0.10}   # Very Large
        ]
        
        # EV specifications (common EV models)
        self.ev_configs = [
            {"battery_capacity_kwh": 40.0, "max_charge_power_kw": 7.2, "weight": 0.25},   # Nissan Leaf
            {"battery_capacity_kwh": 64.0, "max_charge_power_kw": 11.0, "weight": 0.20},  # Chevy Bolt
            {"battery_capacity_kwh": 75.0, "max_charge_power_kw": 11.5, "weight": 0.30},  # Tesla Model 3
            {"battery_capacity_kwh": 82.0, "max_charge_power_kw": 11.5, "weight": 0.15},  # Tesla Model Y
            {"battery_capacity_kwh": 100.0, "max_charge_power_kw": 11.5, "weight": 0.10}  # Tesla Model S
        ]
        
        # Solar system sizes (kW)
        self.solar_configs = [
            {"capacity_kw": 4.0, "weight": 0.20},   # Small system
            {"capacity_kw": 6.0, "weight": 0.30},   # Medium system
            {"capacity_kw": 8.0, "weight": 0.25},   # Large system
            {"capacity_kw": 10.0, "weight": 0.15},  # Very large system
            {"capacity_kw": 12.0, "weight": 0.10}   # Premium system
        ]
    
    def _load_profile_data(self) -> List[pd.DataFrame]:
        """Load all load profile CSV files."""
        profiles = []
        profile_dir = os.path.join(self.data_path, "load_profiles")
        
        if not os.path.exists(profile_dir):
            raise FileNotFoundError(f"Load profiles directory not found: {profile_dir}")
        
        profile_files = [f for f in os.listdir(profile_dir) if f.endswith('.csv')]
        profile_files.sort()  # Ensure consistent ordering
        
        for file in profile_files:
            file_path = os.path.join(profile_dir, file)
            df = pd.read_csv(file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            profiles.append(df)
        
        return profiles
    
    def _load_solar_data(self) -> pd.DataFrame:
        """Load solar generation data."""
        solar_file = os.path.join(self.data_path, "solar_data.csv")
        
        if not os.path.exists(solar_file):
            raise FileNotFoundError(f"Solar data file not found: {solar_file}")
        
        df = pd.read_csv(solar_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def _weighted_choice(self, choices: List[Dict[str, Any]], weight_key: str = 'weight') -> Dict[str, Any]:
        """Make a weighted random choice from list of dictionaries."""
        weights = [choice[weight_key] for choice in choices]
        return random.choices(choices, weights=weights)[0]
    
    def _generate_user_preferences(self) -> Dict[str, Any]:
        """Generate realistic user preferences."""
        # Preference profiles with different risk tolerance and participation levels
        preference_profiles = [
            {  # Conservative
                "backup_power_hours": random.uniform(6, 12),
                "participation_willingness": random.uniform(0.3, 0.6),
                "min_compensation_per_kwh": random.uniform(0.20, 0.35),
                "max_discharge_percent": random.uniform(30, 50),
                "ev_priority": random.choice(["high", "medium"])
            },
            {  # Moderate
                "backup_power_hours": random.uniform(3, 8),
                "participation_willingness": random.uniform(0.6, 0.8),
                "min_compensation_per_kwh": random.uniform(0.12, 0.25),
                "max_discharge_percent": random.uniform(50, 70),
                "ev_priority": random.choice(["medium", "medium", "low"])
            },
            {  # Aggressive
                "backup_power_hours": random.uniform(1, 4),
                "participation_willingness": random.uniform(0.8, 0.95),
                "min_compensation_per_kwh": random.uniform(0.08, 0.18),
                "max_discharge_percent": random.uniform(70, 85),
                "ev_priority": random.choice(["low", "medium"])
            }
        ]
        
        return random.choice(preference_profiles)
    
    def _generate_ev_charging_schedule(self) -> str:
        """Generate realistic EV charging deadline (departure time)."""
        # Most people leave between 6-9 AM
        hour = random.choice([6, 7, 7, 7, 8, 8, 9])  # Weighted towards 7-8 AM
        minute = random.choice([0, 15, 30, 45])
        return f"{hour:02d}:{minute:02d}"
    
    def create_prosumer_fleet(self, n: int, random_seed: int = 42) -> List[Prosumer]:
        """
        Generate a fleet of n prosumers with diverse characteristics.
        
        Args:
            n: Number of prosumers to generate
            random_seed: Random seed for reproducible results
            
        Returns:
            List of Prosumer objects
        """
        random.seed(random_seed)
        np.random.seed(random_seed)
        
        if n > len(self.load_profiles):
            raise ValueError(f"Requested {n} prosumers, but only {len(self.load_profiles)} load profiles available")
        
        fleet = []
        
        for i in range(n):
            prosumer_id = f"prosumer_{i+1:03d}"
            
            # Assign load profile (round-robin to ensure diversity)
            profile_idx = i % len(self.load_profiles)
            load_profile_id = f"profile_{profile_idx + 1}"
            
            # Generate user preferences
            preferences = self._generate_user_preferences()
            
            # Determine which assets this prosumer has
            has_bess = random.random() < self.asset_probabilities["has_bess"]
            has_ev = random.random() < self.asset_probabilities["has_ev"]
            has_solar = random.random() < self.asset_probabilities["has_solar"]
            
            # Generate BESS if applicable
            bess = None
            if has_bess:
                bess_config = self._weighted_choice(self.bess_configs)
                bess = BESS(
                    capacity_kwh=bess_config["capacity_kwh"],
                    max_power_kw=bess_config["max_power_kw"],
                    current_soc_percent=random.uniform(40, 80),  # Start with varied SOC
                    min_soc_percent=random.uniform(5, 15),
                    max_soc_percent=random.uniform(90, 98)
                )
            
            # Generate EV if applicable
            ev = None
            if has_ev:
                ev_config = self._weighted_choice(self.ev_configs)
                ev = ElectricVehicle(
                    battery_capacity_kwh=ev_config["battery_capacity_kwh"],
                    max_charge_power_kw=ev_config["max_charge_power_kw"],
                    current_soc_percent=random.uniform(60, 85),
                    min_departure_soc_percent=random.uniform(75, 90),
                    charge_deadline=self._generate_ev_charging_schedule(),
                    is_plugged_in=random.random() < 0.8  # 80% are plugged in
                )
            
            # Generate Solar PV if applicable
            solar = None
            if has_solar:
                solar_config = self._weighted_choice(self.solar_configs)
                solar = SolarPV(
                    capacity_kw=solar_config["capacity_kw"],
                    efficiency=random.uniform(0.80, 0.90)
                )
            
            # Create prosumer
            prosumer = Prosumer(
                prosumer_id=prosumer_id,
                location="Los Angeles, CA",
                bess=bess,
                ev=ev,
                solar=solar,
                load_profile_id=load_profile_id,
                **preferences
            )
            
            fleet.append(prosumer)
        
        return fleet
    
    def get_fleet_statistics(self, fleet: List[Prosumer]) -> Dict[str, Any]:
        """
        Generate statistics about the fleet composition.
        
        Args:
            fleet: List of Prosumer objects
            
        Returns:
            Dict with fleet statistics
        """
        stats = {
            "total_prosumers": len(fleet),
            "asset_counts": {
                "bess": sum(1 for p in fleet if p.bess is not None),
                "ev": sum(1 for p in fleet if p.ev is not None),
                "solar": sum(1 for p in fleet if p.solar is not None)
            },
            "asset_percentages": {},
            "total_capacities": {
                "bess_kwh": sum(p.bess.capacity_kwh for p in fleet if p.bess),
                "ev_kwh": sum(p.ev.battery_capacity_kwh for p in fleet if p.ev),
                "solar_kw": sum(p.solar.capacity_kw for p in fleet if p.solar),
                "bess_power_kw": sum(p.bess.max_power_kw for p in fleet if p.bess)
            },
            "participation_stats": {
                "mean_willingness": np.mean([p.participation_willingness for p in fleet]),
                "mean_min_compensation": np.mean([p.min_compensation_per_kwh for p in fleet]),
                "mean_backup_hours": np.mean([p.backup_power_hours for p in fleet])
            }
        }
        
        # Calculate percentages
        for asset in stats["asset_counts"]:
            stats["asset_percentages"][asset] = (stats["asset_counts"][asset] / len(fleet)) * 100
        
        return stats
    
    def export_fleet_summary(self, fleet: List[Prosumer], output_file: str = "fleet_summary.csv") -> None:
        """
        Export fleet summary to CSV for analysis.
        
        Args:
            fleet: List of Prosumer objects
            output_file: Output CSV filename
        """
        data = []
        
        for prosumer in fleet:
            row = {
                "prosumer_id": prosumer.prosumer_id,
                "load_profile_id": prosumer.load_profile_id,
                "has_bess": prosumer.bess is not None,
                "has_ev": prosumer.ev is not None,
                "has_solar": prosumer.solar is not None,
                "participation_willingness": prosumer.participation_willingness,
                "min_compensation_per_kwh": prosumer.min_compensation_per_kwh,
                "backup_power_hours": prosumer.backup_power_hours,
                "max_discharge_percent": prosumer.max_discharge_percent
            }
            
            if prosumer.bess:
                row.update({
                    "bess_capacity_kwh": prosumer.bess.capacity_kwh,
                    "bess_max_power_kw": prosumer.bess.max_power_kw,
                    "bess_initial_soc": prosumer.bess.current_soc_percent
                })
            
            if prosumer.ev:
                row.update({
                    "ev_battery_kwh": prosumer.ev.battery_capacity_kwh,
                    "ev_max_charge_kw": prosumer.ev.max_charge_power_kw,
                    "ev_departure_time": prosumer.ev.charge_deadline,
                    "ev_min_departure_soc": prosumer.ev.min_departure_soc_percent
                })
            
            if prosumer.solar:
                row.update({
                    "solar_capacity_kw": prosumer.solar.capacity_kw,
                    "solar_efficiency": prosumer.solar.efficiency
                })
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f"Fleet summary exported to {output_file}")


def main():
    """Example usage of the fleet generator."""
    # Initialize generator
    generator = FleetGenerator()
    
    # Create a fleet of 20 prosumers
    fleet = generator.create_prosumer_fleet(n=20)
    
    # Print fleet statistics
    stats = generator.get_fleet_statistics(fleet)
    print("Fleet Statistics:")
    print(f"Total Prosumers: {stats['total_prosumers']}")
    print(f"BESS: {stats['asset_counts']['bess']} ({stats['asset_percentages']['bess']:.1f}%)")
    print(f"EVs: {stats['asset_counts']['ev']} ({stats['asset_percentages']['ev']:.1f}%)")
    print(f"Solar: {stats['asset_counts']['solar']} ({stats['asset_percentages']['solar']:.1f}%)")
    print(f"Total BESS Capacity: {stats['total_capacities']['bess_kwh']:.1f} kWh")
    print(f"Total Solar Capacity: {stats['total_capacities']['solar_kw']:.1f} kW")
    print(f"Mean Participation Willingness: {stats['participation_stats']['mean_willingness']:.2f}")
    
    # Export fleet summary
    generator.export_fleet_summary(fleet)
    
    # Test individual prosumer
    prosumer = fleet[0]
    print(f"\nSample Prosumer ({prosumer.prosumer_id}):")
    print(f"Assets: BESS={prosumer.bess is not None}, EV={prosumer.ev is not None}, Solar={prosumer.solar is not None}")
    if prosumer.bess:
        print(f"BESS: {prosumer.bess.capacity_kwh} kWh, {prosumer.bess.max_power_kw} kW")
    
    # Test market opportunity evaluation
    opportunity = prosumer.evaluate_market_opportunity(price_per_mwh=120.0)
    print(f"Market Opportunity Response: {opportunity}")


if __name__ == "__main__":
    main()
