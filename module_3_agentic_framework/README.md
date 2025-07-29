# Module 3: Agentic Framework & Communication

## Overview

Module 3 implements the multi-agent system structure using LangGraph for the VPP LLM Agent project. This module defines the communication protocols, agent personas, and negotiation workflow between AggregatorAgent and ProsumerAgents.

## Components

### Core Files

- **`agent_framework.py`**: Main framework implementing the LangGraph-based multi-agent system
- **`schemas.py`**: Pydantic models for all inter-agent communication messages
- **`prompts/aggregator_prompt.txt`**: System prompt defining AggregatorAgent behavior
- **`prompts/prosumer_prompt.txt`**: System prompt defining ProsumerAgent behavior
- **`test_module3.py`**: Comprehensive test suite validating all components
- **`requirements.txt`**: Python dependencies for this module

### Architecture

The module implements a state-based workflow using LangGraph with the following structure:

```
AggregatorAgent → announces opportunity → ProsumerAgents
       ↓                                        ↓
   evaluates bids ← submit initial bids ←───────┘
       ↓
   multi-round negotiation process
       ↓
   coalition formation → final bid optimization
```

## Requirements

### Python Dependencies

```
pandas==2.2.2
numpy==1.26.4
pydantic==2.8.2
python-dotenv==1.0.1
langgraph==0.2.16
langchain==0.2.16
langchain-google-genai==1.0.10
google-generativeai==0.7.2
typing-extensions==4.12.2
```

### Prerequisites

- Python 3.8+
- Gemini API key (set in `.env` file)
- Module 2 components (prosumer models and fleet generator)

## Installation

```bash
# Navigate to module directory
cd module_3_agentic_framework

# Install dependencies in virtual environment
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from agent_framework import VPPAgentFramework
from schemas import MarketOpportunity, MarketOpportunityType

# Initialize framework
framework = VPPAgentFramework()

# Create market opportunity
opportunity = framework.create_market_opportunity(
    market_type="energy",
    required_capacity_mw=5.0,
    market_price_mwh=75.0,
    duration_hours=1.0
)

# Run negotiation
result = framework.run_negotiation(opportunity, fleet_size=50)

# Access results
print(f"Coalition size: {len(result['committed_coalition'])}")
print(f"Capacity secured: {result['current_capacity_secured_mw']:.2f} MW")
print(f"Success: {result['success']}")
```

### Advanced Configuration

```python
# Custom market opportunity
from datetime import datetime, timedelta

opportunity = MarketOpportunity(
    opportunity_id="custom_opp_001",
    market_type=MarketOpportunityType.SPIN,
    timestamp=datetime.now() + timedelta(hours=2),
    duration_hours=4.0,
    required_capacity_mw=10.0,
    market_price_mwh=120.0,
    deadline=datetime.now() + timedelta(minutes=45),
    ramp_rate_required=5.0,  # MW/min
    minimum_duration=1.0     # hours
)

# Run with custom opportunity
result = framework.run_negotiation(opportunity)
```

## API Reference

### VPPAgentFramework

Main class managing the multi-agent VPP negotiation system.

#### Methods

- **`__init__(api_key: Optional[str] = None)`**: Initialize framework with Gemini API
- **`initialize_prosumer_fleet(fleet_size: int = 50)`**: Create prosumer fleet for negotiation
- **`create_market_opportunity(**kwargs)`**: Generate sample market opportunity
- **`run_negotiation(opportunity, fleet_size)`**: Execute complete negotiation workflow

### Communication Schemas

#### MarketOpportunity
Market opportunity announced by AggregatorAgent.

```python
MarketOpportunity(
    opportunity_id: str,
    market_type: MarketOpportunityType,
    timestamp: datetime,
    duration_hours: float,
    required_capacity_mw: float,
    market_price_mwh: float,
    deadline: datetime
)
```

#### ProsumerBid
Bid response from ProsumerAgent.

```python
ProsumerBid(
    prosumer_id: str,
    opportunity_id: str,
    is_available: bool,
    available_capacity_kw: float,
    minimum_price_per_mwh: float,
    user_preferences: Dict[str, Any]
)
```

#### AggregatorOffer
Counter-offer from AggregatorAgent during negotiation.

```python
AggregatorOffer(
    offer_id: str,
    opportunity_id: str,
    target_prosumer_ids: List[str],
    offered_price_per_mwh: float,
    requested_capacity_kw: float,
    round_number: int
)
```

#### ProsumerResponse
Response to AggregatorOffer.

```python
ProsumerResponse(
    response_id: str,
    offer_id: str,
    prosumer_id: str,
    is_accepted: bool,
    rejection_reason: Optional[str]
)
```

#### CoalitionMember
Final coalition member details.

```python
CoalitionMember(
    prosumer_id: str,
    committed_capacity_kw: float,
    agreed_price_per_mwh: float,
    dispatch_schedule: Dict[str, float],
    asset_type: str,
    technical_constraints: Dict[str, Any]
)
```

### Workflow Nodes

The LangGraph workflow consists of these nodes:

