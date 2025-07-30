# VPP LLM Agent - Comprehensive Visualization Dashboard (Module 6)

[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)]()
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)

## Overview

The VPP LLM Agent Dashboard is a comprehensive, interactive web application that provides:

- **🧪 Individual Module Testing**: Run and test each of the 5 VPP modules independently
- **📊 Advanced Data Visualization**: Interactive charts and real-time performance monitoring
- **🏠 Prosumer Fleet Management**: Create, manage, and analyze prosumer populations
- **📋 Comprehensive Logging**: Detailed execution logs and system monitoring
- **🤖 AI-Powered Insights**: Natural language analysis using Google Gemini
- **⚡ Real-time Performance Analysis**: Agentic vs Centralized model comparison

## Key Features

### 🧪 Module Testing Interface
- **Module 1**: Data collection and environment setup testing
- **Module 2**: Asset modeling and fleet generation with LLM parsing
- **Module 3**: Multi-agent framework and negotiation workflow testing
- **Module 4**: Core negotiation logic and optimization validation
- **Module 5**: Full simulation orchestration and benchmarking

### 🏠 Advanced Prosumer Management
- **Fleet Overview**: Real-time fleet characteristics and statistics
- **Natural Language Creation**: Create prosumers using LLM-powered parsing
- **Manual Configuration**: Detailed prosumer asset and preference setup
- **Fleet Analytics**: Comprehensive adoption rates and capacity analysis

### 📊 Enhanced Visualization
- **Performance Comparison**: Agentic vs Centralized model radar charts
- **Market Analysis**: CAISO price trends and opportunity identification
- **Negotiation Analytics**: Coalition formation and efficiency metrics
- **Real-time Monitoring**: Live system status and execution tracking

### 📋 Comprehensive Logging
- **Execution Logs**: Real-time system logs with filtering and search
- **Module Results**: Detailed test results and error tracking
- **Export Capabilities**: Download logs, fleet data, and test results
- **System Monitoring**: Performance metrics and success rate tracking

## Installation & Setup

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows
```

### Installation
```bash
# Clone the repository
git clone https://github.com/srmadani/VPP_LLM_Agent.git
cd VPP_LLM_Agent/module_6_visualization_dashboard

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (optional)
cp ../.env.example ../.env
# Edit .env with your API keys
```

### API Keys Configuration (Optional)
The dashboard works with fallback data if API keys are not provided:

```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here      # For AI analysis
NREL_API_KEY=your_nrel_api_key_here          # For solar data
GRIDSTATUS_API_KEY=your_gridstatus_key_here  # For market data
```

## Quick Start

### Launch Dashboard
```bash
# Method 1: Using launch script
./launch_dashboard.sh

# Method 2: Manual launch
streamlit run dashboard.py

