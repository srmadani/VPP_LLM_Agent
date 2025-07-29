"""
Prosumer Asset Models for VPP LLM Agent - Module 2

This module defines the core classes for modeling prosumer assets including
Battery Energy Storage Systems (BESS), Electric Vehicles (EVs), and Solar PV systems.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BESS(BaseModel):
    """
    Battery Energy Storage System (BESS) model with state tracking and constraints.
    
    This class models a residential battery system with realistic charge/discharge
    characteristics, efficiency losses, and operational constraints.
    """
    
    capacity_kwh: float = Field(..., description="Total battery capacity in kWh")
    max_power_kw: float = Field(..., description="Maximum charge/discharge power in kW")
    current_soc_percent: float = Field(default=50.0, description="Current State of Charge (%)")
    min_soc_percent: float = Field(default=10.0, description="Minimum allowed SOC (%)")
    max_soc_percent: float = Field(default=95.0, description="Maximum allowed SOC (%)")
    charge_efficiency: float = Field(default=0.95, description="Charging efficiency (0-1)")
    discharge_efficiency: float = Field(default=0.95, description="Discharging efficiency (0-1)")
    
    class Config:
        arbitrary_types_allowed = True
    
    def get_available_charge_capacity_kw(self) -> float:
        """Calculate available charging capacity in kW based on current SOC."""
        available_capacity_kwh = (self.max_soc_percent - self.current_soc_percent) / 100.0 * self.capacity_kwh
        return min(self.max_power_kw, available_capacity_kwh * 4)  # 4 = 1/(15min/60min)
    
    def get_available_discharge_capacity_kw(self) -> float:
        """Calculate available discharging capacity in kW based on current SOC."""
        available_capacity_kwh = (self.current_soc_percent - self.min_soc_percent) / 100.0 * self.capacity_kwh
        return min(self.max_power_kw, available_capacity_kwh * 4)  # 4 = 1/(15min/60min)
    
    def charge(self, power_kw: float, duration_hours: float = 0.25) -> float:
        """
        Charge the battery for the given power and duration.
        
        Args:
            power_kw: Charging power in kW (positive value)
            duration_hours: Charging duration in hours (default 0.25 for 15min intervals)
            
        Returns:
            float: Actual energy charged in kWh
        """
        if power_kw <= 0:
            return 0.0
            
        # Limit charging power to maximum and available capacity
        max_charge_power = min(power_kw, self.max_power_kw, self.get_available_charge_capacity_kw())
        
        # Calculate energy with efficiency
        energy_charged_kwh = max_charge_power * duration_hours * self.charge_efficiency
        
        # Update SOC
        soc_increase = (energy_charged_kwh / self.capacity_kwh) * 100.0
        self.current_soc_percent = min(self.max_soc_percent, self.current_soc_percent + soc_increase)
        
        return energy_charged_kwh
    
    def discharge(self, power_kw: float, duration_hours: float = 0.25) -> float:
        """
        Discharge the battery for the given power and duration.
        
        Args:
            power_kw: Discharging power in kW (positive value)
            duration_hours: Discharging duration in hours (default 0.25 for 15min intervals)
            
        Returns:
            float: Actual energy discharged in kWh
        """
        if power_kw <= 0:
            return 0.0
            
        # Limit discharging power to maximum and available capacity
        max_discharge_power = min(power_kw, self.max_power_kw, self.get_available_discharge_capacity_kw())
        
        # Calculate energy with efficiency
        energy_discharged_kwh = max_discharge_power * duration_hours / self.discharge_efficiency
        
        # Update SOC
        soc_decrease = (energy_discharged_kwh / self.capacity_kwh) * 100.0
        self.current_soc_percent = max(self.min_soc_percent, self.current_soc_percent - soc_decrease)
        
        return max_discharge_power * duration_hours  # Return actual output energy
    
    def get_status(self) -> Dict[str, Any]:
        """Get current battery status."""
        return {
            "capacity_kwh": self.capacity_kwh,
            "current_soc_percent": self.current_soc_percent,
            "available_charge_kw": self.get_available_charge_capacity_kw(),
            "available_discharge_kw": self.get_available_discharge_capacity_kw(),
            "energy_stored_kwh": (self.current_soc_percent / 100.0) * self.capacity_kwh
        }


class ElectricVehicle(BaseModel):
    """
    Electric Vehicle (EV) model with charging constraints and mobility patterns.
    """
    
    battery_capacity_kwh: float = Field(..., description="EV battery capacity in kWh")
    max_charge_power_kw: float = Field(..., description="Maximum charging power in kW")
    current_soc_percent: float = Field(default=70.0, description="Current SOC (%)")
    min_departure_soc_percent: float = Field(default=80.0, description="Required SOC at departure (%)")
    charge_deadline: str = Field(default="07:00", description="Departure time (HH:MM)")
    is_plugged_in: bool = Field(default=True, description="Whether EV is plugged in")
    charge_efficiency: float = Field(default=0.92, description="Charging efficiency (0-1)")
    
    def get_charging_requirement_kwh(self) -> float:
        """Calculate required energy to reach target SOC."""
        if self.current_soc_percent >= self.min_departure_soc_percent:
            return 0.0
        
        soc_deficit = self.min_departure_soc_percent - self.current_soc_percent
        return (soc_deficit / 100.0) * self.battery_capacity_kwh
    
    def get_available_charge_power_kw(self) -> float:
        """Get maximum available charging power considering constraints."""
        if not self.is_plugged_in or self.current_soc_percent >= 95.0:
            return 0.0
        
        return self.max_charge_power_kw
    
    def charge(self, power_kw: float, duration_hours: float = 0.25) -> float:
        """Charge the EV battery."""
        if not self.is_plugged_in or power_kw <= 0:
            return 0.0
        
        actual_power = min(power_kw, self.max_charge_power_kw)
        energy_charged_kwh = actual_power * duration_hours * self.charge_efficiency
        
        soc_increase = (energy_charged_kwh / self.battery_capacity_kwh) * 100.0
        self.current_soc_percent = min(95.0, self.current_soc_percent + soc_increase)
        
        return energy_charged_kwh


class SolarPV(BaseModel):
    """
    Solar Photovoltaic system model with generation forecasting.
    """
    
    capacity_kw: float = Field(..., description="Solar system capacity in kW")
    efficiency: float = Field(default=0.85, description="System efficiency (0-1)")
    
    def get_generation_kw(self, solar_irradiance_per_kw: float) -> float:
        """
        Calculate current solar generation based on irradiance data.
        
        Args:
            solar_irradiance_per_kw: Normalized solar generation (kW per kW installed)
            
        Returns:
            float: Current generation in kW
        """
        return self.capacity_kw * solar_irradiance_per_kw * self.efficiency


class Prosumer(BaseModel):
    """
    Prosumer model representing a household with distributed energy resources.
    
    This class combines multiple DER assets (BESS, EV, Solar) with load patterns
    and user preferences to model a complete prosumer entity.
    """
    
    prosumer_id: str = Field(..., description="Unique prosumer identifier")
    location: str = Field(default="Los Angeles, CA", description="Prosumer location")
    
    # Asset specifications
    bess: Optional[BESS] = Field(default=None, description="Battery system")
    ev: Optional[ElectricVehicle] = Field(default=None, description="Electric vehicle")
    solar: Optional[SolarPV] = Field(default=None, description="Solar PV system")
    
    # Load profile
    load_profile_id: str = Field(..., description="Associated load profile ID")
    current_load_kw: float = Field(default=0.0, description="Current load in kW")
    
    # User preferences (qualitative constraints)
    backup_power_hours: float = Field(default=4.0, description="Required backup power duration (hours)")
    comfort_temperature_range: tuple = Field(default=(68, 76), description="Comfort temperature range (F)")
    ev_priority: str = Field(default="medium", description="EV charging priority (low/medium/high)")
    participation_willingness: float = Field(default=0.8, description="Willingness to participate (0-1)")
    
    # Financial preferences
    min_compensation_per_kwh: float = Field(default=0.15, description="Minimum compensation ($/kWh)")
    max_discharge_percent: float = Field(default=60.0, description="Max battery discharge for grid (%)")
    
    class Config:
        arbitrary_types_allowed = True
    
    def update_load(self, load_kw: float) -> None:
        """Update current load from load profile data."""
        self.current_load_kw = load_kw
    
    def get_net_load_kw(self, solar_generation_kw: float = 0.0) -> float:
        """Calculate net load considering solar generation."""
        return max(0.0, self.current_load_kw - solar_generation_kw)
    
    def get_available_flexibility_kw(self) -> Dict[str, float]:
        """
        Calculate available flexibility for grid services.
        
        Returns:
            Dict with 'charge' and 'discharge' capacity in kW
        """
        flexibility = {"charge": 0.0, "discharge": 0.0}
        
        if self.bess:
            # Reserve capacity for backup power requirements
            backup_energy_kwh = self.backup_power_hours * 2.0  # Assume 2kW average load
            current_energy_kwh = (self.bess.current_soc_percent / 100.0) * self.bess.capacity_kwh
            
            # Available discharge (consider backup requirement and max discharge limit)
            min_energy_for_backup = max(
                (self.bess.min_soc_percent / 100.0) * self.bess.capacity_kwh,
                backup_energy_kwh
            )
            
            available_discharge_energy = current_energy_kwh - min_energy_for_backup
            max_allowed_discharge_energy = (self.max_discharge_percent / 100.0) * self.bess.capacity_kwh
            
            actual_discharge_energy = max(0.0, min(available_discharge_energy, max_allowed_discharge_energy))
            flexibility["discharge"] = min(self.bess.max_power_kw, actual_discharge_energy * 4)
            
            # Available charge
            flexibility["charge"] = self.bess.get_available_charge_capacity_kw()
        
        return flexibility
    
    def evaluate_market_opportunity(self, price_per_mwh: float, duration_hours: float = 0.25) -> Dict[str, Any]:
        """
        Evaluate a market opportunity and return bid parameters.
        
        Args:
            price_per_mwh: Market price in $/MWh
            duration_hours: Event duration in hours
            
        Returns:
            Dict with bid evaluation results
        """
        flexibility = self.get_available_flexibility_kw()
        price_per_kwh = price_per_mwh / 1000.0
        
        # Simple decision logic based on price and preferences
        participation_score = self.participation_willingness
        
        if price_per_kwh < self.min_compensation_per_kwh:
            participation_score *= 0.3  # Low willingness at low prices
        
        # Adjust based on current conditions
        if self.bess and self.bess.current_soc_percent < 30.0:
            participation_score *= 0.5  # Reduce participation if battery is low
        
        if self.ev and self.ev.get_charging_requirement_kwh() > 0:
            participation_score *= 0.7  # Reduce if EV needs charging
        
        return {
            "prosumer_id": self.prosumer_id,
            "available_discharge_kw": flexibility["discharge"],
            "available_charge_kw": flexibility["charge"],
            "participation_score": participation_score,
            "min_price_per_kwh": self.min_compensation_per_kwh,
            "max_duration_hours": 4.0  # Maximum event duration willing to participate
        }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary of all assets."""
        status = {
            "prosumer_id": self.prosumer_id,
            "current_load_kw": self.current_load_kw,
            "participation_willingness": self.participation_willingness
        }
        
        if self.bess:
            status["bess"] = self.bess.get_status()
        
        if self.ev:
            status["ev"] = {
                "soc_percent": self.ev.current_soc_percent,
                "charging_requirement_kwh": self.ev.get_charging_requirement_kwh(),
                "is_plugged_in": self.ev.is_plugged_in
            }
        
        if self.solar:
            status["solar_capacity_kw"] = self.solar.capacity_kw
        
        return status