1. **`announce_opportunity`**: AggregatorAgent broadcasts market opportunity
2. **`collect_initial_bids`**: Gather ProsumerAgent responses
3. **`evaluate_bids`**: AggregatorAgent analyzes received bids
4. **`make_counter_offers`**: Send targeted offers to selected prosumers
5. **`collect_responses`**: Gather responses to counter-offers
6. **`form_coalition`**: Create final coalition from committed prosumers
7. **`finalize_negotiation`**: Generate summary and results

## Testing

### Run All Tests

```bash
python test_module3.py
```

### Test Components

- **Schema Validation**: Tests all Pydantic models work correctly
- **Framework Initialization**: Validates proper setup and configuration
- **Workflow Structure**: Confirms LangGraph workflow is properly constructed
- **Agent Prompts**: Verifies system prompts are loaded and formatted
- **End-to-End Negotiation**: Complete workflow execution with validation

### Expected Output

```
VPP Agent Framework Validation - Module 3
==================================================
🧪 Testing Pydantic schemas...
   ✅ MarketOpportunity schema working
   ✅ All schemas validated successfully

🧪 Testing framework initialization...
   ✅ Framework initialized successfully
   ✅ Prosumer fleet created successfully
   ✅ Market opportunity created successfully

🧪 Testing workflow structure...
   ✅ Workflow compiled successfully
   ✅ Workflow structure validated

🧪 Testing agent prompts...
   ✅ Agent prompts loaded and validated

🧪 Testing simple negotiation...
   ✅ Negotiation completed successfully
   
🎉 All tests passed successfully!
```

## Integration Points

### With Module 2 (Asset Modeling)

- Imports `Prosumer`, `BESS`, `ElectricVehicle`, `SolarPV` classes
- Uses `FleetGenerator` to create diverse prosumer fleets
- Accesses prosumer asset characteristics for bid simulation

### With Module 4 (Core Logic)

- Provides communication schemas and agent framework
- Defines workflow structure for negotiation implementation
- Establishes agent personas and behavioral guidelines

## Configuration

### Environment Variables

Required in `.env` file:

```bash
# Gemini API Key for LLM functionality
GEMINI_API_KEY=your_gemini_api_key_here
```

### Agent Behavior

Agent behavior is controlled through system prompts in the `prompts/` directory:

- **AggregatorAgent**: Focuses on profit optimization, risk management, and coalition building
- **ProsumerAgent**: Protects user preferences while pursuing fair compensation

## Performance Metrics

### Negotiation Metrics

- **Coalition Formation Time**: Time to reach agreement
- **Capacity Coverage**: Percentage of required capacity secured
- **Price Efficiency**: Average price vs. market rates
- **Prosumer Participation**: Bid response rates
- **Negotiation Rounds**: Rounds needed for convergence

### Technical Performance

- **Framework Initialization**: < 1 second
- **Fleet Generation**: 50 prosumers in < 0.5 seconds
- **Workflow Compilation**: < 0.2 seconds
- **Single Negotiation**: 15-prosumer fleet in < 5 seconds

## Limitations

### Current Implementation

- **Simulated LLM Responses**: Module 3 uses rule-based bid simulation instead of actual LLM reasoning
- **Basic Negotiation Logic**: Counter-offers use simple pricing adjustments
- **Limited Asset Integration**: Simplified capacity calculation from asset characteristics
- **No Real-time Updates**: Static prosumer availability during negotiation

### Future Enhancements (Module 4)

- Full LLM-powered agent reasoning and decision-making
- Advanced negotiation strategies and game theory implementation
- Dynamic asset state updates during negotiation
- Sophisticated preference handling and constraint satisfaction

## Error Handling

The framework includes comprehensive error handling for:

- **API Key Validation**: Checks for required Gemini API key
- **Schema Validation**: Pydantic ensures all messages conform to defined schemas
- **Workflow Execution**: LangGraph handles node execution failures gracefully
- **Asset Model Integration**: Validates prosumer fleet compatibility

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

framework = VPPAgentFramework()
result = framework.run_negotiation(opportunity)
```

### Common Issues

1. **Missing API Key**: Ensure `GEMINI_API_KEY` is set in `.env`
2. **Import Errors**: Verify Module 2 is in Python path
3. **Schema Validation**: Check all required fields in communication messages
4. **Memory Usage**: Large fleets (>100 prosumers) may require increased memory

## Next Steps

Module 3 provides the foundation for Module 4 implementation:

1. **Agent Reasoning**: Replace simulated responses with actual LLM-powered decision-making
2. **Optimization Integration**: Add "LLM-to-Solver" hybrid optimization
3. **Advanced Negotiation**: Implement multi-round strategic negotiation algorithms
4. **Performance Optimization**: Enhance efficiency for large-scale deployments

## File Structure

```
module_3_agentic_framework/
├── agent_framework.py          # Main framework implementation
├── schemas.py                  # Communication schemas
├── test_module3.py            # Test suite
├── requirements.txt           # Dependencies
├── README.md                  # This documentation
└── prompts/
    ├── aggregator_prompt.txt  # AggregatorAgent system prompt
    └── prosumer_prompt.txt    # ProsumerAgent system prompt
```

---

**Module Status**: ✅ Complete and Ready for Module 4 Integration  
**Last Updated**: July 29, 2025  
**Dependencies**: Module 2 (Asset Modeling)  
**Next Module**: Module 4 (Core Negotiation & Optimization Logic)
