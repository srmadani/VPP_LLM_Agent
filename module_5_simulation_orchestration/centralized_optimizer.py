"""
Centralized Optimizer for VPP LLM Agent - Module 5

This module implements the baseline centralized optimization model for comparison
against the agentic negotiation approach. It assumes perfect information and control
over all prosumer assets to maximize total VPP profit.
"""

import os
import sys
import cvxpy as cp
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

# Add paths for imports
sys.path.append('../module_2_asset_modeling')
sys.path.append('../module_3_agentic_framework')

from prosumer_models import Prosumer
from schemas import MarketOpportunity


@dataclass
class CentralizedResult:
    """Result of centralized optimization."""
    success: bool
    total_bid_capacity_mw: float
    optimal_bid_price_mwh: float
    dispatch_schedule: Dict[str, float]  # prosumer_id -> dispatch_kw
    expected_profit: float
    prosumer_satisfaction_score: float  # Moderate baseline - doesn't consider detailed preferences
    violated_preferences: List[str]  # List of preference violations
    optimization_time_seconds: float


class CentralizedOptimizer:
    """
    Centralized optimization baseline that assumes perfect control and information.
    
    This optimizer maximizes total VPP profit without considering prosumer preferences,
    serving as a theoretical upper bound for profit comparison.
    """
    
    def __init__(self):
        """Initialize the centralized optimizer."""
        self.preference_violations = []
        
    def optimize_dispatch(
        self, 
        market_opportunity: MarketOpportunity,
        prosumer_fleet: List[Prosumer],
        current_timestamp: datetime
    ) -> CentralizedResult:
        """
        Perform centralized optimization for the VPP dispatch.
        
        Args:
            market_opportunity: Market bidding opportunity
            prosumer_fleet: List of available prosumers
            current_timestamp: Current simulation timestamp
            
        Returns:
            CentralizedResult with optimization outcome
        """
        start_time = datetime.now()
        self.preference_violations = []
        
        try:
            # Filter available prosumers based on asset availability
            available_prosumers = self._filter_available_prosumers(
                prosumer_fleet, current_timestamp
            )
            
            if not available_prosumers:
                return CentralizedResult(
                    success=False,
                    coalition_members=[],
                    total_bid_capacity_mw=0.0,
                    optimal_bid_price_mwh=0.0,
                    dispatch_schedule={},
                    expected_profit=0.0,
                    prosumer_satisfaction_score=4.5,  # Moderate baseline - doesn't consider individual preferences
                    violated_preferences=[],
                    optimization_time_seconds=0.0
                )
            
            # Set up optimization problem
            n_prosumers = len(available_prosumers)
            prosumer_ids = [p.prosumer_id for p in available_prosumers]
            
            # Decision variables
            dispatch_vars = cp.Variable(n_prosumers, nonneg=True)  # kW dispatch per prosumer
            
            # Extract prosumer capacities and costs
            max_capacities = []
            marginal_costs = []
            
            for prosumer in available_prosumers:
                capacity, cost, violations = self._calculate_prosumer_capacity_cost(
                    prosumer, market_opportunity.market_type, current_timestamp
                )
                max_capacities.append(capacity)
                marginal_costs.append(cost)
                self.preference_violations.extend(violations)
            
            max_capacities = np.array(max_capacities)
            marginal_costs = np.array(marginal_costs)
            
            # Profit-based objective: maximize (market_price - marginal_cost) * dispatch
            bid_price = market_opportunity.market_price_mwh * 0.95  # Conservative bid
            profit_margins = bid_price - marginal_costs  # $/MWh - $/MWh = $/MWh
            
            # Convert to profit per kW ($/MWh -> $/kWh)
            profit_per_kw = profit_margins / 1000.0  # $/kWh
            
            objective = cp.Maximize(cp.sum(cp.multiply(profit_per_kw, dispatch_vars)))
            
            # Constraints
            constraints = [
                # Capacity constraints
                dispatch_vars <= max_capacities
            ]
            
            # Market size constraints
            total_available_kw = np.sum(max_capacities)
            max_required_kw = market_opportunity.required_capacity_mw * 1000.0
            
            # Set feasible dispatch bounds - no minimum constraint
            # Maximum is the smaller of available capacity or market requirement
            max_dispatch_kw = min(total_available_kw, max_required_kw)
            
            if max_dispatch_kw > 0:
                constraints.append(cp.sum(dispatch_vars) <= max_dispatch_kw)
            
            # Debug constraints
            print(f"Max capacities: {max_capacities}")
            print(f"Required capacity: {market_opportunity.required_capacity_mw} MW")
            print(f"Total available capacity: {total_available_kw} kW")
            print(f"Max dispatch allowed: {max_dispatch_kw} kW")
            
            # Solve optimization problem
            problem = cp.Problem(objective, constraints)
            problem.solve(solver=cp.ECOS, verbose=True)
            
            if problem.status not in ["infeasible", "unbounded"]:
                # Extract solution
                optimal_dispatch = dispatch_vars.value
                optimal_bid_price = market_opportunity.market_price_mwh * 0.95  # Conservative bid
                
                dispatch_schedule = {
                    prosumer_ids[i]: max(0.0, optimal_dispatch[i])
                    for i in range(n_prosumers)
                }
                
                total_capacity = sum(dispatch_schedule.values()) / 1000.0  # MW
                
                # Calculate actual expected profit
                total_dispatched_kw = sum(dispatch_schedule.values())
                total_profit_per_hour = problem.value if problem.value else 0.0
                expected_profit = total_profit_per_hour  # Already in $ from optimization
                
                # Calculate satisfaction score (moderate baseline - doesn't consider detailed preferences)
                satisfaction_score = 4.5
                
                optimization_time = (datetime.now() - start_time).total_seconds()
                
                return CentralizedResult(
                    success=True,
                    total_bid_capacity_mw=total_capacity,
                    optimal_bid_price_mwh=optimal_bid_price,
                    dispatch_schedule=dispatch_schedule,
                    expected_profit=expected_profit,
                    prosumer_satisfaction_score=satisfaction_score,
                    violated_preferences=self.preference_violations.copy(),
                    optimization_time_seconds=optimization_time
                )
            else:
                optimization_time = (datetime.now() - start_time).total_seconds()
                return CentralizedResult(
                    success=False,
                    total_bid_capacity_mw=0.0,
                    optimal_bid_price_mwh=0.0,
                    dispatch_schedule={},
                    expected_profit=0.0,
                    prosumer_satisfaction_score=4.5,  # Moderate baseline even on failure
                    violated_preferences=self.preference_violations.copy(),
                    optimization_time_seconds=optimization_time
                )
                
        except Exception as e:
            optimization_time = (datetime.now() - start_time).total_seconds()
            print(f"Centralized optimization error: {e}")
            return CentralizedResult(
                success=False,
                total_bid_capacity_mw=0.0,
                optimal_bid_price_mwh=0.0,
                dispatch_schedule={},
                expected_profit=0.0,
                prosumer_satisfaction_score=4.5,  # Moderate baseline even on error
                violated_preferences=self.preference_violations.copy(),
                optimization_time_seconds=optimization_time
            )
    
    def _filter_available_prosumers(
        self, 
        prosumer_fleet: List[Prosumer], 
        timestamp: datetime
    ) -> List[Prosumer]:
        """Filter prosumers that have available capacity."""
        available = []
        
        for prosumer in prosumer_fleet:
            has_capacity = False
            
            # Check BESS availability
            if prosumer.bess and prosumer.bess.capacity_kwh > 0:
                current_soc_kwh = (prosumer.bess.current_soc_percent / 100.0) * prosumer.bess.capacity_kwh
                if current_soc_kwh > prosumer.bess.capacity_kwh * 0.1:  # At least 10% available
                    has_capacity = True
            
            # Check EV availability (if plugged in)
            if prosumer.ev and prosumer.ev.is_plugged_in:
                current_soc_kwh = (prosumer.ev.current_soc_percent / 100.0) * prosumer.ev.battery_capacity_kwh
                if current_soc_kwh > prosumer.ev.battery_capacity_kwh * 0.2:  # At least 20% available
                    has_capacity = True
            
            if has_capacity:
                available.append(prosumer)
        
        return available
    
    def _calculate_prosumer_capacity_cost(
        self, 
        prosumer: Prosumer, 
        market_type: str,
        timestamp: datetime
    ) -> Tuple[float, float, List[str]]:
        """
        Calculate available capacity and marginal cost for a prosumer.
        
        This method IGNORES prosumer preferences to achieve maximum theoretical profit.
        All preference violations are recorded.
        """
        total_capacity = 0.0
        weighted_cost = 0.0
        violations = []
        
        # BESS contribution (ignores backup requirements)
        if prosumer.bess:
            # Ignore minimum SoC preferences and backup requirements
            available_soc_kwh = (prosumer.bess.current_soc_percent / 100.0) * prosumer.bess.capacity_kwh
            if prosumer.backup_power_hours > 2.0:  # Normal backup is 2 hours
                violations.append(f"{prosumer.prosumer_id}: Violated backup power requirement")
            
            # Use maximum available capacity (ignoring backup needs)
            bess_capacity = min(
                available_soc_kwh * 0.9,  # 90% discharge allowed
                prosumer.bess.max_power_kw
            )
            
            total_capacity += bess_capacity
            weighted_cost += bess_capacity * 50.0  # $/MWh opportunity cost
        
        # EV contribution (ignores charging deadlines)
        if prosumer.ev and prosumer.ev.is_plugged_in:
            # Ignore charging deadline preferences
            if prosumer.ev.get_charging_requirement_kwh() > 0:
                violations.append(f"{prosumer.prosumer_id}: Violated EV charging requirement")
            
            available_soc_kwh = (prosumer.ev.current_soc_percent / 100.0) * prosumer.ev.battery_capacity_kwh
            ev_capacity = min(
                available_soc_kwh * 0.8,  # 80% discharge allowed
                prosumer.ev.max_charge_power_kw
            )
            
            total_capacity += ev_capacity
            weighted_cost += ev_capacity * 80.0  # Higher cost due to mobility impact
        
        # Calculate weighted average cost
        if total_capacity > 0:
            avg_cost = weighted_cost / total_capacity
        else:
            avg_cost = 100.0  # Default high cost
        
        return total_capacity, avg_cost, violations
    
    def _estimate_clearing_probability(self, market_price: float, bid_price: cp.Variable) -> float:
        """
        Estimate probability of bid clearing based on market conditions.
        
        Simplified model: higher bid prices have lower clearing probability.
        """
        # Linear probability model
        prob = cp.maximum(0.1, 1.0 - (bid_price - market_price) / (market_price * 0.5))
        return cp.minimum(1.0, prob)