# Method 3: Custom port
streamlit run dashboard.py --server.port 8502
```

### Access Dashboard
- **URL**: http://localhost:8501
- **Mobile**: Responsive design supported
- **Multiple Tabs**: Fully functional in multiple browser tabs

## Dashboard Sections

### 1. 🧪 Module Testing
Test each VPP module independently with configurable parameters:

- **Module 1**: Configure data collection dates and load profile count
- **Module 2**: Set fleet size and test LLM parser with custom descriptions
- **Module 3**: Adjust negotiation rounds and test agent framework
- **Module 4**: Configure test fleet size for negotiation logic validation
- **Module 5**: Full simulation with customizable fleet size and duration

### 2. 🏠 Prosumer Management
Comprehensive prosumer fleet management:

#### Fleet Overview
- Real-time fleet statistics and technology adoption rates
- Asset distribution charts (BESS, EV, Solar)
- Capacity analysis and prosumer characteristics

#### Add Prosumer
- **Natural Language**: "A tech-savvy homeowner with Tesla Powerwall and Model 3"
- **Manual Configuration**: Detailed asset and preference setup
- **Custom Prosumers**: Track and manage user-created prosumers

#### Fleet Analytics
- Technology adoption rates and risk tolerance distribution
- Total fleet capacity and average prosumer capacity
- Capacity distribution histograms

### 3. 📈 Performance Analysis
Advanced performance comparison and visualization:

- **Profit vs Satisfaction**: Trade-off analysis between models
- **Radar Charts**: Multi-dimensional performance comparison
- **Success Rates**: Coalition formation and negotiation efficiency
- **Detailed Metrics**: Comprehensive performance table with advantages

### 4. 💹 Market Analysis
CAISO market data analysis and opportunity identification:

- **Price Trends**: LMP, spinning, and non-spinning reserve prices
- **Market Opportunities**: High-value period identification
- **Statistical Analysis**: Price ranges, averages, and distributions
- **Best Hours**: Optimal times for VPP participation

### 5. 📋 Logs & Monitoring
Comprehensive system monitoring and logging:

- **Real-time Logs**: Filtered execution logs with search capabilities
- **Module Results**: Test results tracking and error analysis
- **System Status**: Module test status and data availability
- **Export Options**: Download logs, fleet data, and results

## Advanced Features

### 🤖 AI-Powered Analysis
- **Natural Language Insights**: Gemini-powered simulation analysis
- **Performance Recommendations**: Data-driven optimization suggestions
- **Strategic Implications**: Real-world deployment considerations

### 📊 Interactive Controls
- **Real-time Filtering**: Dynamic log filtering and search
- **Customizable Charts**: Adjustable chart heights and display options
- **Export Capabilities**: CSV, JSON, and markdown export options
- **Auto-refresh**: Real-time data updates and monitoring

### 🎨 Professional UI
- **Modern Design**: Clean, professional interface with consistent styling
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Status Indicators**: Visual system status and health monitoring
- **Error Handling**: Graceful error handling with detailed feedback

## Performance Specifications

### Dashboard Performance
- **Load Time**: < 5 seconds for full dashboard
- **Chart Rendering**: < 2 seconds per visualization
- **Memory Usage**: < 150MB for typical operations
- **Concurrent Users**: Supports multiple browser sessions

### System Capabilities
- **Fleet Testing**: Up to 200 prosumers in test configurations
- **Module Testing**: All 5 modules with comprehensive validation
- **Data Processing**: Real-time analysis of simulation results
- **Log Management**: Efficient log storage and retrieval

## User Guide

### Module Testing Workflow

1. **Start with Module 1**: Test data collection first
   ```
   Configuration: Set date range and number of load profiles
   Expected Result: Market data, solar data, and load profiles generated
   ```

2. **Test Module 2**: Validate asset modeling
   ```
   Configuration: Set fleet size and test LLM parser
   Expected Result: Diverse prosumer fleet with BESS, EV, and Solar assets
   ```

3. **Test Module 3**: Verify agent framework
   ```
   Configuration: Set negotiation rounds
   Expected Result: Multi-agent negotiation workflow completion
   ```

4. **Test Module 4**: Validate negotiation logic
   ```
   Configuration: Set test fleet size
   Expected Result: Coalition formation with satisfaction scores
   ```

5. **Run Module 5**: Execute full simulation
   ```
   Configuration: Fleet size, duration, opportunity frequency
   Expected Result: Complete performance comparison and benchmarking
   ```

### Prosumer Creation Guide

#### Natural Language Method
```
Input: "A tech-savvy homeowner with a 15kWh Tesla Powerwall, Model 3 EV that must be charged by 7 AM, and 8kW solar panels. Prefers backup power and has moderate risk tolerance."

Output: Structured prosumer configuration with:
- BESS: 15kWh Tesla Powerwall
- EV: Model 3 with 7 AM charging deadline
- Solar: 8kW system
- Preferences: Backup power priority, moderate risk
```

#### Manual Configuration Method
```
Step 1: Basic Information
- Prosumer ID
- Backup power hours
- Minimum compensation rate
- Participation willingness

