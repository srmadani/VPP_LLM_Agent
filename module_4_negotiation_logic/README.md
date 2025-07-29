# Module 4: Core Negotiation Logic & Optimization

## Overview

Module 4 implements the core LLM-powered negotiation algorithms and hybrid optimization for the VPP agent system. This module integrates with the LangGraph framework from Module 3 to provide complete multi-round negotiation capabilities and LLM-to-solver optimization for bid formulation.

## Architecture

The module consists of three main components:

1. **Core Negotiation Engine** (`main_negotiation.py`): Implements multi-round negotiation workflow
2. **Optimization Tool** (`optimization_tool.py`): Hybrid LLM-to-solver optimization system
3. **Integrated System** (`integrated_system.py`): Complete orchestration and coordination

## Features

### Multi-Round Negotiation
- **Round 1**: Initial bid collection from all prosumers
- **Round 2**: Strategic counter-offers to optimize coalition composition
- **Round 3**: Final coalition formation and commitment

### LLM-Powered Reasoning
- Strategic evaluation of prosumer bids
- Dynamic counter-offer generation
- Coalition formation optimization
- Natural language preference handling

### Hybrid Optimization
- LLM problem formulation and guidance
- CVXPY numerical optimization
- Profit maximization with satisfaction constraints
- Competitive bid pricing

## Technical Implementation

### Negotiation Engine
```python
from main_negotiation import CoreNegotiationEngine

engine = CoreNegotiationEngine()
result = engine.run_negotiation(market_opportunity, prosumer_fleet, market_data)
```

### Optimization Tool
```python
from optimization_tool import OptimizationTool

tool = OptimizationTool()
optimization = tool.formulate_and_submit_bid(opportunity, coalition)
```

### Integrated System
```python
from integrated_system import IntegratedNegotiationSystem

system = IntegratedNegotiationSystem()
result = system.run_complete_negotiation_cycle(opportunity, fleet, market_data)
```

## Dependencies

### From Previous Modules
- **Module 1**: Market data (market_data.csv, solar_data.csv)
- **Module 2**: Prosumer models (prosumer_models.py, fleet_generator.py)
- **Module 3**: Agent framework (schemas.py, agent_framework.py)

### External Libraries
- **LangChain/LangGraph**: Multi-agent framework and LLM integration
- **CVXPY**: Convex optimization solver
- **Pandas/NumPy**: Data processing and numerical operations
- **Google Gemini API**: LLM reasoning and problem formulation

## Input Requirements

### Market Opportunity
```python
MarketOpportunity(
    opportunity_id="energy_20230815_1200",
    market_type="energy",  # or "spin", "nonspin"
    timestamp=datetime(2023, 8, 15, 12, 0, 0),
    duration_hours=1.0,
    required_capacity_mw=2.0,
    market_price_mwh=85.0,
    deadline=datetime(2023, 8, 15, 11, 45, 0)
)
```

### Prosumer Fleet
- List of Prosumer objects from Module 2
- Each with BESS, user preferences, and constraints
- Minimum 3 prosumers recommended for viable coalition

### Market Data
- Current CAISO LMP and ancillary service prices
- Pandas DataFrame with timestamp, lmp, spin_price, nonspin_price

## Output Specifications

### Negotiation Result
```json
{
    "success": true,
    "coalition_members": [
        {
            "prosumer_id": "prosumer_001",
            "committed_capacity_kw": 500.0,
            "agreed_price_per_mwh": 78.5,
            "satisfaction_score": 8.2
        }
    ],
    "total_capacity_mw": 2.1,
    "negotiation_rounds": 3,
    "final_bid_price": 82.5,
    "prosumer_satisfaction_avg": 7.8
}
```

### Optimization Result
```json
{
    "success": true,
    "total_bid_capacity_mw": 2.1,
    "optimal_bid_price_mwh": 82.5,
    "expected_profit": 45.2,
    "dispatch_schedule": {
        "prosumer_001": 500.0,
        "prosumer_002": 600.0,
        "prosumer_003": 1000.0
    },
    "prosumer_payments": {
        "prosumer_001": 39.25,
        "prosumer_002": 48.0,
        "prosumer_003": 75.0
    }
}
```

### Final VPP Bid
```json
{
    "bid_id": "vpp_bid_energy_20230815_a1b2c3d4",
    "opportunity_id": "energy_20230815_1200",
    "total_capacity_mw": 2.1,
    "bid_price_mwh": 82.5,
    "expected_profit": 45.2,
    "profit_margin": 0.26,
    "reliability_score": 0.85,
    "coalition_size": 3
}
```

## Installation and Setup

### Environment Setup
```bash
cd module_4_negotiation_logic
pip install -r requirements.txt
```

### API Configuration
Ensure `.env` file contains:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Path Configuration
The module expects the following directory structure:
```
VPP_LLM_Agent/
├── module_1_data_simulation/
├── module_2_asset_modeling/
├── module_3_agentic_framework/
└── module_4_negotiation_logic/  # This module
```

## Usage Examples

### Basic Negotiation Test
```bash
python main_negotiation.py
```

### Optimization Tool Test
```bash
python optimization_tool.py
```

### Integrated System Test
```bash
python integrated_system.py
```