def main():
    """Test the centralized optimizer."""
    from schemas import MarketOpportunity, MarketOpportunityType
    from fleet_generator import FleetGenerator
    from datetime import datetime, timedelta
    
    # Initialize components
    optimizer = CentralizedOptimizer()
    fleet_gen = FleetGenerator()
    
    # Create test fleet
    test_fleet = fleet_gen.create_prosumer_fleet(5)
    
    # Create test market opportunity with correct schema
    now = datetime.now()
    opportunity = MarketOpportunity(
        opportunity_id="test_001",
        market_type=MarketOpportunityType.ENERGY,
        timestamp=now,
        duration_hours=1.0,
        required_capacity_mw=2.0,
        market_price_mwh=75.0,
        deadline=now + timedelta(minutes=30)
    )
    
    # Run optimization
    result = optimizer.optimize_dispatch(
        opportunity, 
        test_fleet, 
        datetime.now()
    )
    
    print("\n=== Centralized Optimization Test ===")
    print(f"Success: {result.success}")
    print(f"Total capacity: {result.total_bid_capacity_mw:.3f} MW")
    print(f"Optimal price: ${result.optimal_bid_price_mwh:.2f}/MWh")
    print(f"Expected profit: ${result.expected_profit:.2f}")
    print(f"Preference violations: {len(result.violated_preferences)}")
    print(f"Optimization time: {result.optimization_time_seconds:.3f}s")


if __name__ == "__main__":
    main()