Step 2: Asset Configuration
- Battery: Capacity, power rating, current SOC
- EV: Battery size, charge power, departure time
- Solar: System capacity

Step 3: Preferences
- Risk tolerance level
- Maximum discharge percentage
```

### Performance Analysis Interpretation

#### Key Metrics Explained
- **Satisfaction Advantage**: Higher values indicate better prosumer preference handling
- **Coalition Size**: Larger coalitions indicate better coordination
- **Success Rate**: Percentage of successful negotiations
- **Negotiation Time**: Efficiency of the negotiation process

#### Trade-off Analysis
- **Agentic Model**: Higher satisfaction, respects preferences, realistic deployment
- **Centralized Model**: Higher theoretical profit, ignores preferences, deployment challenges

## Troubleshooting

### Common Issues

1. **Dashboard won't start**
   ```bash
   # Check Python version
   python --version  # Should be 3.8+
   
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   
   # Check port availability
   lsof -i :8501  # Kill any existing Streamlit processes
   ```

2. **Module imports failing**
   ```bash
   # Check file paths
   ls ../module_*/
   
   # Verify all modules are present
   find .. -name "*.py" -path "*/module_*" | head -10
   ```

3. **No data displayed**
   ```bash
   # Run Module 1 test to generate data
   # Check data directory exists
   ls ../module_1_data_simulation/data/
   
   # Verify CSV files are present
   ls ../module_1_data_simulation/data/*.csv
   ```

4. **API features not working**
   ```bash
   # Check .env file exists and has correct keys
   cat ../.env
   
   # Test API connectivity (if applicable)
   curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1/models
   ```

### Performance Optimization

1. **Large Fleet Sizes**: For fleets >100 prosumers, consider reducing visualization complexity
2. **Memory Usage**: Clear module results regularly using sidebar controls
3. **Log Management**: Use log filtering to reduce display overhead
4. **Browser Performance**: Close unused tabs and clear browser cache periodically

### Error Handling

The dashboard includes comprehensive error handling:
- **Module Import Errors**: Graceful fallbacks with user-friendly messages
- **Data Loading Errors**: Clear indication of missing data with recovery suggestions
- **API Errors**: Fallback functionality when external services are unavailable
- **Configuration Errors**: Detailed error messages with suggested fixes

## Development & Customization

### Adding New Visualizations
```python
def render_custom_analysis(self):
    """Add custom analysis section."""
    st.header("📊 Custom Analysis")
    
    # Your custom visualization code
    fig = px.scatter(self.data, x='timestamp', y='metric')
    st.plotly_chart(fig, use_container_width=True)
```

### Custom Module Testing
```python
def run_custom_module(self, **kwargs):
    """Add custom module testing."""
    try:
        # Your module testing logic
        result = custom_test_function(**kwargs)
        return {
            'status': 'success', 
            'message': 'Custom test completed',
            'data': result
        }
    except Exception as e:
        return {
            'status': 'error', 
            'message': str(e),
            'traceback': traceback.format_exc()
        }
```

### Extending Prosumer Management
```python
def add_custom_prosumer_type(self):
    """Add support for new prosumer asset types."""
    # Custom asset configuration UI
    has_heat_pump = st.checkbox("Has Heat Pump")
    if has_heat_pump:
        heat_pump_capacity = st.number_input("Heat Pump Capacity (kW)")
        # Add to prosumer configuration
```

### Custom Styling
```python
# Add custom CSS in setup_page_config()
st.markdown("""
<style>
.custom-metric {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #1f77b4;
}
</style>
""", unsafe_allow_html=True)
```

## API Reference

### Dashboard Class Methods

#### Core Rendering Methods
- `render_header()`: Main dashboard header with key metrics
- `render_sidebar()`: Control panel and system status
- `render_module_testing_panel()`: Module testing interface
- `render_prosumer_management()`: Fleet management interface
- `render_performance_comparison()`: Performance analysis charts
- `render_market_analysis()`: Market data visualization
- `render_comprehensive_logs()`: Logging and monitoring interface

#### Module Runner Methods
- `run_module_1(**kwargs)`: Data collection testing
- `run_module_2(**kwargs)`: Asset modeling testing
- `run_module_3(**kwargs)`: Agent framework testing
- `run_module_4(**kwargs)`: Negotiation logic testing
- `run_module_5(**kwargs)`: Full simulation testing

#### Utility Methods
- `load_data()`: Load all required data files
- `setup_gemini()`: Configure AI analysis capabilities
- `parse_prosumer_description()`: LLM-powered prosumer parsing
- `simple_description_parser()`: Fallback prosumer parsing

### Configuration Parameters

#### Module Testing Parameters
```python
# Module 1 parameters
{
    'start_date': '2023-08-01',
    'end_date': '2023-08-31',
    'num_profiles': 50
}

# Module 2 parameters
{
    'fleet_size': 20,
    'test_description': 'Prosumer description text'
}

# Module 5 parameters
{
    'fleet_size': 20,
    'duration_hours': 24,
    'opportunity_frequency': 1.0
}
```

#### Dashboard Configuration
```python
# Display options
{
    'show_detailed_metrics': True,
    'show_logs': True,
    'chart_height': 400,
    'log_level': 'INFO'
}
```

## Integration Points

### Data Sources
- **Module 1**: Market data, solar data, load profiles
- **Module 2**: Prosumer fleet configurations and asset models
- **Module 3**: Agent framework results and negotiation workflows
- **Module 4**: Negotiation results and optimization outcomes
- **Module 5**: Complete simulation results and performance metrics

### External APIs
- **Google Gemini**: AI-powered analysis and natural language processing
- **NREL API**: Solar data collection (optional)
- **GridStatus API**: Market data collection (optional)

### Export Formats
- **CSV**: Raw data exports for analysis
- **JSON**: Structured data and configurations
- **Logs**: Text-based execution logs
- **Charts**: PNG exports of visualizations

## Security Considerations

### API Key Management
- Environment variables for sensitive credentials
- Fallback functionality when APIs are unavailable
- No hardcoded credentials in source code

### Data Privacy
- Local data processing and storage
- No external data transmission without explicit API calls
- User-generated prosumer data remains local

### Network Security
- Local hosting by default (localhost:8501)
- HTTPS support when deployed to production
- Configurable firewall and access controls

## Deployment Options

### Local Development
```bash
# Standard local development
streamlit run dashboard.py
```

### Production Deployment
```bash
# Docker deployment
docker build -t vpp-dashboard .
docker run -p 8501:8501 vpp-dashboard

# Cloud deployment (example with Streamlit Cloud)
# Push to GitHub and connect to Streamlit Cloud
```

### Enterprise Deployment
- **Load Balancing**: Multiple dashboard instances
- **Authentication**: Integration with enterprise SSO
- **Monitoring**: Application performance monitoring
- **Backup**: Regular data backup and recovery procedures

## Support & Documentation

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive inline documentation
- **Examples**: Working examples throughout the interface
- **Community**: User community and discussion forums

### Contributing
- **Fork Repository**: Create feature branches for contributions
- **Testing**: Include tests for all new functionality
- **Documentation**: Update README and inline documentation
- **Code Review**: All contributions reviewed before merging

### Roadmap
- **Real-time Simulation**: Live simulation monitoring
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: Native mobile application
- **API Integration**: RESTful API for external systems

## License

MIT License - see LICENSE file for details.

---

**🚀 Ready to explore the future of Virtual Power Plant operations with comprehensive AI-driven analysis and testing!**

*Built with ❤️ using Streamlit, Plotly, and Google Gemini API*