### Custom Integration
```python
import sys
sys.path.append('../module_2_asset_modeling')
sys.path.append('../module_3_agentic_framework')

from integrated_system import IntegratedNegotiationSystem
from fleet_generator import FleetGenerator
import pandas as pd

# Initialize system
system = IntegratedNegotiationSystem()

# Load market data
market_data = pd.read_csv('../module_1_data_simulation/data/market_data.csv')

# Generate prosumer fleet
fleet_gen = FleetGenerator()
prosumers = fleet_gen.create_prosumer_fleet(20)

# Create market opportunity
opportunity = MarketOpportunity(...)

# Run negotiation
result = system.run_complete_negotiation_cycle(
    opportunity, prosumers, market_data.iloc[0:1]
)
```

## Performance Characteristics

### Negotiation Engine
- **Coalition Formation**: 3-10 prosumers per coalition
- **Negotiation Rounds**: Fixed 3-round structure
- **Success Rate**: >80% for viable market opportunities
- **Processing Time**: <30 seconds per negotiation cycle

### Optimization Tool
- **Problem Size**: Up to 20 decision variables (prosumers)
- **Solver**: CVXPY with ECOS backend
- **Solution Time**: <5 seconds for typical problems
- **Optimality**: Guaranteed global optimum for convex formulations

### LLM Integration
- **Model**: Google Gemini Pro
- **Temperature**: 0.1-0.3 for consistent reasoning
- **Token Usage**: ~1000-3000 tokens per negotiation
- **Response Time**: 2-8 seconds per LLM call

## Key Algorithms

### Bid Evaluation Scoring
```python
def bid_score(bid: ProsumerBid) -> float:
    price_score = 1.0 / max(bid.minimum_price_per_mwh, 1.0)
    capacity_score = bid.available_capacity_kw / 1000.0
    reliability_score = 1.0
    capacity_bonus = min(bid.available_capacity_kw / 10.0, 2.0)
    return price_score + capacity_score + reliability_score + capacity_bonus
```

### Coalition Formation
- Sort prosumers by cost-effectiveness score
- Select minimum viable coalition size (3+ members)
- Ensure 80% of required capacity is met
- Maximize satisfaction while minimizing cost

### Optimization Objective
```python
# Maximize: Revenue - Costs + Satisfaction Bonus
objective = cp.Maximize(
    bid_price * cp.sum(dispatch) / 1000.0 -  # Revenue
    cp.sum(cp.multiply(agreed_prices, dispatch)) / 1000.0 +  # Costs
    cp.sum(cp.multiply(satisfaction_weights, dispatch)) * 0.1  # Bonus
)
```

## Error Handling

### Negotiation Failures
- No available prosumers: Return failed result with empty coalition
- Insufficient capacity: Attempt with relaxed constraints (80% requirement)
- LLM API errors: Use fallback rule-based pricing

### Optimization Failures
- Infeasible problem: Apply fallback weighted-average pricing
- Solver timeout: Return best feasible solution found
- Numerical issues: Use simplified linear formulation

## Testing and Validation

### Unit Tests
- Individual component functionality
- Edge case handling
- API integration validation

### Integration Tests
- End-to-end negotiation cycles
- Multi-opportunity scenarios
- Performance benchmarking

### Validation Metrics
- Coalition formation success rate
- Optimization convergence rate
- Prosumer satisfaction maintenance
- Profit margin achievement

## Limitations and Considerations

### Technical Limitations
- Fixed 3-round negotiation structure
- Maximum 20 prosumers per coalition
- CVXPY solver dependencies
- Gemini API rate limits

### Economic Assumptions
- Static market prices during negotiation
- Perfect information about prosumer assets
- No transmission constraints
- Simplified operational costs

### Scalability Considerations
- LLM token costs scale with coalition size
- Optimization complexity is O(n²) in prosumer count
- Memory usage scales linearly with fleet size

## Future Enhancements

### Algorithmic Improvements
- Dynamic negotiation round adaptation
- Multi-objective optimization with Pareto frontiers
- Reinforcement learning for negotiation strategy
- Stochastic optimization under uncertainty

### Technical Enhancements
- Distributed optimization for large fleets
- Real-time constraint updates
- Advanced solver integration (Gurobi, CPLEX)
- Caching and memoization for repeated scenarios

## Integration with Other Modules

### Module 1 Integration
- Reads market_data.csv for price context
- Uses timestamp alignment for simulation

### Module 2 Integration
- Imports Prosumer and BESS classes
- Uses FleetGenerator for test scenarios
- Accesses asset constraints and preferences

### Module 3 Integration
- Extends LangGraph agent framework
- Uses Pydantic schemas for type safety
- Integrates with agent prompt templates

### Module 5 Integration (Future)
- Provides negotiation results for benchmarking
- Interfaces with simulation orchestration
- Supports performance comparison metrics

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure proper Python path configuration
2. **API Key Issues**: Verify GEMINI_API_KEY in .env file
3. **CVXPY Installation**: May require conda for optimal performance
4. **Memory Issues**: Reduce fleet size for large-scale testing

### Debug Tools
- Comprehensive logging in all components
- Negotiation trace visualization
- Optimization problem inspection
- Performance profiling utilities

## Contributing

When extending this module:
1. Maintain compatibility with Module 3 schemas
2. Add comprehensive unit tests
3. Document new algorithms and parameters
4. Update performance benchmarks
5. Ensure proper error handling and fallbacks
