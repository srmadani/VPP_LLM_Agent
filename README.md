# VPP LLM Agent - Virtual Power Plant with AI-Driven Negotiation

## Project Overview

This is a Virtual Power Plant (VPP) Agent Proof-of-Concept that demonstrates an agentic, negotiation-based approach for VPP bidding in the CAISO market using Large Language Models (LLMs) and multi-agent systems.

### The Innovation

Traditional VPP optimization relies on centralized mathematical models that struggle with human-centric preferences and dynamic conditions. This project proposes a **multi-agent system powered by LLMs** that simulates human-like negotiation between:

- **AggregatorAgent**: Central VPP operator identifying market opportunities
- **ProsumerAgents**: Individual DER owners with qualitative preferences

The system enables dynamic negotiation where agents evaluate market opportunities, respond with availability and pricing, and build optimal coalitions through strategic reasoning.

## Project Status

### ✅ Module 1: Data & Simulation Environment - COMPLETED
- **Status**: Fully implemented and validated
- **Deliverables**: CAISO market data, solar generation profiles, residential load patterns
- **Features**: Interactive dashboard, comprehensive validation, shared environment

### 🚧 Planned Modules
- **Module 2**: Asset Modeling & Optimization
- **Module 3**: Market Interface & Bidding  
- **Module 4**: Prosumer Agent Framework
- **Module 5**: Aggregator Agent & Negotiation
- **Module 6**: Multi-Agent Coordination & Evaluation

## Quick Start

### Prerequisites
- Python 3.8+
- API keys for NREL and GridStatus (optional - has synthetic fallbacks)

### Setup
```bash
# Clone and navigate to project
cd VPP_LLM_Agent

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Create shared virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies and run Module 1
cd module_1_data_simulation
pip install -r requirements.txt
python collect_data.py
python create_dashboard.py
```

## Project Architecture

```
VPP_LLM_Agent/
├── .env.example                     # API key template
├── .gitignore                       # Git ignore rules
├── venv/                           # Shared Python environment
├── PROJECT_STATUS.md               # Project status tracking
├── module_1_data_simulation/       # ✅ Data foundation
│   ├── collect_data.py            # CAISO & NREL data collection
│   ├── create_dashboard.py        # Interactive visualizations
│   ├── test_data.py              # Validation suite
│   └── data/                     # Generated datasets
├── module_2_asset_modeling/        # 🚧 DER asset modeling
├── module_3_market_interface/      # 🚧 CAISO market integration
├── module_4_prosumer_agents/       # 🚧 LLM-powered DER agents
├── module_5_aggregator_agent/      # 🚧 VPP operator agent
└── module_6_system_integration/    # 🚧 Full system evaluation
```

## API Keys Required

The project uses several APIs for data collection and LLM functionality:

1. **NREL API** (Optional - has synthetic fallback)
   - Purpose: Solar generation data via PVWatts
   - Get from: https://developer.nrel.gov/signup/

2. **GridStatus API** (Optional - has synthetic fallback)  
   - Purpose: CAISO market data
   - Get from: https://www.gridstatus.io/

3. **Gemini API** (For future modules)
   - Purpose: LLM-powered agent reasoning
   - Get from: https://ai.google.dev/

## Key Features

### Module 1 Features (Available Now)
- **Real-time Data Collection**: CAISO market prices and NREL solar data
- **Synthetic Data Fallbacks**: Works without API keys for development
- **Interactive Dashboard**: Comprehensive data visualization and analysis
- **Quality Assurance**: Extensive validation and testing framework
- **Shared Environment**: Centralized setup for all modules

### Planned Features
- **Multi-Agent Negotiation**: LLM-powered agents with strategic reasoning
- **Human-Centric Preferences**: Natural language constraint handling
- **Dynamic Coalition Building**: Optimal resource aggregation
- **Market Integration**: Real CAISO bidding interface
- **Performance Benchmarking**: Comparison with traditional optimization

## Technical Specifications

### Data Specifications
- **Market**: CAISO (California Independent System Operator)
- **Time Period**: August 15-21, 2023 (7-day simulation)  
- **Resolution**: 15-minute intervals (672 data points)
- **Location**: Los Angeles, CA (34.05°N, -118.24°W)
- **Assets**: 20 residential households + solar generation

