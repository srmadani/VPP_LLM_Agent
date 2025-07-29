"""
Integrated Negotiation System for VPP LLM Agent - Module 4

This module provides a complete integration of the negotiation engine and
optimization tool, implementing the full LangGraph-based workflow with
LLM-powered agents and hybrid optimization.
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Add paths for imports
sys.path.append('../module_1_data_simulation')
sys.path.append('../module_2_asset_modeling')
sys.path.append('../module_3_agentic_framework')

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import pandas as pd

# Import the core components
from main_negotiation import CoreNegotiationEngine, NegotiationResult
from optimization_tool import OptimizationTool, OptimizationResult

# Import schemas and models (with fallback definitions)
try:
    from schemas import (
        AgentState, MarketOpportunity, ProsumerBid, AggregatorOffer,
        ProsumerResponse, CoalitionMember, NegotiationSummary
    )
    from prosumer_models import Prosumer
    from fleet_generator import FleetGenerator
except ImportError:
    # Fallback minimal definitions for testing
    from dataclasses import dataclass
    from typing import Dict, List
    from datetime import datetime
    
    @dataclass
    class MarketOpportunity:
        opportunity_id: str
        market_type: str
        timestamp: datetime
        duration_hours: float
        required_capacity_mw: float
        market_price_mwh: float
        deadline: datetime
    
    @dataclass
    class CoalitionMember:
        prosumer_id: str
        committed_capacity_kw: float
        agreed_price_per_mwh: float
        satisfaction_score: float
        technical_constraints: Dict
        dispatch_flexibility: float


class IntegratedNegotiationSystem:
    """
    Complete negotiation system integrating LLM-powered agents with optimization.
    
    This system orchestrates the full negotiation workflow from opportunity
    identification through final bid submission, including multi-round
    negotiations and hybrid LLM-to-solver optimization.
    """
    
    def __init__(self):
        """Initialize the integrated negotiation system."""
        load_dotenv()
        
        # Initialize core components
        self.negotiation_engine = CoreNegotiationEngine()
        self.optimization_tool = OptimizationTool()
        
        # Initialize LLM for coordination
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.2
        )
        
        # System parameters
        self.simulation_start_time = datetime(2023, 8, 15, 0, 0, 0)
        self.time_step_minutes = 15
        
    def run_complete_negotiation_cycle(
        self,
        market_opportunity: MarketOpportunity,
        prosumer_fleet: List,  # List[Prosumer] with fallback
        market_data: pd.DataFrame,
        simulation_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run a complete negotiation and optimization cycle.
        
        Args:
            market_opportunity: The market opportunity to bid on
            prosumer_fleet: Available prosumer fleet
            market_data: Current market data context
            simulation_context: Additional simulation information
            
        Returns:
            Dict containing complete results including negotiation and optimization
        """
        
        cycle_log = []
        cycle_log.append(f"Starting negotiation cycle for {market_opportunity.opportunity_id}")
        
        # Phase 1: Multi-round negotiation
        cycle_log.append("Phase 1: Running multi-round negotiation")
        negotiation_result = self.negotiation_engine.run_negotiation(
            market_opportunity, prosumer_fleet, market_data
        )
        
        cycle_log.extend(negotiation_result.negotiation_log)
        
        if not negotiation_result.success:
            cycle_log.append("Negotiation failed - no viable coalition formed")
            return self._format_failed_result(cycle_log, "negotiation_failed")
        
        # Phase 2: Hybrid optimization
        cycle_log.append("Phase 2: Running hybrid LLM-to-solver optimization")
        optimization_result = self.optimization_tool.formulate_and_submit_bid(
            market_opportunity,
            negotiation_result.coalition_members,
            simulation_context
        )
        
        cycle_log.extend(optimization_result.optimization_log)
        
        if not optimization_result.success:
            cycle_log.append("Optimization failed - reverting to simple pricing")
            optimization_result = self._create_fallback_optimization(
                market_opportunity, negotiation_result.coalition_members
            )
        
        # Phase 3: Final bid preparation
        cycle_log.append("Phase 3: Preparing final VPP bid")
        final_bid = self._prepare_final_bid(
            market_opportunity,
            negotiation_result,
            optimization_result
        )
        
        cycle_log.append(f"Final bid: {final_bid['total_capacity_mw']:.2f} MW @ ${final_bid['bid_price_mwh']:.2f}/MWh")
        
        # Compile complete results
        complete_result = {
            "success": True,
            "opportunity_id": market_opportunity.opportunity_id,
            "market_type": getattr(market_opportunity.market_type, 'value', market_opportunity.market_type),
            "timestamp": market_opportunity.timestamp.isoformat(),
            
            # Negotiation results
            "negotiation": {
                "success": negotiation_result.success,
                "coalition_size": len(negotiation_result.coalition_members),
                "total_capacity_mw": negotiation_result.total_capacity_mw,
                "negotiation_rounds": negotiation_result.negotiation_rounds,
                "avg_satisfaction": negotiation_result.prosumer_satisfaction_avg,
                "coalition_members": [
                    {
                        "prosumer_id": member.prosumer_id,
                        "capacity_kw": member.committed_capacity_kw,
                        "price_mwh": member.agreed_price_per_mwh,
                        "satisfaction": getattr(member, 'satisfaction_score', 6.0)  # Realistic baseline if not present
                    }
                    for member in negotiation_result.coalition_members
                ]
            },
            
            # Optimization results
            "optimization": {
                "success": optimization_result.success,
                "method": "hybrid_llm_solver",
                "bid_capacity_mw": optimization_result.total_bid_capacity_mw,
                "bid_price_mwh": optimization_result.optimal_bid_price_mwh,
                "expected_profit": optimization_result.expected_profit,
                "dispatch_schedule": optimization_result.dispatch_schedule,
                "prosumer_payments": optimization_result.prosumer_payments
            },
            
            # Final bid
            "final_bid": final_bid,
            
            # Performance metrics
            "metrics": self._calculate_performance_metrics(
                market_opportunity, negotiation_result, optimization_result
            ),
            
            # Complete log
            "execution_log": cycle_log
        }
        
        return complete_result
    
    def _create_fallback_optimization(
        self,
        opportunity: MarketOpportunity,
        coalition: List[CoalitionMember]
    ) -> OptimizationResult:
        """Fallback optimization using simple weighted average pricing."""
        
        if not coalition:
            return OptimizationResult(
                success=False,
                total_bid_capacity_mw=0.0,
                optimal_bid_price_mwh=0.0,
                dispatch_schedule={},
                expected_profit=0.0,
                prosumer_payments={},
                optimization_log=["Fallback optimization: no coalition members"]
            )
        
        # Calculate weighted average price
        total_capacity = sum(member.committed_capacity_kw for member in coalition)
        weighted_price = sum(
            member.agreed_price_per_mwh * member.committed_capacity_kw
            for member in coalition
        ) / total_capacity
        
        # Add small profit margin
        bid_price = weighted_price * 1.05  # 5% markup
        bid_price = min(bid_price, opportunity.market_price_mwh * 0.95)  # Cap at 95% of market
        
        # Simple proportional dispatch
        dispatch_schedule = {}
        prosumer_payments = {}
        total_cost = 0.0
        
        for member in coalition:
            dispatch_schedule[member.prosumer_id] = member.committed_capacity_kw
            payment = member.agreed_price_per_mwh * member.committed_capacity_kw / 1000.0
            prosumer_payments[member.prosumer_id] = payment
            total_cost += payment
        
        revenue = bid_price * total_capacity / 1000.0
        profit = revenue - total_cost
        
        return OptimizationResult(
            success=True,
            total_bid_capacity_mw=total_capacity / 1000.0,
            optimal_bid_price_mwh=bid_price,
            dispatch_schedule=dispatch_schedule,
            expected_profit=profit,
            prosumer_payments=prosumer_payments,
            optimization_log=["Fallback optimization: simple weighted pricing"]
        )
    
    def _prepare_final_bid(
        self,
        opportunity: MarketOpportunity,
        negotiation_result: NegotiationResult,
        optimization_result: OptimizationResult
    ) -> Dict[str, Any]:
        """Prepare the final VPP bid for market submission."""
        
        return {
            "bid_id": f"vpp_bid_{opportunity.opportunity_id}_{uuid.uuid4().hex[:8]}",
            "opportunity_id": opportunity.opportunity_id,
            "market_type": getattr(opportunity.market_type, 'value', opportunity.market_type),
            "total_capacity_mw": optimization_result.total_bid_capacity_mw,
            "bid_price_mwh": optimization_result.optimal_bid_price_mwh,
            "delivery_timestamp": opportunity.timestamp.isoformat(),
            "duration_hours": opportunity.duration_hours,
            
            # Bid composition
            "coalition_size": len(negotiation_result.coalition_members),
            "dispatch_schedule": optimization_result.dispatch_schedule,
            "reliability_score": self._calculate_reliability_score(negotiation_result.coalition_members),
            
            # Economics
            "expected_revenue": optimization_result.optimal_bid_price_mwh * optimization_result.total_bid_capacity_mw,
            "expected_costs": sum(optimization_result.prosumer_payments.values()),
            "expected_profit": optimization_result.expected_profit,
            "profit_margin": optimization_result.expected_profit / (optimization_result.optimal_bid_price_mwh * optimization_result.total_bid_capacity_mw) if optimization_result.total_bid_capacity_mw > 0 else 0.0,
            
            # Submission metadata
            "submission_timestamp": datetime.now().isoformat(),
            "aggregator_id": "vpp_llm_agent",
            "negotiation_method": "multi_agent_llm"
        }
    
    def _calculate_reliability_score(self, coalition: List[CoalitionMember]) -> float:
        """Calculate coalition reliability score based on member characteristics."""
        if not coalition:
            return 0.0
        
        # Weighted by capacity and satisfaction
        total_capacity = sum(member.committed_capacity_kw for member in coalition)
        weighted_reliability = sum(
            getattr(member, 'satisfaction_score', 7.5) * getattr(member, 'dispatch_flexibility', 0.8) * member.committed_capacity_kw
            for member in coalition
        ) / (total_capacity * 10.0)  # Normalize satisfaction score
        
        return min(weighted_reliability, 1.0)
    
    def _calculate_performance_metrics(
        self,
        opportunity: MarketOpportunity,
        negotiation_result: NegotiationResult,
        optimization_result: OptimizationResult
    ) -> Dict[str, float]:
        """Calculate key performance metrics for the negotiation cycle."""
        
        metrics = {}
        
        # Capacity metrics
        metrics["capacity_utilization"] = (
            optimization_result.total_bid_capacity_mw / opportunity.required_capacity_mw
            if opportunity.required_capacity_mw > 0 else 0.0
        )
        
        # Economic metrics
        market_value = opportunity.market_price_mwh * optimization_result.total_bid_capacity_mw
        metrics["economic_efficiency"] = (
            optimization_result.expected_profit / market_value
            if market_value > 0 else 0.0
        )
        
        # Satisfaction metrics
        metrics["prosumer_satisfaction"] = negotiation_result.prosumer_satisfaction_avg / 10.0
        
        # Negotiation efficiency
        metrics["coalition_formation_efficiency"] = (
            len(negotiation_result.coalition_members) / max(negotiation_result.negotiation_rounds, 1)
        )
        
        # Competitiveness
        metrics["bid_competitiveness"] = (
            opportunity.market_price_mwh - optimization_result.optimal_bid_price_mwh
        ) / opportunity.market_price_mwh if opportunity.market_price_mwh > 0 else 0.0
        
        return metrics
    
    def _format_failed_result(self, cycle_log: List[str], failure_reason: str) -> Dict[str, Any]:
        """Format result for failed negotiation cycles."""
        return {
            "success": False,
            "failure_reason": failure_reason,
            "negotiation": {"success": False, "coalition_size": 0},
            "optimization": {"success": False, "bid_capacity_mw": 0.0},
            "final_bid": None,
            "metrics": {"capacity_utilization": 0.0, "prosumer_satisfaction": 0.0},
            "execution_log": cycle_log
        }
    
    def run_market_simulation_step(
        self,
        current_time: datetime,
        market_data_row: pd.Series,
        prosumer_fleet: List,
        simulation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a single time step of the market simulation.
        
        This method identifies market opportunities and runs complete
        negotiation cycles for viable opportunities.
        """
        
        step_results = {
            "timestamp": current_time.isoformat(),
            "market_data": {
                "lmp": float(market_data_row['lmp']),
                "spin_price": float(market_data_row['spin_price']),
                "nonspin_price": float(market_data_row['nonspin_price'])
            },
            "opportunities_identified": [],
            "negotiations_completed": [],
            "total_bids_submitted": 0
        }
        
        # Identify market opportunities
        opportunities = self._identify_market_opportunities(current_time, market_data_row)
        step_results["opportunities_identified"] = [opp.opportunity_id for opp in opportunities]
        
        # Run negotiations for each opportunity
        for opportunity in opportunities:
            try:
                negotiation_result = self.run_complete_negotiation_cycle(
                    opportunity, prosumer_fleet, pd.DataFrame([market_data_row]),
                    {"simulation_time": current_time, "step_state": simulation_state}
                )
                
                step_results["negotiations_completed"].append(negotiation_result)
                
                if negotiation_result["success"] and negotiation_result["final_bid"]:
                    step_results["total_bids_submitted"] += 1
                    
            except Exception as e:
                step_results["negotiations_completed"].append({
                    "success": False,
                    "opportunity_id": opportunity.opportunity_id,
                    "error": str(e)
                })
        
        return step_results
    
    def _identify_market_opportunities(
        self,
        current_time: datetime,
        market_data: pd.Series
    ) -> List[MarketOpportunity]:
        """Identify viable market opportunities from current market conditions."""
        
        opportunities = []
        
        # Energy market opportunity
        if market_data['lmp'] > 50.0:  # Threshold for profitable energy opportunity
            opportunities.append(MarketOpportunity(
                opportunity_id=f"energy_{current_time.strftime('%Y%m%d_%H%M')}",
                market_type="energy",
                timestamp=current_time + timedelta(hours=1),  # Next hour delivery
                duration_hours=1.0,
                required_capacity_mw=2.0,  # Standard 2MW opportunity
                market_price_mwh=float(market_data['lmp']),
                deadline=current_time + timedelta(minutes=45)
            ))
        
        # Spinning reserves opportunity
        if market_data['spin_price'] > 8.0:  # Threshold for spin reserves
            opportunities.append(MarketOpportunity(
                opportunity_id=f"spin_{current_time.strftime('%Y%m%d_%H%M')}",
                market_type="spin",
                timestamp=current_time + timedelta(hours=1),
                duration_hours=1.0,
                required_capacity_mw=1.0,  # Smaller ancillary service
                market_price_mwh=float(market_data['spin_price']),
                deadline=current_time + timedelta(minutes=30)
            ))
        
        return opportunities


def run_integrated_test():
    """Run a comprehensive test of the integrated negotiation system."""
    
    print("Testing Integrated Negotiation System...")
    print("="*60)
    
    # Initialize system
    system = IntegratedNegotiationSystem()
    
    # Create test market opportunity
    opportunity = MarketOpportunity(
        opportunity_id="integrated_test_001",
        market_type="energy",
        timestamp=datetime(2023, 8, 15, 12, 0, 0),
        duration_hours=1.0,
        required_capacity_mw=2.0,
        market_price_mwh=85.0,
        deadline=datetime(2023, 8, 15, 11, 45, 0)
    )
    
    # Create test prosumer fleet (simplified)
    test_prosumers = []
    for i in range(5):
        # Create minimal prosumer-like objects for testing
        prosumer = type('TestProsumer', (), {
            'prosumer_id': f'test_prosumer_{i+1:03d}',
            'bess': type('TestBESS', (), {
                'capacity_kwh': 13.5,
                'current_soc_percent': 60.0 + (i * 5),
                'min_soc_percent': 20.0,
                'max_power_kw': 5.0,
                'get_available_discharge_capacity_kw': lambda: 4.0 + (i * 0.5),
                'get_available_charge_capacity_kw': lambda: 3.0 + (i * 0.3)
            })(),
            'user_preferences': {
                'backup_power_percent': 25.0 + (i * 5),
                'risk_tolerance': ['low', 'medium', 'high'][i % 3]
            }
        })()
        test_prosumers.append(prosumer)
    
    # Create test market data
    test_market_data = pd.DataFrame({
        'timestamp': [datetime(2023, 8, 15, 12, 0, 0)],
        'lmp': [85.0],
        'spin_price': [12.5],
        'nonspin_price': [7.5]
    })
    
    print(f"Running negotiation for opportunity: {opportunity.opportunity_id}")
    print(f"Market price: ${opportunity.market_price_mwh:.2f}/MWh")
    print(f"Required capacity: {opportunity.required_capacity_mw:.1f} MW")
    print(f"Prosumer fleet size: {len(test_prosumers)}")
    print(f"")
    
    # Run complete negotiation cycle
    try:
        result = system.run_complete_negotiation_cycle(
            opportunity, test_prosumers, test_market_data
        )
        
        # Display results
        print("RESULTS:")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"\nNegotiation Results:")
            print(f"  Coalition Size: {result['negotiation']['coalition_size']}")
            print(f"  Total Capacity: {result['negotiation']['total_capacity_mw']:.2f} MW")
            print(f"  Avg Satisfaction: {result['negotiation']['avg_satisfaction']:.1f}/10")
            
            print(f"\nOptimization Results:")
            print(f"  Method: {result['optimization']['method']}")
            print(f"  Bid Capacity: {result['optimization']['bid_capacity_mw']:.2f} MW")
            print(f"  Bid Price: ${result['optimization']['bid_price_mwh']:.2f}/MWh")
            print(f"  Expected Profit: ${result['optimization']['expected_profit']:.2f}")
            
            print(f"\nFinal Bid:")
            print(f"  Bid ID: {result['final_bid']['bid_id']}")
            print(f"  Total Capacity: {result['final_bid']['total_capacity_mw']:.2f} MW")
            print(f"  Bid Price: ${result['final_bid']['bid_price_mwh']:.2f}/MWh")
            print(f"  Profit Margin: {result['final_bid']['profit_margin']:.1%}")
            print(f"  Reliability Score: {result['final_bid']['reliability_score']:.2f}")
            
            print(f"\nPerformance Metrics:")
            for metric, value in result['metrics'].items():
                print(f"  {metric}: {value:.3f}")
        
        print(f"\nExecution Log:")
        for log_entry in result['execution_log'][-10:]:  # Last 10 entries
            print(f"  - {log_entry}")
            
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "="*60)
    print("Integrated test completed.")


if __name__ == "__main__":
    run_integrated_test()
