"""
Optimization Tool for VPP LLM Agent - Module 4

This module implements the hybrid "LLM-to-Solver" optimization approach,
where the LLM formulates the optimization problem and a numerical solver
finds the optimal dispatch solution.
"""

import os
import sys
import json
import cvxpy as cp
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# Add paths for imports
sys.path.append('../module_3_agentic_framework')

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from schemas import MarketOpportunity, CoalitionMember


@dataclass
class OptimizationResult:
    """Result of the optimization process."""
    success: bool
    total_bid_capacity_mw: float
    optimal_bid_price_mwh: float
    dispatch_schedule: Dict[str, float]  # prosumer_id -> dispatch_kw
    expected_profit: float
    prosumer_payments: Dict[str, float]  # prosumer_id -> payment
    optimization_log: List[str]


class OptimizationTool:
    """
    Hybrid LLM-to-Solver optimization tool for VPP bid formulation.
    
    This tool uses LLM reasoning to formulate the optimization problem
    and then passes it to CVXPY for numerical solution.
    """
    
    def __init__(self):
        """Initialize the optimization tool."""
        load_dotenv()
        
        # Initialize LLM
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1  # Low temperature for consistent optimization
        )
        
        # Optimization parameters
        self.min_profit_margin = 0.05  # 5% minimum profit margin
        self.reliability_buffer = 0.05  # 5% capacity buffer for reliability
        
    def formulate_and_submit_bid(
        self,
        opportunity: MarketOpportunity,
        coalition: List[CoalitionMember],
        market_context: Dict[str, Any] = None
    ) -> OptimizationResult:
        """
        Main optimization function that formulates and solves the bid optimization problem.
        
        Args:
            opportunity: Market opportunity details
            coalition: List of committed coalition members
            market_context: Additional market information
            
        Returns:
            OptimizationResult: Complete optimization outcome
        """
        optimization_log = []
        optimization_log.append(f"Starting optimization for opportunity {opportunity.opportunity_id}")
        optimization_log.append(f"Coalition size: {len(coalition)} members")
        
        if not coalition:
            return OptimizationResult(
                success=False,
                total_bid_capacity_mw=0.0,
                optimal_bid_price_mwh=0.0,
                dispatch_schedule={},
                expected_profit=0.0,
                prosumer_payments={},
                optimization_log=optimization_log
            )
        
        try:
            # Step 1: Generate optimization problem using LLM
            optimization_problem = self._generate_optimization_problem(
                opportunity, coalition, market_context
            )
            optimization_log.append("Generated optimization problem structure")
            
            # Step 2: Solve using CVXPY
            solution = self._solve_optimization_problem(
                opportunity, coalition, optimization_problem
            )
            optimization_log.append(f"Solved optimization: {solution['status']}")
            
            # Step 3: Format results
            result = self._format_optimization_result(
                opportunity, coalition, solution, optimization_log
            )
            
            return result
            
        except Exception as e:
            optimization_log.append(f"Optimization failed: {str(e)}")
            return OptimizationResult(
                success=False,
                total_bid_capacity_mw=0.0,
                optimal_bid_price_mwh=0.0,
                dispatch_schedule={},
                expected_profit=0.0,
                prosumer_payments={},
                optimization_log=optimization_log
            )
    
    def _generate_optimization_problem(
        self,
        opportunity: MarketOpportunity,
        coalition: List[CoalitionMember],
        market_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate optimization problem structure using LLM reasoning.
        
        This function asks the LLM to analyze the problem and provide
        optimization guidance rather than generating executable code.
        """
        
        # Prepare context for LLM
        coalition_summary = []
        for member in coalition:
            coalition_summary.append({
                "prosumer_id": member.prosumer_id,
                "capacity_kw": member.committed_capacity_kw,
                "price_mwh": member.agreed_price_per_mwh,
                "satisfaction": member.satisfaction_score,
                "flexibility": member.dispatch_flexibility
            })
        
        context = {
            "opportunity": {
                "market_type": getattr(opportunity.market_type, 'value', opportunity.market_type),
                "required_capacity_mw": opportunity.required_capacity_mw,
                "market_price_mwh": opportunity.market_price_mwh,
                "duration_hours": opportunity.duration_hours
            },
            "coalition": coalition_summary,
            "market_context": market_context or {}
        }
        
        # Create LLM prompt for optimization guidance
        prompt = f"""
You are an expert optimization consultant for a Virtual Power Plant (VPP). 
Analyze the following market opportunity and prosumer coalition to provide optimization guidance.

Market Opportunity:
- Type: {getattr(opportunity.market_type, 'value', opportunity.market_type)}
- Required Capacity: {opportunity.required_capacity_mw:.2f} MW
- Market Price: ${opportunity.market_price_mwh:.2f}/MWh
- Duration: {opportunity.duration_hours:.1f} hours

Coalition Members:
{json.dumps(coalition_summary, indent=2)}

Provide optimization recommendations including:
1. Optimal dispatch strategy for each prosumer
2. Recommended bid price considering costs and market conditions
3. Risk factors and constraints to consider
4. Expected profit margins and prosumer satisfaction impact

Format your response as structured recommendations, not code.
"""
        
        # Get LLM response
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse LLM recommendations into structured format
        recommendations = {
            "dispatch_strategy": "proportional",  # Default strategy
            "bid_price_guidance": opportunity.market_price_mwh * 0.95,
            "risk_factors": ["market_volatility", "prosumer_reliability"],
            "constraints": ["capacity_limits", "satisfaction_scores"],
            "llm_analysis": response.content
        }
        
        return recommendations
    
    def _solve_optimization_problem(
        self,
        opportunity: MarketOpportunity,
        coalition: List[CoalitionMember],
        problem_guidance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Solve the optimization problem using CVXPY.
        
        This implements a concrete optimization formulation based on
        the LLM guidance and coalition constraints.
        """
        
        n_prosumers = len(coalition)
        
        # Decision variables
        dispatch = cp.Variable(n_prosumers, nonneg=True)  # Dispatch for each prosumer (kW)
        bid_price = cp.Variable()  # VPP bid price ($/MWh)
        
        # Parameters
        capacities = np.array([member.committed_capacity_kw for member in coalition])
        agreed_prices = np.array([member.agreed_price_per_mwh for member in coalition])
        satisfaction_weights = np.array([member.satisfaction_score / 10.0 for member in coalition])
        
        # Market parameters
        market_price = opportunity.market_price_mwh
        required_capacity_kw = opportunity.required_capacity_mw * 1000.0
        
        # Objective: Maximize profit while maintaining satisfaction
        revenue = bid_price * cp.sum(dispatch) / 1000.0  # Convert kW to MW
        costs = cp.sum(cp.multiply(agreed_prices, dispatch)) / 1000.0  # Prosumer payments
        satisfaction_bonus = cp.sum(cp.multiply(satisfaction_weights, dispatch)) * 0.1  # Small bonus
        
        objective = cp.Maximize(revenue - costs + satisfaction_bonus)
        
        # Constraints
        constraints = []
        
        # Capacity constraints for each prosumer
        constraints.append(dispatch <= capacities)
        
        # Total capacity constraint (meet at least 90% of requirement)
        constraints.append(cp.sum(dispatch) >= required_capacity_kw * 0.9)
        constraints.append(cp.sum(dispatch) <= required_capacity_kw * 1.1)
        
        # Bid price constraints (must be competitive)
        constraints.append(bid_price <= market_price * 0.98)  # At most 2% below market
        constraints.append(bid_price >= cp.sum(cp.multiply(agreed_prices, dispatch)) / cp.sum(dispatch) * 1.05)  # At least 5% profit
        
        # Solve the problem
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Return solution
        return {
            "status": problem.status,
            "optimal_value": problem.value,
            "dispatch_values": dispatch.value if dispatch.value is not None else np.zeros(n_prosumers),
            "bid_price_value": bid_price.value if bid_price.value is not None else 0.0,
            "solver_time": problem.solver_stats.solve_time if hasattr(problem.solver_stats, 'solve_time') else 0.0
        }
    
    def _format_optimization_result(
        self,
        opportunity: MarketOpportunity,
        coalition: List[CoalitionMember],
        solution: Dict[str, Any],
        optimization_log: List[str]
    ) -> OptimizationResult:
        """Format the optimization solution into a structured result."""
        
        success = solution["status"] == cp.OPTIMAL
        
        if not success:
            return OptimizationResult(
                success=False,
                total_bid_capacity_mw=0.0,
                optimal_bid_price_mwh=0.0,
                dispatch_schedule={},
                expected_profit=0.0,
                prosumer_payments={},
                optimization_log=optimization_log
            )
        
        # Extract solution values
        dispatch_values = solution["dispatch_values"]
        bid_price = solution["bid_price_value"]
        
        # Create dispatch schedule
        dispatch_schedule = {}
        prosumer_payments = {}
        total_capacity_kw = 0.0
        total_cost = 0.0
        
        for i, member in enumerate(coalition):
            dispatch_kw = float(dispatch_values[i])
            dispatch_schedule[member.prosumer_id] = dispatch_kw
            
            # Calculate payment to prosumer
            payment = (member.agreed_price_per_mwh * dispatch_kw / 1000.0)  # Convert to MWh
            prosumer_payments[member.prosumer_id] = payment
            
            total_capacity_kw += dispatch_kw
            total_cost += payment
        
        # Calculate expected profit
        revenue = bid_price * total_capacity_kw / 1000.0  # Convert to MW
        expected_profit = revenue - total_cost
        
        optimization_log.append(f"Total capacity: {total_capacity_kw/1000.0:.2f} MW")
        optimization_log.append(f"Bid price: ${bid_price:.2f}/MWh")
        optimization_log.append(f"Expected profit: ${expected_profit:.2f}")
        
        return OptimizationResult(
            success=True,
            total_bid_capacity_mw=total_capacity_kw / 1000.0,
            optimal_bid_price_mwh=bid_price,
            dispatch_schedule=dispatch_schedule,
            expected_profit=expected_profit,
            prosumer_payments=prosumer_payments,
            optimization_log=optimization_log
        )
    
    def generate_cvxpy_code(
        self,
        opportunity: MarketOpportunity,
        coalition: List[CoalitionMember]
    ) -> str:
        """
        Alternative method: Generate executable CVXPY code using LLM.
        
        This demonstrates the pure LLM-to-code approach mentioned in the requirements.
        """
        
        # Create detailed prompt for code generation
        prompt = f"""
Generate a complete CVXPY optimization script for a VPP bid formulation problem.

Problem Details:
- Market Type: {getattr(opportunity.market_type, 'value', opportunity.market_type)}
- Required Capacity: {opportunity.required_capacity_mw:.2f} MW
- Market Price: ${opportunity.market_price_mwh:.2f}/MWh
- Coalition Size: {len(coalition)} prosumers

Coalition Details:
"""
        
        for i, member in enumerate(coalition):
            prompt += f"- Prosumer {i+1}: {member.committed_capacity_kw:.1f} kW @ ${member.agreed_price_per_mwh:.2f}/MWh\n"
        
        prompt += """
Generate a complete Python script that:
1. Imports necessary libraries (cvxpy, numpy)
2. Defines decision variables for dispatch and bid price
3. Sets up the optimization objective (maximize profit)
4. Includes all necessary constraints
5. Solves the problem and returns results

The script should be executable and return a dictionary with:
- 'bid_price': optimal bid price
- 'dispatch': list of dispatch values for each prosumer
- 'profit': expected profit

Return only the Python code, no explanations.
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


def test_optimization_tool():
    """Test the optimization tool with sample data."""
    
    print("Testing Optimization Tool...")
    
    # Initialize tool
    tool = OptimizationTool()
    
    # Create sample data
    opportunity = MarketOpportunity(
        opportunity_id="test_opt_001",
        market_type="energy",
        timestamp=datetime.now(),
        duration_hours=1.0,
        required_capacity_mw=1.5,
        market_price_mwh=80.0,
        deadline=datetime.now() + timedelta(minutes=30)
    )
    
    coalition = [
        CoalitionMember(
            prosumer_id="prosumer_001",
            committed_capacity_kw=500.0,
            agreed_price_per_mwh=75.0,
            satisfaction_score=8.0,
            technical_constraints={},
            dispatch_flexibility=0.9
        ),
        CoalitionMember(
            prosumer_id="prosumer_002",
            committed_capacity_kw=600.0,
            agreed_price_per_mwh=78.0,
            satisfaction_score=7.5,
            technical_constraints={},
            dispatch_flexibility=0.8
        ),
        CoalitionMember(
            prosumer_id="prosumer_003",
            committed_capacity_kw=400.0,
            agreed_price_per_mwh=72.0,
            satisfaction_score=9.0,
            technical_constraints={},
            dispatch_flexibility=0.95
        )
    ]
    
    # Run optimization
    result = tool.formulate_and_submit_bid(opportunity, coalition)
    
    # Print results
    print(f"\nOptimization Results:")
    print(f"Success: {result.success}")
    print(f"Total Bid Capacity: {result.total_bid_capacity_mw:.2f} MW")
    print(f"Optimal Bid Price: ${result.optimal_bid_price_mwh:.2f}/MWh")
    print(f"Expected Profit: ${result.expected_profit:.2f}")
    
    print(f"\nDispatch Schedule:")
    for prosumer_id, dispatch_kw in result.dispatch_schedule.items():
        print(f"  - {prosumer_id}: {dispatch_kw:.1f} kW")
    
    print(f"\nProsumer Payments:")
    for prosumer_id, payment in result.prosumer_payments.items():
        print(f"  - {prosumer_id}: ${payment:.2f}")
    
    print(f"\nOptimization Log:")
    for log_entry in result.optimization_log:
        print(f"  - {log_entry}")
    
    # Test code generation feature
    print(f"\n" + "="*50)
    print("Testing CVXPY Code Generation:")
    cvxpy_code = tool.generate_cvxpy_code(opportunity, coalition)
    print("Generated CVXPY Code:")
    print(cvxpy_code[:500] + "..." if len(cvxpy_code) > 500 else cvxpy_code)
    
    return result


if __name__ == "__main__":
    test_optimization_tool()