### Technology Stack
- **Backend**: Python 3.8+, pandas, numpy
- **Data Sources**: GridStatus.io, NREL PVWatts API
- **Visualization**: matplotlib, seaborn
- **Future**: LangGraph, Gemini API for multi-agent systems

## Documentation

Each module contains comprehensive documentation:
- **README.md**: Setup instructions and specifications
- **Code Documentation**: Inline comments and docstrings
- **Validation Reports**: Automated testing and quality metrics
- **Dashboard Outputs**: Visual analysis and insights

## Contributing

This is a research project demonstrating VPP agent capabilities. Each module is designed to be:
- **Self-contained**: Independent functionality and testing
- **Well-documented**: Clear specifications and usage instructions  
- **Validated**: Comprehensive testing and quality assurance
- **Extensible**: Ready for integration with other modules

## Next Steps

### Phase 1: Complete Foundation (Module 1) ✅
- [x] Data collection and simulation environment
- [x] CAISO market data integration
- [x] Solar generation profiles
- [x] Residential load patterns
- [x] Interactive dashboard and analytics
- [x] Comprehensive validation framework

### Phase 2: Asset Modeling (Module 2) 🚧
**Objective**: Model distributed energy resources with operational constraints and capabilities

**Key Components**:
- **Battery Energy Storage Systems (BESS)**: State of charge, efficiency curves, degradation
- **Solar PV Systems**: DC/AC conversion, weather dependencies, forecasting
- **Electric Vehicles (EVs)**: Charging constraints, mobility patterns, V2G capabilities
- **Flexible Loads**: Demand response potential, comfort constraints

**Technical Approach**:
- Physics-based models for each asset type
- Constraint formulation for optimization
- Uncertainty modeling and forecasting
- Integration with Module 1 data

**Deliverables**:
- Asset modeling framework
- Operational constraint definitions
- Forecasting algorithms
- Integration testing with real data

### Phase 3: Market Interface (Module 3) 🚧
**Objective**: CAISO market interface for bid submission and clearing price analysis

**Key Components**:
- **Market API Integration**: Real-time price feeds, bid submission protocols
- **Bid Optimization**: Price forecasting, risk management, portfolio optimization
- **Settlement Processing**: Revenue calculation, imbalance penalties
- **Regulatory Compliance**: CAISO market rules, telemetry requirements

**Technical Approach**:
- CAISO OASIS API integration
- Mathematical optimization for bid curves
- Real-time data processing pipeline
- Risk assessment and portfolio management

**Deliverables**:
- Market interface framework
- Bid optimization algorithms
- Settlement and revenue tracking
- Compliance monitoring system

### Phase 4: Prosumer Agents (Module 4) 🚧
**Objective**: LLM-powered agents representing individual DER owners with human-centric preferences

**Key Components**:
- **Natural Language Processing**: Parse user preferences from text
- **Preference Modeling**: Comfort constraints, backup power needs, EV charging requirements
- **Strategic Reasoning**: Evaluate market opportunities, negotiate terms
- **Learning Capabilities**: Adapt to user behavior patterns over time

**Technical Approach**:
- LangGraph framework for agent orchestration
- Gemini API for natural language understanding
- Reinforcement learning for strategy adaptation
- Multi-modal preference integration

**Deliverables**:
- Prosumer agent framework
- Preference parsing and modeling
- Strategic reasoning algorithms
- Learning and adaptation mechanisms

### Phase 5: Aggregator Agent (Module 5) 🚧
**Objective**: Central VPP operator agent with strategic bidding and coalition building

**Key Components**:
- **Market Opportunity Identification**: Price forecasting, demand response events
- **Coalition Formation**: Optimal resource aggregation, risk diversification
- **Negotiation Strategy**: Dynamic pricing, incentive design
- **Real-time Dispatch**: Optimal resource allocation, constraint satisfaction

**Technical Approach**:
- Multi-agent negotiation protocols
- Game theory for strategic interactions
- Optimization under uncertainty
- Real-time control algorithms

**Deliverables**:
- Aggregator agent framework
- Coalition formation algorithms
- Negotiation and pricing strategies
- Real-time dispatch optimization

