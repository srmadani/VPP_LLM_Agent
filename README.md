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

### ✅ Module 2: Prosumer Asset & Behavior Modeling - COMPLETED
- **Status**: Production ready with comprehensive testing
- **Deliverables**: BESS, EV, and Solar PV models with realistic constraints
- **Features**: Fleet generation, LLM-powered parsing, physics-based simulation

### ✅ Module 3: Agentic Framework & Communication - COMPLETED
- **Status**: LangGraph-based multi-agent system ready for negotiation
- **Deliverables**: Agent personas, communication schemas, workflow management
- **Features**: Multi-round negotiation, coalition formation, market integration

### 🚧 Remaining Modules
- **Module 4**: Core Negotiation & Optimization Logic
- **Module 5**: Simulation Orchestration & Benchmarking
- **Module 6**: Visualization Dashboard

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
├── module_2_asset_modeling/        # ✅ DER asset modeling
│   ├── prosumer_models.py         # BESS, EV, Solar PV classes
│   ├── fleet_generator.py         # Prosumer fleet creation
│   ├── llm_parser.py             # Natural language parsing
│   └── test_module2.py           # Comprehensive test suite
├── module_3_agentic_framework/     # ✅ Multi-agent system
│   ├── agent_framework.py         # LangGraph negotiation workflow
│   ├── schemas.py                 # Communication protocols
│   ├── prompts/                   # Agent system prompts
│   ├── test_module3.py           # Framework validation
│   └── demo_module3.py           # Interactive demonstrations
├── module_4_negotiation_logic/     # 🚧 Core algorithms
├── module_5_simulation_orchestration/ # 🚧 Benchmarking engine
└── module_6_visualization_dashboard/  # 🚧 Web interface
```

## API Keys Required

The project uses several APIs for data collection and LLM functionality:

1. **NREL API** (Optional - has synthetic fallback)
   - Purpose: Solar generation data via PVWatts
   - Get from: https://developer.nrel.gov/signup/

2. **GridStatus API** (Optional - has synthetic fallback)  
   - Purpose: CAISO market data
   - Get from: https://www.gridstatus.io/

3. **Gemini API** (For Modules 2-6)
   - Purpose: LLM-powered agent reasoning and natural language processing
   - Get from: https://ai.google.dev/

## Key Features

### Module 1 Features (Available Now)
- **Real-time Data Collection**: CAISO market prices and NREL solar data
- **Synthetic Data Fallbacks**: Works without API keys for development
- **Interactive Dashboard**: Comprehensive data visualization and analysis
- **Quality Assurance**: Extensive validation and testing framework
- **Shared Environment**: Centralized setup for all modules

### Module 2 Features (Available Now)
- **Asset Modeling**: Physics-based BESS, EV, and Solar PV models
- **Fleet Generation**: Realistic prosumer diversity with California adoption rates
- **LLM Integration**: Natural language parsing for prosumer configurations
- **Performance Optimization**: 1000 prosumers/5 seconds, <1ms per timestep
- **Test Coverage**: 22 comprehensive tests with 100% pass rate

### Module 3 Features (Available Now)
- **Multi-Agent Framework**: LangGraph-based negotiation workflow
- **Communication Protocols**: Strict Pydantic schema validation
- **Agent Personas**: Professional AggregatorAgent and ProsumerAgent prompts
- **Market Support**: Energy and ancillary services (SPIN, NONSPIN)
- **Coalition Formation**: Automatic resource aggregation and optimization

### Upcoming Features (Modules 4-6)
- **LLM-Powered Negotiation**: Strategic reasoning and advanced decision-making
- **Hybrid Optimization**: LLM-to-Solver integration for bid formulation
- **Performance Benchmarking**: Comparison against centralized optimization baselines
- **Interactive Dashboard**: Web-based visualization of negotiations and results
- **Real-time Simulation**: Complete market participation workflow

## Technical Specifications

### Data Specifications
- **Market**: CAISO (California Independent System Operator)
- **Time Period**: August 15-21, 2023 (7-day simulation)  
- **Resolution**: 15-minute intervals (672 data points)
- **Location**: Los Angeles, CA (34.05°N, -118.24°W)
- **Assets**: 20 residential households + solar generation

### Technology Stack
- **Backend**: Python 3.8+, pandas, numpy, pydantic
- **Data Sources**: GridStatus.io, NREL PVWatts API
- **Multi-Agent System**: LangGraph, LangChain, Google Gemini API
- **Visualization**: matplotlib, seaborn
- **Testing**: pytest with comprehensive validation suites

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

### Phase 2: Asset Modeling (Module 2) ✅
- [x] Physics-based BESS, EV, and Solar PV models
- [x] Realistic operational constraints and efficiency curves
- [x] Fleet generation with California adoption rates  
- [x] LLM-powered natural language configuration parsing
- [x] Comprehensive testing with 22 test cases
- [x] Performance optimization (1000 prosumers in 5 seconds)

### Phase 3: Multi-Agent Framework (Module 3) ✅
- [x] LangGraph-based agent system architecture
- [x] Pydantic communication schemas for all agent messages
- [x] Professional AggregatorAgent and ProsumerAgent personas
- [x] Multi-round negotiation workflow with coalition formation
- [x] Energy and ancillary services market support
- [x] Comprehensive testing and interactive demonstrations

### Phase 4: Core Logic & Optimization (Module 4) 🚧
**Objective**: Implement LLM-powered negotiation algorithms and hybrid optimization

**Key Components**:
- **LLM-Powered Reasoning**: Replace rule-based logic with strategic AI decision-making
- **Advanced Negotiation**: Game theory and multi-round strategic offers
- **Hybrid Optimization**: LLM-to-Solver integration for bid formulation
- **Dynamic Constraints**: Real-time asset state and preference handling

**Technical Approach**:
- Integration of Gemini API for agent reasoning
- CVXPY optimization with LLM-generated constraints
- Strategic negotiation algorithms
- Performance comparison with centralized baselines

**Deliverables**:
- LLM-powered agent reasoning system
- Hybrid optimization framework
- Advanced negotiation strategies
- Performance benchmarking results

### Phase 5: Simulation & Benchmarking (Module 5) 🚧
**Objective**: Complete simulation orchestration with performance comparison against centralized optimization

**Key Components**:
- **Simulation Engine**: Time-stepped market participation workflow
- **Baseline Comparison**: Centralized optimization for benchmarking
- **Performance Metrics**: Profit, prosumer satisfaction, reliability measures
- **Scenario Testing**: Various market conditions and fleet configurations

**Technical Approach**:
- Integration of all previous modules into unified simulation
- Centralized MILP/LP baseline implementation
- Statistical analysis and performance reporting
- Scalability testing with large prosumer fleets

**Deliverables**:
- Complete simulation orchestration system
- Centralized optimization baseline
- Performance comparison framework
- Comprehensive benchmarking results

### Phase 6: Visualization Dashboard (Module 6) 🚧
**Objective**: Interactive web interface for simulation results and agent negotiation visualization

**Key Components**:
- **Real-time Negotiation Visualization**: Live agent communication display
- **Performance Analytics**: Interactive charts and metrics dashboards
- **Scenario Configuration**: User-friendly simulation parameter controls
- **Results Export**: Data download and reporting capabilities

**Technical Approach**:
- Streamlit-based web application
- Real-time data streaming and visualization
- Interactive parameter controls and scenario management
- Professional reporting and data export features

**Deliverables**:
- Interactive web dashboard
- Real-time negotiation visualization
- Performance analytics interface
- User-friendly scenario configuration
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

## Module Usage

### Module 1: Data & Simulation Environment
```bash
cd module_1_data_simulation
python collect_data.py      # Data collection
python test_data.py         # Validation
python create_dashboard.py  # Visualization
```

### Module 2: Asset Modeling
```bash
cd module_2_asset_modeling
python fleet_generator.py   # Generate prosumer fleet
python llm_parser.py        # Test natural language parsing
python test_module2.py      # Run validation tests
python demo_module2.py      # Interactive demonstrations
```

### Module 3: Agentic Framework
```bash
cd module_3_agentic_framework
python demo_module3.py         # Run interactive demonstrations  
python test_module3.py         # Validate all components
python agent_framework.py      # Run basic negotiation test
```

## Development Roadmap

### Immediate Next Steps (Weeks 1-2)
1. **Begin Module 4 Development**
   - LLM-powered agent reasoning implementation
   - Hybrid optimization framework setup
   - Strategic negotiation algorithm design

2. **Enhanced Integration Testing**
   - Cross-module compatibility validation
   - Performance optimization and scaling tests

### Short-term Goals (Month 1)
1. **Complete Module 4: Core Logic & Optimization**
   - Full LLM integration with strategic reasoning
   - Hybrid LLM-to-Solver optimization working
   - Advanced multi-round negotiation protocols

2. **Begin Module 5: Simulation Orchestration**
   - Complete simulation workflow integration
   - Centralized optimization baseline implementation

### Medium-term Goals (Months 2-3)
1. **Complete Modules 5-6**
   - Full simulation orchestration with benchmarking
   - Interactive web dashboard with real-time visualization
   - Performance comparison against centralized optimization
   - Comprehensive testing and validation

2. **Research & Publication**
   - Performance analysis and results documentation
   - Academic paper preparation
   - Open-source release preparation

### Long-term Goals (Months 3-6)
1. **Advanced Features & Optimization**
   - Machine learning integration for strategy improvement
   - Predictive analytics for market opportunity identification
   - Advanced optimization algorithms and risk management
   - Real-world pilot deployment preparation

2. **Industry Integration**
   - Utility partnership development
   - Regulatory compliance enhancement
   - Commercial deployment feasibility study
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
1. **Choose a Module**: Pick from Modules 4-6 based on expertise
2. **Set Up Environment**: Use shared virtual environment (compatible across modules)
3. **Follow Standards**: Maintain code quality and documentation standards
4. **Integration Testing**: Ensure compatibility with completed modules 1-3

### For Researchers
1. **Algorithm Development**: Focus on novel optimization or learning algorithms for Module 4+
2. **Performance Analysis**: Comparative studies with traditional VPP methods
3. **Use Case Expansion**: Adapt existing framework to different markets or asset types
4. **Validation Studies**: Real-world testing and validation of agent-based approaches

### For Industry Partners
1. **Pilot Programs**: Test with actual DER portfolios using completed framework
2. **Market Integration**: Adapt agent-based system to specific utility requirements
3. **Regulatory Compliance**: Ensure adherence to local market rules and standards
4. **Commercial Deployment**: Scale proven agentic approach for production use

---

**Current Status**: Modules 1-3 Complete ✅ | Ready for Module 4 Development 🚀  
**Next Milestone**: Core Negotiation & Optimization Logic (Module 4)  
**Target Completion**: Full LLM-powered VPP Agent System within 3 months

## License

This project is for research and educational purposes. See individual module documentation for specific usage guidelines.

---

**Project Status**: Module 1 Complete ✅ | Modules 2-6 In Planning 🚧  
**Last Updated**: July 29, 2025  
**Contact**: See module documentation for specific questions
