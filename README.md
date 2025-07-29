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

## Research Goals

1. **Demonstrate Feasibility**: Prove agentic VPP model is technically viable
2. **Quantify Added Value**: Show benefits over traditional optimization
3. **Showcase LLM Capabilities**: Highlight unique AI advantages for VPP operations
4. **Enable Future Research**: Provide foundation for advanced VPP agent systems

## License

This project is for research and educational purposes. See individual module documentation for specific usage guidelines.

---

**Project Status**: Module 1 Complete ✅ | Modules 2-6 In Planning 🚧  
**Last Updated**: July 29, 2025  
**Contact**: See module documentation for specific questions