### Phase 6: System Integration (Module 6) 🚧
**Objective**: Complete system integration with performance benchmarking against traditional methods

**Key Components**:
- **End-to-End Integration**: All modules working together seamlessly
- **Performance Benchmarking**: Compare against centralized optimization baseline
- **Scalability Testing**: Large portfolio simulation, computational efficiency
- **Real-world Validation**: Integration with actual DER assets (if available)

**Technical Approach**:
- System architecture design
- Performance metrics definition
- Large-scale simulation framework
- Comparative analysis methodologies

**Deliverables**:
- Integrated VPP agent system
- Performance benchmarking results
- Scalability analysis
- Research findings and recommendations

## Development Roadmap

### Immediate Next Steps (Weeks 1-2)
1. **Begin Module 2 Development**
   - Set up asset modeling framework
   - Implement battery storage models
   - Create solar PV system models
   - Develop constraint formulation methods

2. **Enhanced Data Pipeline**
   - Add real-time data feeds
   - Implement forecasting algorithms
   - Create data quality monitoring
   - Expand to additional markets (PJM, ERCOT)

### Short-term Goals (Month 1)
1. **Complete Module 2: Asset Modeling**
   - All DER asset types modeled
   - Operational constraints defined
   - Forecasting capabilities implemented
   - Integration testing complete

2. **Begin Module 3: Market Interface**
   - CAISO API integration
   - Basic bid optimization
   - Price forecasting framework
   - Settlement processing

### Medium-term Goals (Months 2-3)
1. **Complete Modules 3-4**
   - Full market interface functionality
   - LLM-powered prosumer agents
   - Natural language preference processing
   - Strategic reasoning capabilities

2. **Begin Multi-Agent System**
   - Agent communication protocols
   - Negotiation frameworks
   - Coalition formation algorithms

### Long-term Goals (Months 3-6)
1. **Complete Modules 5-6**
   - Full aggregator agent functionality
   - End-to-end system integration
   - Performance benchmarking
   - Research publication preparation

2. **Advanced Features**
   - Machine learning integration
   - Predictive analytics
   - Advanced optimization algorithms
   - Real-world pilot deployment

## Success Metrics

### Technical Metrics
- **Data Quality**: >99% uptime, <1% data gaps
- **Forecast Accuracy**: <5% MAPE for day-ahead prices
- **System Performance**: <100ms response time for agent negotiations
- **Scalability**: Support for 1000+ prosumer agents

### Economic Metrics
- **Revenue Optimization**: >95% of theoretical maximum
- **Prosumer Satisfaction**: >90% preference compliance
- **Market Efficiency**: Reduced bid-ask spreads
- **Cost Reduction**: <50% operational costs vs traditional VPP

### Research Impact
- **Academic Publications**: Target 3-5 peer-reviewed papers
- **Industry Adoption**: Pilot deployments with utilities
- **Open Source Contribution**: Public codebase for research community
- **Patent Applications**: Novel agent-based VPP concepts

## Contributing to Development

### For Developers
1. **Choose a Module**: Pick from Modules 2-6 based on expertise
2. **Set Up Environment**: Use shared virtual environment
3. **Follow Standards**: Maintain code quality and documentation
4. **Integration Testing**: Ensure compatibility with existing modules

### For Researchers
1. **Algorithm Development**: Focus on novel optimization or learning algorithms
2. **Performance Analysis**: Comparative studies with traditional methods
3. **Use Case Expansion**: Adapt to different markets or asset types
4. **Validation Studies**: Real-world testing and validation

### For Industry Partners
1. **Pilot Programs**: Test with actual DER portfolios
2. **Market Integration**: Adapt to specific utility requirements
3. **Regulatory Compliance**: Ensure adherence to local market rules
4. **Commercial Deployment**: Scale for production use

---

**Current Status**: Module 1 Complete ✅ | Ready for Module 2 Development 🚀  
**Next Milestone**: Asset Modeling Framework (Module 2)  
**Target Completion**: End-to-end VPP Agent System within 6 months

## License

This project is for research and educational purposes. See individual module documentation for specific usage guidelines.

---

**Project Status**: Module 1 Complete ✅ | Modules 2-6 In Planning 🚧  
**Last Updated**: July 29, 2025  
**Contact**: See module documentation for specific questions
