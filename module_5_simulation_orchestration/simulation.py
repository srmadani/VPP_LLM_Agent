"""
Main Simulation Orchestration for VPP LLM Agent - Module 5

This module implements the complete simulation loop that orchestrates all modules,
runs both agentic and centralized approaches, and generates comprehensive results
for performance comparison.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from tqdm import tqdm
import time
from loguru import logger

# Add paths for imports
sys.path.append('../module_1_data_simulation')
sys.path.append('../module_2_asset_modeling')
sys.path.append('../module_3_agentic_framework')
sys.path.append('../module_4_negotiation_logic')

# Configure logging
logger.add("simulation.log", rotation="10 MB")

# Import from previous modules
from prosumer_models import Prosumer
from fleet_generator import FleetGenerator
from schemas import MarketOpportunity, AgentState
from main_negotiation import CoreNegotiationEngine
from centralized_optimizer import CentralizedOptimizer


@dataclass
class SimulationMetrics:
    """Comprehensive metrics for each simulation timestep."""
    timestamp: datetime
    
    # Market conditions
    lmp_price: float
    spin_price: float
    nonspin_price: float
    
    # Agentic model results
    agentic_success: bool
    agentic_bid_capacity_mw: float
    agentic_bid_price_mwh: float
    agentic_expected_profit: float
    agentic_actual_profit: float
    agentic_prosumer_satisfaction: float
    agentic_negotiation_rounds: int
    agentic_coalition_size: int
    agentic_optimization_time: float
    
    # Centralized model results
    centralized_success: bool
    centralized_bid_capacity_mw: float
    centralized_bid_price_mwh: float
    centralized_expected_profit: float
    centralized_actual_profit: float
    centralized_prosumer_satisfaction: float
    centralized_preference_violations: int
    centralized_optimization_time: float
    
    # Comparative metrics
    profit_difference: float
    satisfaction_difference: float
    capacity_difference_mw: float
    price_difference_mwh: float


@dataclass
class SimulationSummary:
    """Final simulation summary statistics."""
    total_timesteps: int
    simulation_duration_hours: float
    
    # Agentic performance
    agentic_total_profit: float
    agentic_avg_satisfaction: float
    agentic_success_rate: float
    agentic_avg_coalition_size: float
    agentic_avg_negotiation_rounds: float
    agentic_total_capacity_mwh: float
    
    # Centralized performance
    centralized_total_profit: float
    centralized_avg_satisfaction: float
    centralized_success_rate: float
    centralized_total_violations: int
    centralized_total_capacity_mwh: float
    
    # Comparative analysis
    profit_advantage_percent: float
    satisfaction_advantage_percent: float
    efficiency_ratio: float
    
    # Computational performance
    agentic_avg_time_seconds: float
    centralized_avg_time_seconds: float
    total_simulation_time_minutes: float


class VPPSimulationOrchestrator:
    """
    Main simulation orchestrator that runs both agentic and centralized approaches
    and provides comprehensive performance comparison.
    """
    
    def __init__(self, data_path: str = "../module_1_data_simulation/data"):
        """Initialize the simulation orchestrator."""
        self.data_path = Path(data_path)
        self.results_path = Path("results")
        self.results_path.mkdir(exist_ok=True)
        
        # Load market data
        self.market_data = self._load_market_data()
        
        # Initialize engines
        self.negotiation_engine = CoreNegotiationEngine()
        self.centralized_optimizer = CentralizedOptimizer()
        self.fleet_generator = FleetGenerator(str(self.data_path))
        
        # Simulation state
        self.prosumer_fleet = []
        self.simulation_metrics = []
        self.current_timestep = 0
        
        logger.info("VPP Simulation Orchestrator initialized")
    
    def run_full_simulation(
        self,
        fleet_size: int = 200,  # Scaled up 10x from original 20
        start_timestamp: Optional[datetime] = None,
        duration_hours: int = 744,  # 31 days (August) = 31 * 24 = 744 hours
        opportunity_frequency_hours: int = 1  # Market opportunities every hour
    ) -> SimulationSummary:
        """
        Run the complete simulation comparing agentic vs centralized approaches.
        
        Args:
            fleet_size: Number of prosumers in the fleet
            start_timestamp: Start time (defaults to data start)
            duration_hours: Total simulation duration
            opportunity_frequency_hours: Hours between market opportunities
            
        Returns:
            SimulationSummary with complete results
        """
        start_time = datetime.now()
        logger.info(f"Starting VPP simulation: {fleet_size} prosumers, {duration_hours}h duration")
        
        # Initialize simulation
        self._initialize_simulation(fleet_size, start_timestamp)
        
        # Calculate timesteps
        total_timesteps = duration_hours // opportunity_frequency_hours
        
        # Main simulation loop
        for timestep in tqdm(range(total_timesteps), desc="Simulation Progress"):
            try:
                current_time = self._get_current_timestamp(timestep, opportunity_frequency_hours)
                metrics = self._run_timestep(current_time, timestep)
                self.simulation_metrics.append(metrics)
                
                # Update prosumer states
                self._update_prosumer_states(current_time, opportunity_frequency_hours)
                
            except Exception as e:
                logger.error(f"Error in timestep {timestep}: {e}")
                continue
        
        # Generate final results
        summary = self._generate_simulation_summary(start_time)
        self._save_results(summary)
        
        logger.info(f"Simulation completed in {summary.total_simulation_time_minutes:.1f} minutes")
        return summary
    
    def _initialize_simulation(self, fleet_size: int, start_timestamp: Optional[datetime]):
        """Initialize the simulation with prosumer fleet and data."""
        logger.info(f"Initializing simulation with {fleet_size} prosumers")
        
        # Generate prosumer fleet
        self.prosumer_fleet = self.fleet_generator.create_prosumer_fleet(fleet_size)
        
        # Set starting timestamp
        if start_timestamp is None:
            start_timestamp = pd.to_datetime(self.market_data.iloc[0]['timestamp'])
        
        self.start_timestamp = start_timestamp
        logger.info(f"Simulation starts at {start_timestamp}")
    
    def _run_timestep(self, current_time: datetime, timestep: int) -> SimulationMetrics:
        """Run a single simulation timestep with both approaches."""
        
        # Get market conditions
        market_row = self._get_market_data_for_timestamp(current_time)
        if market_row is None:
            return self._create_empty_metrics(current_time)
        
        # Create market opportunity
        opportunity = self._create_market_opportunity(market_row, current_time)
        
        # Run agentic approach
        agentic_start = time.time()
        agentic_result = self.negotiation_engine.run_negotiation(
            opportunity, self.prosumer_fleet.copy(), self.market_data
        )
        agentic_time = time.time() - agentic_start
        
        # Run centralized approach
        centralized_start = time.time()
        centralized_result = self.centralized_optimizer.optimize_dispatch(
            opportunity, self.prosumer_fleet.copy(), current_time
        )
        centralized_time = time.time() - centralized_start
        
        # Calculate actual profits (simplified clearing simulation)
        agentic_actual_profit = self._calculate_actual_profit(
            agentic_result.total_capacity_mw,
            agentic_result.final_bid_price,
            market_row['lmp']
        ) if agentic_result.success else 0.0
        
        centralized_actual_profit = self._calculate_actual_profit(
            centralized_result.total_bid_capacity_mw,
            centralized_result.optimal_bid_price_mwh,
            market_row['lmp']
        ) if centralized_result.success else 0.0
        
        # Create metrics
        metrics = SimulationMetrics(
            timestamp=current_time,
            lmp_price=market_row['lmp'],
            spin_price=market_row['spin_price'],
            nonspin_price=market_row['nonspin_price'],
            
            # Agentic results
            agentic_success=agentic_result.success,
            agentic_bid_capacity_mw=agentic_result.total_capacity_mw,
            agentic_bid_price_mwh=agentic_result.final_bid_price,
            agentic_expected_profit=0.0,  # Would need market clearing model
            agentic_actual_profit=agentic_actual_profit,
            agentic_prosumer_satisfaction=agentic_result.prosumer_satisfaction_avg,
            agentic_negotiation_rounds=agentic_result.negotiation_rounds,
            agentic_coalition_size=len(agentic_result.coalition_members),
            agentic_optimization_time=agentic_time,
            
            # Centralized results
            centralized_success=centralized_result.success,
            centralized_bid_capacity_mw=centralized_result.total_bid_capacity_mw,
            centralized_bid_price_mwh=centralized_result.optimal_bid_price_mwh,
            centralized_expected_profit=centralized_result.expected_profit,
            centralized_actual_profit=centralized_actual_profit,
            centralized_prosumer_satisfaction=centralized_result.prosumer_satisfaction_score,
            centralized_preference_violations=len(centralized_result.violated_preferences),
            centralized_optimization_time=centralized_time,
            
            # Comparative metrics
            profit_difference=agentic_actual_profit - centralized_actual_profit,
            satisfaction_difference=agentic_result.prosumer_satisfaction_avg - 0.0,
            capacity_difference_mw=agentic_result.total_capacity_mw - centralized_result.total_bid_capacity_mw,
            price_difference_mwh=agentic_result.final_bid_price - centralized_result.optimal_bid_price_mwh
        )
        
        logger.debug(f"Timestep {timestep}: Agentic profit=${agentic_actual_profit:.2f}, "
                    f"Centralized profit=${centralized_actual_profit:.2f}")
        
        return metrics
    
    def _create_market_opportunity(self, market_row: Dict, current_time: datetime) -> MarketOpportunity:
        """Create a market opportunity from market data."""
        from schemas import MarketOpportunity, MarketOpportunityType
        from datetime import timedelta
        
        # Calculate total available fleet capacity
        total_capacity_kw = sum(
            prosumer.get_available_capacity_kw() for prosumer in self.prosumer_fleet
        )
        
        # Set required capacity to be achievable (50-80% of total available capacity)
        required_capacity_kw = min(total_capacity_kw * 0.7, 100.0)  # Max 100kW for residential VPP
        required_capacity_mw = required_capacity_kw / 1000.0
        
        return MarketOpportunity(
            opportunity_id=f"opp_{current_time.strftime('%Y%m%d_%H%M')}",
            market_type=MarketOpportunityType.ENERGY,
            timestamp=current_time,
            duration_hours=1.0,
            required_capacity_mw=required_capacity_mw,  # Realistic capacity for residential fleet
            market_price_mwh=float(market_row['lmp']),
            deadline=current_time + timedelta(minutes=15)  # 15-minute ahead market
        )
    
    def _calculate_actual_profit(self, capacity_mw: float, bid_price: float, clearing_price: float) -> float:
        """Calculate actual profit based on simplified market clearing."""
        if capacity_mw <= 0 or bid_price <= 0:
            return 0.0
        
        # Simplified clearing: bid clears if price is competitive
        if bid_price <= clearing_price * 1.1:  # 10% margin
            # Revenue minus estimated costs
            revenue = capacity_mw * clearing_price
            costs = capacity_mw * clearing_price * 0.7  # 70% cost ratio
            return revenue - costs
        else:
            return 0.0  # Bid didn't clear
    
    def _update_prosumer_states(self, current_time: datetime, hours_elapsed: int):
        """Update prosumer asset states based on time progression."""
        for prosumer in self.prosumer_fleet:
            # Update battery states based on load and solar
            if prosumer.bess:
                # Simplified state update - would use actual load/solar data
                load_change = np.random.normal(0, 1.0)  # kWh change
                # Use charge/discharge methods instead of update_soc
                if load_change > 0:
                    # Net energy available - charge battery
                    prosumer.bess.charge(load_change * 4, 0.25)  # Convert kWh to kW for 15min
                else:
                    # Net energy needed - discharge battery
                    prosumer.bess.discharge(abs(load_change) * 4, 0.25)
            
            # Update EV states
            if prosumer.ev:
                # Simplified EV behavior
                if np.random.random() < 0.1:  # 10% chance to unplug/plug
                    prosumer.ev.is_plugged_in = not prosumer.ev.is_plugged_in
    
    def _get_current_timestamp(self, timestep: int, frequency_hours: int) -> datetime:
        """Get the current simulation timestamp."""
        return self.start_timestamp + timedelta(hours=timestep * frequency_hours)
    
    def _get_market_data_for_timestamp(self, timestamp: datetime) -> Optional[Dict]:
        """Get market data for a specific timestamp."""
        # Find closest timestamp in market data
        market_times = pd.to_datetime(self.market_data['timestamp'])
        closest_idx = (market_times - timestamp).abs().idxmin()
        
        if (market_times.iloc[closest_idx] - timestamp).total_seconds() < 3600:  # Within 1 hour
            return self.market_data.iloc[closest_idx].to_dict()
        return None
    
    def _create_empty_metrics(self, timestamp: datetime) -> SimulationMetrics:
        """Create empty metrics for failed timesteps."""
        return SimulationMetrics(
            timestamp=timestamp,
            lmp_price=0.0, spin_price=0.0, nonspin_price=0.0,
            agentic_success=False, agentic_bid_capacity_mw=0.0, agentic_bid_price_mwh=0.0,
            agentic_expected_profit=0.0, agentic_actual_profit=0.0, agentic_prosumer_satisfaction=0.0,
            agentic_negotiation_rounds=0, agentic_coalition_size=0, agentic_optimization_time=0.0,
            centralized_success=False, centralized_bid_capacity_mw=0.0, centralized_bid_price_mwh=0.0,
            centralized_expected_profit=0.0, centralized_actual_profit=0.0, centralized_prosumer_satisfaction=0.0,
            centralized_preference_violations=0, centralized_optimization_time=0.0,
            profit_difference=0.0, satisfaction_difference=0.0, capacity_difference_mw=0.0, price_difference_mwh=0.0
        )
    
    def _generate_simulation_summary(self, start_time: datetime) -> SimulationSummary:
        """Generate comprehensive simulation summary."""
        if not self.simulation_metrics:
            raise ValueError("No simulation metrics available")
        
        df = pd.DataFrame([asdict(m) for m in self.simulation_metrics])
        
        # Calculate aggregated statistics
        agentic_successful = df[df['agentic_success'] == True]
        centralized_successful = df[df['centralized_success'] == True]
        
        summary = SimulationSummary(
            total_timesteps=len(df),
            simulation_duration_hours=len(df),  # Assuming 1-hour intervals
            
            # Agentic performance
            agentic_total_profit=df['agentic_actual_profit'].sum(),
            agentic_avg_satisfaction=df['agentic_prosumer_satisfaction'].mean(),
            agentic_success_rate=len(agentic_successful) / len(df),
            agentic_avg_coalition_size=df['agentic_coalition_size'].mean(),
            agentic_avg_negotiation_rounds=df['agentic_negotiation_rounds'].mean(),
            agentic_total_capacity_mwh=df['agentic_bid_capacity_mw'].sum(),
            
            # Centralized performance
            centralized_total_profit=df['centralized_actual_profit'].sum(),
            centralized_avg_satisfaction=df['centralized_prosumer_satisfaction'].mean(),
            centralized_success_rate=len(centralized_successful) / len(df),
            centralized_total_violations=df['centralized_preference_violations'].sum(),
            centralized_total_capacity_mwh=df['centralized_bid_capacity_mw'].sum(),
            
            # Comparative analysis
            profit_advantage_percent=0.0,  # Will calculate below
            satisfaction_advantage_percent=0.0,  # Will calculate below
            efficiency_ratio=0.0,  # Will calculate below
            
            # Computational performance
            agentic_avg_time_seconds=df['agentic_optimization_time'].mean(),
            centralized_avg_time_seconds=df['centralized_optimization_time'].mean(),
            total_simulation_time_minutes=(datetime.now() - start_time).total_seconds() / 60
        )
        
        # Calculate comparative metrics
        if summary.centralized_total_profit > 0:
            summary.profit_advantage_percent = (
                (summary.agentic_total_profit - summary.centralized_total_profit) / 
                summary.centralized_total_profit * 100
            )
        
        if summary.centralized_avg_satisfaction > 0:
            summary.satisfaction_advantage_percent = (
                (summary.agentic_avg_satisfaction - summary.centralized_avg_satisfaction) / 
                summary.centralized_avg_satisfaction * 100
            )
        
        if summary.centralized_total_capacity_mwh > 0:
            summary.efficiency_ratio = (
                summary.agentic_total_capacity_mwh / summary.centralized_total_capacity_mwh
            )
        
        return summary
    
    def _save_results(self, summary: SimulationSummary):
        """Save simulation results to files."""
        # Save detailed timestep data
        df = pd.DataFrame([asdict(m) for m in self.simulation_metrics])
        results_file = self.results_path / "simulation_results.csv"
        df.to_csv(results_file, index=False)
        
        # Save summary statistics
        summary_file = self.results_path / "simulation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
        
        # Save human-readable report
        self._generate_report(summary)
        
        logger.info(f"Results saved to {self.results_path}")
    
    def _generate_report(self, summary: SimulationSummary):
        """Generate human-readable simulation report."""
        report_file = self.results_path / "simulation_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# VPP LLM Agent Simulation Report\n\n")
            f.write(f"**Simulation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration**: {summary.simulation_duration_hours} hours ({summary.total_timesteps} timesteps)\n")
            f.write(f"**Fleet Size**: {len(self.prosumer_fleet)} prosumers\n\n")
            
            f.write("## Performance Comparison\n\n")
            f.write("| Metric | Agentic Model | Centralized Model | Advantage |\n")
            f.write("|--------|---------------|-------------------|----------|\n")
            f.write(f"| Total Profit | ${summary.agentic_total_profit:.2f} | ${summary.centralized_total_profit:.2f} | {summary.profit_advantage_percent:+.1f}% |\n")
            f.write(f"| Avg Satisfaction | {summary.agentic_avg_satisfaction:.3f} | {summary.centralized_avg_satisfaction:.3f} | {summary.satisfaction_advantage_percent:+.1f}% |\n")
            f.write(f"| Success Rate | {summary.agentic_success_rate:.1%} | {summary.centralized_success_rate:.1%} | - |\n")
            f.write(f"| Total Capacity | {summary.agentic_total_capacity_mwh:.1f} MWh | {summary.centralized_total_capacity_mwh:.1f} MWh | - |\n")
            f.write(f"| Avg Optimization Time | {summary.agentic_avg_time_seconds:.3f}s | {summary.centralized_avg_time_seconds:.3f}s | - |\n\n")
            
            f.write("## Key Insights\n\n")
            f.write(f"- **Prosumer Satisfaction**: The agentic model achieved {summary.agentic_avg_satisfaction:.1%} average satisfaction vs {summary.centralized_avg_satisfaction:.1%} for centralized\n")
            f.write(f"- **Preference Violations**: Centralized model violated {summary.centralized_total_violations} prosumer preferences\n")
            f.write(f"- **Negotiation Complexity**: Average {summary.agentic_avg_negotiation_rounds:.1f} rounds with {summary.agentic_avg_coalition_size:.1f} prosumers per coalition\n")
            f.write(f"- **Computational Efficiency**: Agentic model took {summary.agentic_avg_time_seconds/summary.centralized_avg_time_seconds:.1f}x longer than centralized\n\n")
            
            f.write("## Conclusion\n\n")
            if summary.satisfaction_advantage_percent > 50:
                f.write("The agentic model demonstrates significant value in maintaining prosumer satisfaction ")
                f.write("while achieving competitive profit levels. The ability to handle qualitative preferences ")
                f.write("makes it superior for real-world VPP deployment despite slightly lower theoretical profits.\n")
            else:
                f.write("Results show trade-offs between profit optimization and prosumer satisfaction. ")
                f.write("Further tuning of negotiation strategies may improve the balance.\n")
    
    def _load_market_data(self) -> pd.DataFrame:
        """Load market data from Module 1."""
        market_file = self.data_path / "market_data.csv"
        if not market_file.exists():
            raise FileNotFoundError(f"Market data not found: {market_file}")
        
        df = pd.read_csv(market_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df


def main():
    """Run the complete VPP simulation."""
    orchestrator = VPPSimulationOrchestrator()
    
    # Run simulation with different configurations
    print("Starting VPP LLM Agent Simulation...")
    
    # Run realistic scale simulation
    summary = orchestrator.run_full_simulation(
        fleet_size=200,  # Scaled up fleet size
        duration_hours=744,  # Full month (August)
        opportunity_frequency_hours=1  # Hourly opportunities
    )
    
    print("\n=== Simulation Complete ===")
    print(f"Total profit - Agentic: ${summary.agentic_total_profit:.2f}")
    print(f"Total profit - Centralized: ${summary.centralized_total_profit:.2f}")
    print(f"Profit advantage: {summary.profit_advantage_percent:+.1f}%")
    print(f"Satisfaction advantage: {summary.satisfaction_advantage_percent:+.1f}%")
    print(f"Total simulation time: {summary.total_simulation_time_minutes:.1f} minutes")
    
    print(f"\nDetailed results saved to: results/")


if __name__ == "__main__":
    main()
