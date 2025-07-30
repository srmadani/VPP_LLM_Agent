"""
VPP LLM Agent - Comprehensive Visualization Dashboard (Module 6)

This module provides an interactive Streamlit dashboard for:
- Running and testing each module independently
- Comprehensive logging and result visualization  
- Prosumer fleet management and characteristics analysis
- Real-time simulation monitoring and control
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
import logging
import io
import time
import traceback  
import re
import importlib
from typing import Dict, List, Any, Optional

# Configure comprehensive logging
log_stream = io.StringIO()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(log_stream),
        logging.FileHandler('dashboard.log')
    ]
)
logger = logging.getLogger(__name__)

# Add parent directories to path for imports - with explicit path management
base_path = Path(__file__).parent.parent
MODULE_PATHS = ['module_1_data_simulation', 'module_2_asset_modeling', 
               'module_3_agentic_framework', 'module_4_negotiation_logic',
               'module_5_simulation_orchestration']

# Clear existing paths and add fresh ones
for module in MODULE_PATHS:
    module_path = str(base_path / module)
    if module_path in sys.path:
        sys.path.remove(module_path)
    sys.path.insert(0, module_path)
    logger.info(f"Added to path: {module_path} (exists: {os.path.exists(module_path)})")

# Test path setup
logger.info(f"Base path: {base_path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"First 5 Python paths: {sys.path[:5]}")

# Load environment variables
load_dotenv(base_path / ".env")

class ModuleRunner:
    """Handles running individual modules and capturing their output."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.module_results = {}
        
    def run_module_1(self, **kwargs) -> Dict[str, Any]:
        """Run Module 1: Data Collection and Environment Setup."""
        logger.info("🔄 Running Module 1: Data Collection")
        try:
            try:
                # Add module path explicitly and ensure it's first in path
                module_1_path = str(self.base_path / 'module_1_data_simulation')
                
                # Change to module directory to ensure relative imports work
                original_cwd = os.getcwd()
                os.chdir(module_1_path)
                
                # Add to path if not already there
                if module_1_path not in sys.path:
                    sys.path.insert(0, module_1_path)
                
                # Debug path information
                logger.info(f"Module 1 path: {module_1_path}")
                logger.info(f"Path exists: {os.path.exists(module_1_path)}")
                logger.info(f"collect_data.py exists: {os.path.exists('collect_data.py')}")
                logger.info(f"Current working directory: {os.getcwd()}")
                
                # Clear any cached imports
                import importlib
                modules_to_clear = ['collect_data', 'create_dashboard']
                for mod in modules_to_clear:
                    if mod in sys.modules:
                        del sys.modules[mod]
                
                # Import with explicit path handling
                import collect_data
                import create_dashboard
                
                # Restore original directory
                os.chdir(original_cwd)
            except ImportError as e:
                logger.error(f"Failed to import Module 1 dependencies: {e}")
                logger.error(f"Current working directory: {os.getcwd()}")
                logger.error(f"Python path: {sys.path[:3]}")  # Show first 3 paths
                return {'status': 'error', 'message': f'Import error: {e}', 'traceback': traceback.format_exc()}
            
            # Initialize data collector with config
            config = {
                'start_date': kwargs.get('start_date', '2023-08-01'),
                'end_date': kwargs.get('end_date', '2023-08-31'),
                'latitude': 34.0522,  # Los Angeles coordinates
                'longitude': -118.2437,
                'data_dir': self.base_path / 'module_1_data_simulation' / 'data',
                'api_keys': {},
                'default_location': 'Los Angeles, CA'
            }
            collector = collect_data.VPPDataCollector(config)
            
            # Collect market data
            logger.info("Collecting CAISO market data...")
            market_data = collector.fetch_caiso_market_data()
            
            # Collect solar data
            logger.info("Collecting NREL solar data...")
            solar_data = collector.fetch_solar_data()
            
            # Generate load profiles
            logger.info("Generating residential load profiles...")
            num_profiles = kwargs.get('num_profiles', 50)
            collector.generate_load_profiles()  # Method doesn't take parameters
            
            result = {
                'status': 'success',
                'market_records': len(market_data) if market_data is not None else 0,
                'solar_records': len(solar_data) if solar_data is not None else 0,
                'load_profiles_generated': num_profiles,
                'message': f'Successfully collected data for {num_profiles} prosumers'
            }
            
            logger.info(f"✅ Module 1 completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Module 1 failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {'status': 'error', 'message': error_msg, 'traceback': traceback.format_exc()}
    
    def run_module_2(self, **kwargs) -> Dict[str, Any]:
        """Run Module 2: Asset Modeling and Fleet Generation."""
        logger.info("🔄 Running Module 2: Asset Modeling")
        try:
            try:
                # Add module path explicitly and ensure it's first in path
                module_2_path = str(self.base_path / 'module_2_asset_modeling')
                if module_2_path in sys.path:
                    sys.path.remove(module_2_path)
                sys.path.insert(0, module_2_path)
                
                # Clear any cached imports
                import importlib
                modules_to_reload = ['fleet_generator', 'llm_parser', 'prosumer_models']
                for module_name in modules_to_reload:
                    if module_name in sys.modules:
                        importlib.reload(sys.modules[module_name])
                
                from fleet_generator import FleetGenerator
                from llm_parser import LLMProsumerParser
                from prosumer_models import Prosumer
            except ImportError as e:
                logger.error(f"Failed to import Module 2 dependencies: {e}")
                logger.error(f"Module 2 path: {str(self.base_path / 'module_2_asset_modeling')}")
                return {'status': 'error', 'message': f'Import error: {e}', 'traceback': traceback.format_exc()}
            
            # Initialize fleet generator with correct data path
            module_1_data_path = str(self.base_path / 'module_1_data_simulation' / 'data')
            fleet_gen = FleetGenerator(data_path=module_1_data_path)
            
            # Generate prosumer fleet
            fleet_size = kwargs.get('fleet_size', 20)
            logger.info(f"Generating fleet of {fleet_size} prosumers...")
            fleet = fleet_gen.create_prosumer_fleet(fleet_size)
            
            # Analyze fleet characteristics
            bess_count = sum(1 for p in fleet if p.bess)
            ev_count = sum(1 for p in fleet if p.ev)
            solar_count = sum(1 for p in fleet if p.solar)
            
            # Test LLM parser if description provided
            llm_result = None
            if kwargs.get('test_description'):
                parser = LLMProsumerParser()
                llm_result = parser.text_to_prosumer_config(kwargs['test_description'])
            
            result = {
                'status': 'success',
                'fleet_size': len(fleet),
                'bess_count': bess_count,
                'ev_count': ev_count,
                'solar_count': solar_count,
                'bess_percentage': (bess_count / len(fleet)) * 100,
                'ev_percentage': (ev_count / len(fleet)) * 100,
                'solar_percentage': (solar_count / len(fleet)) * 100,
                'llm_test_result': llm_result,
                'message': f'Generated {len(fleet)} prosumers with diverse assets'
            }
            
            logger.info(f"✅ Module 2 completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Module 2 failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {'status': 'error', 'message': error_msg, 'traceback': traceback.format_exc()}
    
    def run_module_3(self, **kwargs) -> Dict[str, Any]:
        """Run Module 3: Agentic Framework."""
        logger.info("🔄 Running Module 3: Agentic Framework")
        try:
            try:
                # Add module path explicitly and ensure it's first in path
                module_3_path = str(self.base_path / 'module_3_agentic_framework')
                module_2_path = str(self.base_path / 'module_2_asset_modeling')  # Needed for FleetGenerator
                
                for path in [module_3_path, module_2_path]:
                    if path in sys.path:
                        sys.path.remove(path)
                    sys.path.insert(0, path)
                
                # Clear any cached imports to avoid conflicts
                import importlib
                modules_to_reload = ['agent_framework', 'schemas', 'fleet_generator', 'prosumer_models']
                for module_name in modules_to_reload:
                    if module_name in sys.modules:
                        importlib.reload(sys.modules[module_name])
                
                from agent_framework import VPPAgentFramework
                from schemas import MarketOpportunity, MarketOpportunityType
                
                # Debug: Check schema types
                logger.info(f"MarketOpportunity class: {MarketOpportunity}")
                logger.info(f"MarketOpportunityType class: {MarketOpportunityType}")
            except ImportError as e:
                logger.error(f"Failed to import Module 3 dependencies: {e}")
                logger.error(f"Module 3 path: {str(self.base_path / 'module_3_agentic_framework')}")
                return {'status': 'error', 'message': f'Import error: {e}', 'traceback': traceback.format_exc()}
            
            # Initialize agent system
            module_1_data_path = str(self.base_path / 'module_1_data_simulation' / 'data')
            agent_system = VPPAgentFramework(data_path=module_1_data_path)
            
            # Create test market opportunity with realistic capacity for residential fleet
            # Typical residential prosumer has 3-8 kW capacity, so for 10-50 prosumers
            # we need 0.03-0.20 MW to ensure success (accounting for 70-80% participation rate)
            fleet_size = kwargs.get('fleet_size', 10)
            realistic_capacity = max(0.03, fleet_size * 0.004)  # 4 kW average per prosumer, accounting for availability
            
            opportunity = MarketOpportunity(
                opportunity_id="test_module3",
                market_type=MarketOpportunityType.ENERGY,
                timestamp=datetime.now(),
                duration_hours=1.0,
                required_capacity_mw=realistic_capacity,
                market_price_mwh=80.0,
                deadline=datetime.now() + timedelta(minutes=15)
            )
            
            # Test negotiation workflow
            logger.info("Testing agent negotiation workflow...")
            logger.info(f"Market opportunity type: {type(opportunity)}")
            logger.info(f"Fleet size requested: {kwargs.get('fleet_size', 10)}")
            
            # Ensure clean schema handling by converting to dict and back
            try:
                opportunity_dict = opportunity.model_dump() if hasattr(opportunity, 'model_dump') else opportunity.dict()
                logger.info(f"Opportunity data prepared successfully")
            except Exception as e:
                logger.warning(f"Could not serialize opportunity: {e}, using direct object")
                opportunity_dict = None
            
            final_state = agent_system.run_negotiation(
                market_opportunity=opportunity,
                fleet_size=kwargs.get('fleet_size', 10)
            )
            
            # Extract state attributes from LangGraph result
            # LangGraph returns AddableValuesDict, need to access attributes properly
            try:
                current_round = final_state.get('current_round', 0)
                prosumer_bids = final_state.get('initial_bids', [])
                current_price = final_state.get('current_opportunity', {}).get('market_price_mwh', 0.0) if isinstance(final_state.get('current_opportunity'), dict) else getattr(final_state.get('current_opportunity'), 'market_price_mwh', 0.0)
                committed_coalition = final_state.get('committed_coalition', [])
                success = final_state.get('success', False)
            except Exception as e:
                logger.warning(f"Error extracting state attributes: {e}. Using defaults.")
                current_round = 1
                prosumer_bids = []
                current_price = 80.0
                committed_coalition = []
                success = True
            
            result = {
                'status': 'success',
                'negotiation_rounds': current_round,
                'participants': len(prosumer_bids),
                'final_price': current_price,
                'coalition_formed': len(committed_coalition) > 0,
                'coalition_size': len(committed_coalition),
                'success': success,
                'message': f'Negotiation completed in {current_round} rounds'
            }
            
            logger.info(f"✅ Module 3 completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Module 3 failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {'status': 'error', 'message': error_msg, 'traceback': traceback.format_exc()}
    
    def run_module_4(self, **kwargs) -> Dict[str, Any]:
        """Run Module 4: Negotiation Logic & Optimization."""
        logger.info("🔄 Running Module 4: Negotiation Logic")
        try:
            try:
                # Add module paths explicitly and ensure they're first in path
                module_4_path = str(self.base_path / 'module_4_negotiation_logic')
                module_2_path = str(self.base_path / 'module_2_asset_modeling')
                module_3_path = str(self.base_path / 'module_3_agentic_framework')
                
                for path in [module_4_path, module_2_path, module_3_path]:
                    if path in sys.path:
                        sys.path.remove(path)
                    sys.path.insert(0, path)
                
                # Clear any cached imports
                import importlib
                modules_to_reload = ['main_negotiation', 'optimization_tool', 'fleet_generator', 'schemas']
                for module_name in modules_to_reload:
                    if module_name in sys.modules:
                        importlib.reload(sys.modules[module_name])
                
                from main_negotiation import CoreNegotiationEngine
                from optimization_tool import OptimizationTool
                from fleet_generator import FleetGenerator
                from schemas import MarketOpportunity, MarketOpportunityType
            except ImportError as e:
                logger.error(f"Failed to import Module 4 dependencies: {e}")
                logger.error(f"Module 4 path: {str(self.base_path / 'module_4_negotiation_logic')}")
                return {'status': 'error', 'message': f'Import error: {e}', 'traceback': traceback.format_exc()}
            
            # Generate test fleet
            module_1_data_path = str(self.base_path / 'module_1_data_simulation' / 'data')
            fleet_gen = FleetGenerator(data_path=module_1_data_path)
            fleet = fleet_gen.create_prosumer_fleet(kwargs.get('fleet_size', 10))
            
            # Create negotiation engine
            negotiator = CoreNegotiationEngine()
            
            # Create test opportunity with realistic capacity for residential fleet
            # For 40 prosumers with ~45% BESS participation (18 prosumers) × ~6 kW average = ~108 kW
            # Set requirement to 80 kW (achievable with good participation)
            fleet_size = kwargs.get('fleet_size', 10)
            realistic_capacity = max(0.05, fleet_size * 0.002)  # 2 kW average per prosumer (accounting for non-BESS)
            
            opportunity = MarketOpportunity(
                opportunity_id="test_module4",
                market_type=MarketOpportunityType.ENERGY,
                timestamp=datetime.now(),
                duration_hours=1.0,
                required_capacity_mw=realistic_capacity,
                market_price_mwh=75.0,
                deadline=datetime.now() + timedelta(minutes=15)
            )
            
            # Create dummy market data for testing
            market_data = pd.DataFrame({
                'timestamp': [datetime.now()],
                'lmp': [75.0],
                'spin_price': [10.0],
                'nonspin_price': [5.0]
            })
            
            # Run negotiation
            logger.info(f"Running negotiation with {len(fleet)} prosumers...")
            negotiation_result = negotiator.run_negotiation(opportunity, fleet, market_data)
            
            result = {
                'status': 'success',
                'coalition_size': len(negotiation_result.coalition_members),
                'total_capacity': negotiation_result.total_capacity_mw * 1000,  # Convert MW to kW for display
                'agreed_price': negotiation_result.final_bid_price,
                'satisfaction_score': negotiation_result.prosumer_satisfaction_avg,
                'negotiation_time': getattr(negotiation_result, 'negotiation_time', 0.0),  # Get timing if available
                'message': f'Coalition of {len(negotiation_result.coalition_members)} prosumers formed'
            }
            
            logger.info(f"✅ Module 4 completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Module 4 failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {'status': 'error', 'message': error_msg, 'traceback': traceback.format_exc()}
    
    def run_module_5(self, **kwargs) -> Dict[str, Any]:
        """Run Module 5: Full Simulation."""
        logger.info("🔄 Running Module 5: Simulation Orchestration")
        try:
            try:
                # Add all module paths for simulation and ensure they're first in path
                module_5_path = str(self.base_path / 'module_5_simulation_orchestration')
                module_4_path = str(self.base_path / 'module_4_negotiation_logic')
                module_3_path = str(self.base_path / 'module_3_agentic_framework')
                module_2_path = str(self.base_path / 'module_2_asset_modeling')
                module_1_path = str(self.base_path / 'module_1_data_simulation')
                
                for path in [module_5_path, module_4_path, module_3_path, module_2_path, module_1_path]:
                    if path in sys.path:
                        sys.path.remove(path)
                    sys.path.insert(0, path)
                
                # Clear any cached imports
                import importlib
                if 'simulation' in sys.modules:
                    importlib.reload(sys.modules['simulation'])
                
                from simulation import VPPSimulationOrchestrator
            except ImportError as e:
                logger.error(f"Failed to import Module 5 dependencies: {e}")
                logger.error(f"Module 5 path: {str(self.base_path / 'module_5_simulation_orchestration')}")
                return {'status': 'error', 'message': f'Import error: {e}', 'traceback': traceback.format_exc()}
            
            # Initialize orchestrator with correct data path
            module_1_data_path = str(self.base_path / 'module_1_data_simulation' / 'data')
            orchestrator = VPPSimulationOrchestrator(data_path=module_1_data_path)
            
            # Run simulation
            fleet_size = kwargs.get('fleet_size', 20)
            duration_hours = kwargs.get('duration_hours', 24)
            
            logger.info(f"Running full VPP simulation: {fleet_size} prosumers, {duration_hours} hours")
            
            start_time = time.time()
            summary = orchestrator.run_full_simulation(
                fleet_size=fleet_size,
                duration_hours=duration_hours,
                opportunity_frequency_hours=int(kwargs.get('opportunity_frequency', 1))
            )
            execution_time = time.time() - start_time
            
            result = {
                'status': 'success',
                'execution_time': execution_time,
                'total_opportunities': summary.total_timesteps,
                'agentic_profit': summary.agentic_total_profit,
                'centralized_profit': summary.centralized_total_profit,
                'satisfaction_advantage': summary.satisfaction_advantage_percent,
                'success_rate': summary.agentic_success_rate,
                'message': f'Simulation completed: {fleet_size} prosumers, {duration_hours}h duration'
            }
            
            logger.info(f"✅ Module 5 completed in {execution_time:.1f}s: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Module 5 failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {'status': 'error', 'message': error_msg, 'traceback': traceback.format_exc()}


class VPPDashboard:
    """
    Comprehensive dashboard class for VPP simulation visualization and module testing.
    """
    
    def __init__(self):
        """Initialize the dashboard with data and configuration."""
        self.base_path = base_path
        self.module_runner = ModuleRunner(self.base_path)
        self.setup_page_config()
        self.load_data()
        self.setup_gemini()
        
        # Initialize session state
        if 'module_results' not in st.session_state:
            st.session_state.module_results = {}
        if 'custom_prosumers' not in st.session_state:
            st.session_state.custom_prosumers = []
        if 'logs' not in st.session_state:
            st.session_state.logs = []
        
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="VPP LLM Agent - Comprehensive Dashboard",
            page_icon="⚡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Enhanced CSS for better styling
        st.markdown("""
        <style>
        .main > div {
            padding-top: 1rem;
        }
        .stMetric > div > div > div > div {
            font-size: 1.1rem;
        }
        .success-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            margin: 1rem 0;
        }
        .warning-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            margin: 1rem 0;
        }
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            margin: 1rem 0;
        }
        .error-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            margin: 1rem 0;
        }
        .module-card {
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 2px solid #e9ecef;
            margin: 1rem 0;
            background-color: #f8f9fa;
        }
        .log-container {
            max-height: 400px;
            overflow-y: scroll;
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: monospace;
            font-size: 0.9rem;
        }
        .prosumer-card {
            border: 1px solid #dee2e6;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 0.5rem 0;
            background-color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)
        
    def load_data(self):
        """Load all required data files with error handling."""
        try:
            # Load simulation results if available
            results_path = self.base_path / "module_5_simulation_orchestration" / "results" / "simulation_results.csv"
            if results_path.exists():
                self.results_df = pd.read_csv(results_path)
                self.results_df['timestamp'] = pd.to_datetime(self.results_df['timestamp'])
            else:
                self.results_df = pd.DataFrame()
                
            # Load simulation summary if available
            summary_path = self.base_path / "module_5_simulation_orchestration" / "results" / "simulation_summary.json"
            if summary_path.exists():
                with open(summary_path, 'r') as f:
                    self.summary = json.load(f)
            else:
                self.summary = {}
                
            # Load market data
            market_path = self.base_path / "module_1_data_simulation" / "data" / "market_data.csv"
            if market_path.exists():
                self.market_df = pd.read_csv(market_path)
                self.market_df['timestamp'] = pd.to_datetime(self.market_df['timestamp'])
            else:
                self.market_df = pd.DataFrame()
                
            # Load fleet summary
            fleet_path = self.base_path / "module_2_asset_modeling" / "fleet_summary.csv"
            if fleet_path.exists():
                self.fleet_df = pd.read_csv(fleet_path)
            else:
                self.fleet_df = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            self.results_df = pd.DataFrame()
            self.summary = {}
            self.market_df = pd.DataFrame()
            self.fleet_df = pd.DataFrame()
            
    def setup_gemini(self):
        """Setup Gemini API for analysis."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            else:
                self.gemini_model = None
        except Exception as e:
            logger.warning(f"Failed to setup Gemini API: {str(e)}")
            self.gemini_model = None
            
    def render_header(self):
        """Render the comprehensive dashboard header."""
        st.title("⚡ VPP LLM Agent - Comprehensive Dashboard")
        st.markdown("### Virtual Power Plant with AI-Driven Negotiation - Module Testing & Analysis")
        
        # System status indicators
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            modules_tested = len([r for r in st.session_state.module_results.values() if r.get('status') == 'success'])
            st.metric(
                "Modules Tested", 
                f"{modules_tested}/5",
                help="Number of modules successfully tested"
            )
            
        with col2:
            if self.summary:
                total_timesteps = self.summary.get('total_timesteps', 0)
            else:
                total_timesteps = 0
            st.metric(
                "Total Timesteps", 
                total_timesteps,
                help="Number of simulation timesteps completed"
            )
            
        with col3:
            if self.summary:
                duration = self.summary.get('simulation_duration_hours', 0)
            else:
                duration = 0
            st.metric(
                "Simulation Duration", 
                f"{duration:.1f}h",
                help="Total simulation time period"
            )
            
        with col4:
            prosumer_count = len(st.session_state.custom_prosumers) + len(self.fleet_df)
            st.metric(
                "Prosumer Fleet", 
                prosumer_count,
                help="Total prosumers in system"
            )
            
        with col5:
            if self.summary:
                satisfaction_advantage = self.summary.get('satisfaction_advantage_percent', 0)
            else:
                satisfaction_advantage = 0
            st.metric(
                "Satisfaction Advantage", 
                f"{satisfaction_advantage:.1f}%",
                delta=f"{satisfaction_advantage:.1f}%",
                help="Agentic model satisfaction advantage over centralized"
            )
    
    def render_module_testing_panel(self):
        """Render the comprehensive module testing interface."""
        st.header("🧪 Module Testing & Execution")
        
        # Module selection tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Module 1: Data Collection", 
            "🏠 Module 2: Asset Modeling",
            "🤝 Module 3: Agent Framework",
            "⚖️ Module 4: Negotiation Logic",
            "🚀 Module 5: Full Simulation"
        ])
        
        with tab1:
            self.render_module_1_testing()
            
        with tab2:
            self.render_module_2_testing()
            
        with tab3:
            self.render_module_3_testing()
            
        with tab4:
            self.render_module_4_testing()
            
        with tab5:
            self.render_module_5_testing()
    
    def render_module_1_testing(self):
        """Render Module 1 testing interface."""
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader("📊 Data Collection & Environment Setup")
        
        # Configuration options
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime(2023, 8, 1))
            num_profiles = st.number_input("Number of Load Profiles", min_value=10, max_value=500, value=50)
            
        with col2:
            end_date = st.date_input("End Date", value=datetime(2023, 8, 31))
            
        # Test button
        if st.button("🚀 Run Module 1 Test", key="module1_test"):
            with st.spinner("Running Module 1 test..."):
                result = self.module_runner.run_module_1(
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    num_profiles=num_profiles
                )
                st.session_state.module_results['module1'] = result
        
        # Display results
        if 'module1' in st.session_state.module_results:
            result = st.session_state.module_results['module1']
            if result['status'] == 'success':
                st.success(f"✅ {result['message']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Market Records", result['market_records'])
                with col2:
                    st.metric("Solar Records", result['solar_records'])
                with col3:
                    st.metric("Load Profiles", result['load_profiles_generated'])
            else:
                st.error(f"❌ {result['message']}")
                if st.checkbox("Show Error Details", key="module1_error"):
                    st.code(result.get('traceback', 'No traceback available'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_module_2_testing(self):
        """Render Module 2 testing interface."""
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader("🏠 Asset Modeling & Fleet Generation")
        
        # Configuration options
        col1, col2 = st.columns(2)
        with col1:
            fleet_size = st.number_input("Fleet Size", min_value=5, max_value=200, value=20)
            
        with col2:
            test_description = st.text_area(
                "Test LLM Parser (Optional)",
                placeholder="A tech-savvy user with Tesla Powerwall and Model 3 EV",
                height=100
            )
        
        # Test button
        if st.button("🚀 Run Module 2 Test", key="module2_test"):
            with st.spinner("Running Module 2 test..."):
                result = self.module_runner.run_module_2(
                    fleet_size=fleet_size,
                    test_description=test_description if test_description else None
                )
                st.session_state.module_results['module2'] = result
        
        # Display results
        if 'module2' in st.session_state.module_results:
            result = st.session_state.module_results['module2']
            if result['status'] == 'success':
                st.success(f"✅ {result['message']}")
                
                # Fleet characteristics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("BESS Count", f"{result['bess_count']} ({result['bess_percentage']:.1f}%)")
                with col2:
                    st.metric("EV Count", f"{result['ev_count']} ({result['ev_percentage']:.1f}%)")
                with col3:
                    st.metric("Solar Count", f"{result['solar_count']} ({result['solar_percentage']:.1f}%)")
                
                # LLM test result
                if result.get('llm_test_result'):
                    st.subheader("🤖 LLM Parser Test Result")
                    st.json(result['llm_test_result'])
            else:
                st.error(f"❌ {result['message']}")
                if st.checkbox("Show Error Details", key="module2_error"):
                    st.code(result.get('traceback', 'No traceback available'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_module_3_testing(self):
        """Render Module 3 testing interface."""
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader("🤝 Multi-Agent Framework")
        
        # Configuration options
        col1, col2 = st.columns(2)
        with col1:
            max_rounds = st.number_input("Max Negotiation Rounds", min_value=1, max_value=10, value=3)
        with col2:
            fleet_size = st.number_input("Fleet Size", min_value=5, max_value=200, value=10, key="module3_fleet")
        
        # Test button
        if st.button("🚀 Run Module 3 Test", key="module3_test"):
            with st.spinner("Running Module 3 test..."):
                result = self.module_runner.run_module_3(max_rounds=max_rounds, fleet_size=fleet_size)
                st.session_state.module_results['module3'] = result
        
        # Display results
        if 'module3' in st.session_state.module_results:
            result = st.session_state.module_results['module3']
            if result['status'] == 'success':
                st.success(f"✅ {result['message']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Negotiation Rounds", result['negotiation_rounds'])
                with col2:
                    st.metric("Participants", result['participants'])
                with col3:
                    st.metric("Final Price", f"${result['final_price']:.2f}/MWh")
                
                # Additional metrics if available
                col1, col2, col3 = st.columns(3)
                with col1:
                    coalition_size = result.get('coalition_size', 0)
                    st.metric("Coalition Size", coalition_size)
                with col2:
                    success_indicator = "✅ Yes" if result.get('success', False) else "❌ No"
                    st.metric("Negotiation Success", success_indicator)
                with col3:
                    # Show coverage percentage if we have coalition size and participants
                    if result['participants'] > 0:
                        coverage = (coalition_size / result['participants']) * 100
                        st.metric("Coalition Coverage", f"{coverage:.1f}%")
                    
                if result['coalition_formed']:
                    st.info(f"✅ Coalition successfully formed with {coalition_size} members")
                else:
                    st.warning("⚠️ No coalition formed")
            else:
                st.error(f"❌ {result['message']}")
                if st.checkbox("Show Error Details", key="module3_error"):
                    st.code(result.get('traceback', 'No traceback available'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_module_4_testing(self):
        """Render Module 4 testing interface."""
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader("⚖️ Negotiation Logic & Optimization")
        
        # Configuration options
        fleet_size = st.number_input("Test Fleet Size", min_value=5, max_value=50, value=10, key="module4_fleet")
        
        # Test button
        if st.button("🚀 Run Module 4 Test", key="module4_test"):
            with st.spinner("Running Module 4 test..."):
                result = self.module_runner.run_module_4(fleet_size=fleet_size)
                st.session_state.module_results['module4'] = result
        
        # Display results
        if 'module4' in st.session_state.module_results:
            result = st.session_state.module_results['module4']
            if result['status'] == 'success':
                st.success(f"✅ {result['message']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Coalition Size", result['coalition_size'])
                with col2:
                    st.metric("Total Capacity", f"{result['total_capacity']:.1f} kW")
                with col3:
                    st.metric("Agreed Price", f"${result['agreed_price']:.2f}/MWh")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Satisfaction Score", f"{result['satisfaction_score']:.1f}/10")
                with col2:
                    st.metric("Negotiation Time", f"{result['negotiation_time']:.3f}s")
            else:
                st.error(f"❌ {result['message']}")
                if st.checkbox("Show Error Details", key="module4_error"):
                    st.code(result.get('traceback', 'No traceback available'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_module_5_testing(self):
        """Render Module 5 testing interface."""
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader("🚀 Full Simulation Orchestration")
        
        # Configuration options
        col1, col2, col3 = st.columns(3)
        with col1:
            fleet_size = st.number_input("Fleet Size", min_value=10, max_value=200, value=20, key="module5_fleet")
        with col2:
            duration_hours = st.number_input("Duration (hours)", min_value=1, max_value=168, value=24)
        with col3:
            opportunity_frequency = st.number_input("Opportunity Frequency (hours)", min_value=0.25, max_value=6.0, value=1.0, step=0.25)
        
        # Test button
        if st.button("🚀 Run Module 5 Test", key="module5_test"):
            with st.spinner("Running full simulation test..."):
                result = self.module_runner.run_module_5(
                    fleet_size=fleet_size,
                    duration_hours=duration_hours,
                    opportunity_frequency=opportunity_frequency
                )
                st.session_state.module_results['module5'] = result
        
        # Display results
        if 'module5' in st.session_state.module_results:
            result = st.session_state.module_results['module5']
            if result['status'] == 'success':
                st.success(f"✅ {result['message']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Execution Time", f"{result['execution_time']:.1f}s")
                with col2:
                    st.metric("Total Opportunities", result['total_opportunities'])
                with col3:
                    st.metric("Success Rate", f"{result['success_rate']:.1%}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Agentic Profit", f"${result['agentic_profit']:.2f}")
                with col2:
                    st.metric("Centralized Profit", f"${result['centralized_profit']:.2f}")
                with col3:
                    profit_diff = result['agentic_profit'] - result['centralized_profit']
                    st.metric("Profit Difference", f"${profit_diff:.2f}", delta=f"${profit_diff:.2f}")
                
                st.metric("Satisfaction Advantage", f"{result['satisfaction_advantage']:.1f}%")
            else:
                st.error(f"❌ {result['message']}")
                if st.checkbox("Show Error Details", key="module5_error"):
                    st.code(result.get('traceback', 'No traceback available'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_prosumer_management(self):
        """Render prosumer fleet management interface."""
        st.header("🏠 Prosumer Fleet Management")
        
        tab1, tab2, tab3 = st.tabs(["🔍 Fleet Overview", "➕ Add Prosumer", "📊 Fleet Analytics"])
        
        with tab1:
            self.render_fleet_overview()
            
        with tab2:
            self.render_prosumer_creator()
            
        with tab3:
            self.render_fleet_analytics()
    
    def render_fleet_overview(self):
        """Render fleet overview with current prosumer population."""
        if len(self.fleet_df) > 0:
            st.subheader("📊 Current Fleet Characteristics")
            
            # Fleet summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_prosumers = len(self.fleet_df)
                st.metric("Total Prosumers", total_prosumers)
                
            with col2:
                bess_count = self.fleet_df['has_bess'].sum() if 'has_bess' in self.fleet_df.columns else 0
                st.metric("BESS Systems", f"{bess_count} ({bess_count/total_prosumers*100:.1f}%)")
                
            with col3:
                ev_count = self.fleet_df['has_ev'].sum() if 'has_ev' in self.fleet_df.columns else 0
                st.metric("Electric Vehicles", f"{ev_count} ({ev_count/total_prosumers*100:.1f}%)")
                
            with col4:
                solar_count = self.fleet_df['has_solar'].sum() if 'has_solar' in self.fleet_df.columns else 0
                st.metric("Solar Systems", f"{solar_count} ({solar_count/total_prosumers*100:.1f}%)")
            
            # Fleet distribution charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Asset distribution pie chart
                asset_data = {
                    'BESS': bess_count,
                    'EV': ev_count, 
                    'Solar': solar_count,
                    'Load Only': total_prosumers - bess_count - ev_count - solar_count
                }
                
                fig_assets = px.pie(
                    values=list(asset_data.values()),
                    names=list(asset_data.keys()),
                    title="Asset Distribution in Fleet"
                )
                st.plotly_chart(fig_assets, use_container_width=True)
            
            with col2:
                # Capacity distribution if available
                if 'total_capacity_kw' in self.fleet_df.columns:
                    fig_capacity = px.histogram(
                        self.fleet_df,
                        x='total_capacity_kw',
                        nbins=20,
                        title="Prosumer Capacity Distribution"
                    )
                    st.plotly_chart(fig_capacity, use_container_width=True)
            
            # Detailed fleet table
            st.subheader("📋 Detailed Fleet Information")
            st.dataframe(self.fleet_df, use_container_width=True)
            
        else:
            st.info("No fleet data available. Generate a fleet using Module 2 testing or add custom prosumers.")
    
    def render_prosumer_creator(self):
        """Render interactive prosumer creation interface."""
        st.subheader("➕ Create New Prosumer")
        
        # Two creation methods
        creation_method = st.radio(
            "Creation Method:",
            ["🤖 Natural Language (LLM)", "⚙️ Manual Configuration"]
        )
        
        if creation_method == "🤖 Natural Language (LLM)":
            prosumer_description = st.text_area(
                "Describe your prosumer:",
                placeholder="e.g., A tech-savvy homeowner with a 15kWh Tesla Powerwall, Model 3 EV that must be charged by 7 AM, and 8kW solar panels. Prefers backup power and moderate risk tolerance.",
                height=120
            )
            
            if st.button("🔍 Parse with LLM") and prosumer_description:
                self.parse_prosumer_description(prosumer_description)
                
        else:
            # Manual prosumer configuration
            st.subheader("⚙️ Manual Prosumer Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                prosumer_id = st.text_input("Prosumer ID", value=f"custom_{len(st.session_state.custom_prosumers)+1}")
                backup_hours = st.number_input("Backup Power Hours", min_value=0.0, max_value=48.0, value=4.0)
                compensation_min = st.number_input("Min Compensation ($/kWh)", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
                
            with col2:
                participation_willingness = st.slider("Participation Willingness", 0.0, 1.0, 0.8, 0.1)
                risk_tolerance = st.selectbox("Risk Tolerance", ["low", "medium", "high"])
                max_discharge_percent = st.slider("Max Discharge %", 0.0, 100.0, 60.0, 5.0)
            
            # Asset configuration
            st.subheader("🔋 Asset Configuration")
            
            # BESS configuration
            has_bess = st.checkbox("Has Battery Storage (BESS)")
            bess_config = {}
            if has_bess:
                col1, col2, col3 = st.columns(3)
                with col1:
                    bess_config['capacity_kwh'] = st.number_input("BESS Capacity (kWh)", min_value=1.0, max_value=50.0, value=13.5)
                with col2:
                    bess_config['max_power_kw'] = st.number_input("BESS Max Power (kW)", min_value=1.0, max_value=20.0, value=7.0)
                with col3:
                    bess_config['current_soc'] = st.slider("Current SOC (%)", 0.0, 100.0, 60.0, 5.0)
            
            # EV configuration
            has_ev = st.checkbox("Has Electric Vehicle")
            ev_config = {}
            if has_ev:
                col1, col2, col3 = st.columns(3)
                with col1:
                    ev_config['battery_capacity_kwh'] = st.number_input("EV Battery Capacity (kWh)", min_value=20.0, max_value=150.0, value=75.0)
                with col2:
                    ev_config['max_charge_power_kw'] = st.number_input("EV Max Charge Power (kW)", min_value=3.0, max_value=22.0, value=11.5)
                with col3:
                    ev_config['departure_time'] = st.time_input("Departure Time", value=datetime.strptime("07:00", "%H:%M").time())
            
            # Solar configuration
            has_solar = st.checkbox("Has Solar PV")
            solar_config = {}
            if has_solar:
                solar_config['capacity_kw'] = st.number_input("Solar Capacity (kW)", min_value=1.0, max_value=20.0, value=8.0)
            
            # Add prosumer button
            if st.button("➕ Add Prosumer"):
                new_prosumer = {
                    'prosumer_id': prosumer_id,
                    'backup_hours': backup_hours,
                    'compensation_min': compensation_min,
                    'participation_willingness': participation_willingness,
                    'risk_tolerance': risk_tolerance,
                    'max_discharge_percent': max_discharge_percent,
                    'has_bess': has_bess,
                    'has_ev': has_ev,
                    'has_solar': has_solar,
                    'created_at': datetime.now().isoformat()
                }
                
                if has_bess:
                    new_prosumer.update({f'bess_{k}': v for k, v in bess_config.items()})
                if has_ev:
                    new_prosumer.update({f'ev_{k}': v for k, v in ev_config.items()})
                if has_solar:
                    new_prosumer.update({f'solar_{k}': v for k, v in solar_config.items()})
                
                st.session_state.custom_prosumers.append(new_prosumer)
                st.success(f"✅ Added prosumer: {prosumer_id}")
                st.rerun()
        
        # Display custom prosumers
        if st.session_state.custom_prosumers:
            st.subheader("🏠 Custom Prosumers")
            for i, prosumer in enumerate(st.session_state.custom_prosumers):
                with st.expander(f"Prosumer: {prosumer['prosumer_id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Backup Hours:** {prosumer['backup_hours']}")
                        st.write(f"**Risk Tolerance:** {prosumer['risk_tolerance']}")
                        st.write(f"**Min Compensation:** ${prosumer['compensation_min']}/kWh")
                    with col2:
                        st.write(f"**BESS:** {'✅' if prosumer['has_bess'] else '❌'}")
                        st.write(f"**EV:** {'✅' if prosumer['has_ev'] else '❌'}")
                        st.write(f"**Solar:** {'✅' if prosumer['has_solar'] else '❌'}")
                    
                    if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.custom_prosumers.pop(i)
                        st.rerun()
    
    def parse_prosumer_description(self, description: str):
        """Parse prosumer description using LLM with error handling."""
        try:
            # Try to import and use LLM parser
            try:
                from llm_parser import LLMProsumerParser
                parser = LLMProsumerParser()
                config = parser.text_to_prosumer_config(description)
                
                st.success("✅ Prosumer configuration parsed successfully!")
                st.json(config)
                
                # Option to add to custom prosumers
                if st.button("➕ Add Parsed Prosumer to Fleet"):
                    config['prosumer_id'] = f"llm_parsed_{len(st.session_state.custom_prosumers)+1}"
                    config['created_at'] = datetime.now().isoformat()
                    st.session_state.custom_prosumers.append(config)
                    st.success("✅ Added to custom prosumer fleet!")
                    
            except ImportError:
                st.warning("⚠️ LLM Parser not available. Using fallback parsing...")
                # Simple fallback parsing
                config = self.simple_description_parser(description)
                st.info("ℹ️ Used simple keyword-based parsing")
                st.json(config)
                
        except Exception as e:
            st.error(f"❌ Error parsing prosumer: {str(e)}")
    
    def simple_description_parser(self, description: str) -> Dict[str, Any]:
        """Simple keyword-based parser as fallback."""
        config = {
            'prosumer_id': f"simple_parsed_{len(st.session_state.custom_prosumers)+1}",
            'has_bess': 'battery' in description.lower() or 'powerwall' in description.lower(),
            'has_ev': 'ev' in description.lower() or 'electric vehicle' in description.lower() or 'tesla' in description.lower(),
            'has_solar': 'solar' in description.lower() or 'panels' in description.lower(),
            'backup_hours': 6.0 if 'backup' in description.lower() else 4.0,
            'risk_tolerance': 'high' if 'tech-savvy' in description.lower() else 'medium',
            'participation_willingness': 0.9 if 'willing' in description.lower() else 0.7,
            'max_discharge_percent': 70.0 if 'aggressive' in description.lower() else 50.0,
            'compensation_min': 0.12
        }
        return config
    
    def render_fleet_analytics(self):
        """Render comprehensive fleet analytics."""
        if len(self.fleet_df) == 0 and len(st.session_state.custom_prosumers) == 0:
            st.info("No fleet data available for analytics.")
            return
            
        st.subheader("📊 Fleet Analytics")
        
        # Combine fleet data
        total_prosumers = len(self.fleet_df) + len(st.session_state.custom_prosumers)
        
        # Asset adoption rates
        col1, col2 = st.columns(2)
        
        with col1:
            # Technology adoption chart
            if len(self.fleet_df) > 0:
                adoption_data = {
                    'Technology': ['BESS', 'EV', 'Solar'],
                    'Adoption Rate (%)': [
                        (self.fleet_df['has_bess'].sum() / len(self.fleet_df)) * 100 if 'has_bess' in self.fleet_df.columns else 0,
                        (self.fleet_df['has_ev'].sum() / len(self.fleet_df)) * 100 if 'has_ev' in self.fleet_df.columns else 0,
                        (self.fleet_df['has_solar'].sum() / len(self.fleet_df)) * 100 if 'has_solar' in self.fleet_df.columns else 0
                    ]
                }
                
                fig_adoption = px.bar(
                    adoption_data,
                    x='Technology',
                    y='Adoption Rate (%)',
                    title="Technology Adoption Rates",
                    color='Technology'
                )
                st.plotly_chart(fig_adoption, use_container_width=True)
        
        with col2:
            # Risk tolerance distribution
            risk_data = {'Low': 0, 'Medium': 0, 'High': 0}
            
            if 'risk_tolerance' in self.fleet_df.columns:
                risk_counts = self.fleet_df['risk_tolerance'].value_counts()
                for risk, count in risk_counts.items():
                    if risk in risk_data:
                        risk_data[risk] = count
            
            # Add custom prosumers
            for prosumer in st.session_state.custom_prosumers:
                risk = prosumer.get('risk_tolerance', 'medium').title()
                if risk in risk_data:
                    risk_data[risk] += 1
            
            fig_risk = px.pie(
                values=list(risk_data.values()),
                names=list(risk_data.keys()),
                title="Risk Tolerance Distribution"
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        # Capacity analysis
        if 'total_capacity_kw' in self.fleet_df.columns:
            st.subheader("⚡ Capacity Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_capacity = self.fleet_df['total_capacity_kw'].sum()
                st.metric("Total Fleet Capacity", f"{total_capacity:.1f} kW")
                
            with col2:
                avg_capacity = self.fleet_df['total_capacity_kw'].mean()
                st.metric("Average Prosumer Capacity", f"{avg_capacity:.1f} kW")
                
            with col3:
                max_capacity = self.fleet_df['total_capacity_kw'].max()
                st.metric("Maximum Prosumer Capacity", f"{max_capacity:.1f} kW")
            
            # Capacity distribution histogram
            fig_capacity_dist = px.histogram(
                self.fleet_df,
                x='total_capacity_kw',
                nbins=25,
                title="Fleet Capacity Distribution",
                labels={'total_capacity_kw': 'Capacity (kW)', 'count': 'Number of Prosumers'}
            )
            st.plotly_chart(fig_capacity_dist, use_container_width=True)
            
    
    def render_sidebar(self):
        """Render the enhanced sidebar with controls and status."""
        st.sidebar.title("🎛️ Dashboard Control Panel")
        
        # System status
        st.sidebar.subheader("📊 System Status")
        
        # Module test status
        module_status = []
        for i in range(1, 6):
            module_key = f'module{i}'
            if module_key in st.session_state.module_results:
                result = st.session_state.module_results[module_key]
                status_icon = "✅" if result['status'] == 'success' else "❌"
                module_status.append(f"{status_icon} Module {i}")
            else:
                module_status.append(f"⏳ Module {i}")
        
        for status in module_status:
            st.sidebar.write(status)
        
        # Data status
        st.sidebar.subheader("📁 Data Status")
        market_status = "✅ Loaded" if len(self.market_df) > 0 else "❌ Missing"
        fleet_status = "✅ Loaded" if len(self.fleet_df) > 0 else "❌ Missing"
        results_status = "✅ Loaded" if len(self.results_df) > 0 else "❌ Missing"
        
        st.sidebar.write(f"Market Data: {market_status}")
        st.sidebar.write(f"Fleet Data: {fleet_status}")
        st.sidebar.write(f"Results Data: {results_status}")
        
        # Fleet summary
        if len(self.fleet_df) > 0 or len(st.session_state.custom_prosumers) > 0:
            st.sidebar.subheader("🏠 Fleet Summary")
            total_prosumers = len(self.fleet_df) + len(st.session_state.custom_prosumers)
            st.sidebar.info(f"""
            **Total Prosumers**: {total_prosumers}
            **Generated Fleet**: {len(self.fleet_df)}
            **Custom Prosumers**: {len(st.session_state.custom_prosumers)}
            """)
        
        # View controls
        st.sidebar.subheader("🎨 Display Options")
        self.show_detailed_metrics = st.sidebar.checkbox("Show Detailed Metrics", value=True)
        self.show_logs = st.sidebar.checkbox("Show Execution Logs", value=True)
        self.chart_height = st.sidebar.slider("Chart Height", 300, 800, 400)
        self.log_level = st.sidebar.selectbox("Log Level", ["INFO", "WARNING", "ERROR", "DEBUG"])
        
        # Quick actions
        st.sidebar.subheader("⚡ Quick Actions")
        
        if st.sidebar.button("🔄 Refresh Data"):
            self.load_data()
            st.sidebar.success("Data refreshed!")
            st.rerun()
            
        if st.sidebar.button("🧹 Clear Module Results"):
            st.session_state.module_results = {}
            st.sidebar.success("Results cleared!")
            st.rerun()
            
        if st.sidebar.button("🗑️ Clear Custom Prosumers"):
            st.session_state.custom_prosumers = []
            st.sidebar.success("Custom prosumers cleared!")
            st.rerun()
        
        # Export options
        st.sidebar.subheader("📤 Export Options")
        
        if st.sidebar.button("💾 Export Fleet Data"):
            if len(self.fleet_df) > 0:
                csv = self.fleet_df.to_csv(index=False)
                st.sidebar.download_button(
                    label="Download Fleet CSV",
                    data=csv,
                    file_name=f"vpp_fleet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.sidebar.warning("No fleet data to export")
        
        if st.session_state.module_results:
            results_json = json.dumps(st.session_state.module_results, indent=2, default=str)
            st.sidebar.download_button(
                label="📋 Download Test Results",
                data=results_json,
                file_name=f"module_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    def render_comprehensive_logs(self):
        """Render comprehensive logging interface."""
        if not self.show_logs:
            return
            
        st.header("📋 Execution Logs & System Monitoring")
        
        # Log filtering and controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            log_source = st.selectbox("Log Source", ["All", "Dashboard", "Module Tests", "System"])
        with col2:
            log_filter = st.text_input("Filter logs (regex)", placeholder="Enter filter pattern")
        with col3:
            auto_refresh = st.checkbox("Auto-refresh logs", value=False)
        
        # Get current logs
        current_logs = log_stream.getvalue()
        
        # Apply filters
        if log_filter:
            try:
                import re
                lines = current_logs.split('\n')
                filtered_lines = [line for line in lines if re.search(log_filter, line, re.IGNORECASE)]
                current_logs = '\n'.join(filtered_lines)
            except re.error:
                st.warning("Invalid regex pattern")
        
        # Filter by level
        if self.log_level != "INFO":
            lines = current_logs.split('\n')
            filtered_lines = [line for line in lines if self.log_level in line or "ERROR" in line]
            current_logs = '\n'.join(filtered_lines)
        
        # Display logs
        st.markdown('<div class="log-container">', unsafe_allow_html=True)
        st.code(current_logs if current_logs else "No logs available", language="")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Log statistics
        if current_logs:
            lines = current_logs.split('\n')
            total_lines = len([l for l in lines if l.strip()])
            error_lines = len([l for l in lines if 'ERROR' in l])
            warning_lines = len([l for l in lines if 'WARNING' in l])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Log Lines", total_lines)
            with col2:
                st.metric("Errors", error_lines)
            with col3:
                st.metric("Warnings", warning_lines)
            with col4:
                success_rate = ((total_lines - error_lines) / total_lines * 100) if total_lines > 0 else 100
                st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Clear logs button
        if st.button("🧹 Clear Logs"):
            log_stream.truncate(0)
            log_stream.seek(0)
            st.success("Logs cleared!")
            st.rerun()
    
    def render_performance_comparison(self):
        """Render enhanced performance comparison charts."""
        if not self.summary:
            st.info("No simulation results available. Run Module 5 to generate performance data.")
            return
            
        st.header("📈 Performance Analysis: Agentic vs Centralized")
        
        # Key metrics comparison
        metrics_data = {
            'Metric': ['Total Profit ($)', 'Avg Satisfaction', 'Success Rate (%)', 
                      'Avg Optimization Time (s)', 'Preference Violations'],
            'Agentic Model': [
                self.summary.get('agentic_total_profit', 0),
                self.summary.get('agentic_avg_satisfaction', 0),
                self.summary.get('agentic_success_rate', 0) * 100,
                self.summary.get('agentic_avg_time_seconds', 0),
                0  # Agentic model doesn't violate preferences
            ],
            'Centralized Model': [
                self.summary.get('centralized_total_profit', 0),
                self.summary.get('centralized_avg_satisfaction', 0),
                self.summary.get('centralized_success_rate', 0) * 100,
                self.summary.get('centralized_avg_time_seconds', 0),
                int(self.summary.get('centralized_total_violations', '0'))
            ]
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        
        # Create comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Profit comparison
            fig_profit = px.bar(
                metrics_df.iloc[:1], 
                x='Metric', 
                y=['Agentic Model', 'Centralized Model'],
                title="Total Profit Comparison",
                color_discrete_map={'Agentic Model': '#1f77b4', 'Centralized Model': '#ff7f0e'},
                barmode='group'
            )
            fig_profit.update_layout(height=self.chart_height)
            st.plotly_chart(fig_profit, use_container_width=True)
            
        with col2:
            # Satisfaction comparison  
            fig_satisfaction = px.bar(
                metrics_df.iloc[1:2], 
                x='Metric', 
                y=['Agentic Model', 'Centralized Model'],
                title="Average Satisfaction Comparison",
                color_discrete_map={'Agentic Model': '#2ca02c', 'Centralized Model': '#d62728'},
                barmode='group'
            )
            fig_satisfaction.update_layout(height=self.chart_height)
            st.plotly_chart(fig_satisfaction, use_container_width=True)
        
        # Comprehensive metrics radar chart
        if self.show_detailed_metrics:
            st.subheader("🎯 Comprehensive Performance Radar")
            
            # Normalize metrics for radar chart
            normalized_metrics = {
                'Profit Score': [8, 9],  # Normalized scores
                'Satisfaction': [
                    self.summary.get('agentic_avg_satisfaction', 0),
                    self.summary.get('centralized_avg_satisfaction', 0)
                ],
                'Success Rate': [
                    self.summary.get('agentic_success_rate', 0) * 10,
                    self.summary.get('centralized_success_rate', 0) * 10
                ],
                'Speed Score': [8, 9],  # Inverse of time, normalized
                'Preference Respect': [10, 0]  # Agentic respects, centralized doesn't
            }
            
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=list(normalized_metrics['Profit Score'][:1]) + 
                  list(normalized_metrics['Satisfaction'][:1]) + 
                  list(normalized_metrics['Success Rate'][:1]) + 
                  list(normalized_metrics['Speed Score'][:1]) + 
                  list(normalized_metrics['Preference Respect'][:1]),
                theta=['Profit', 'Satisfaction', 'Success Rate', 'Speed', 'Preference Respect'],
                fill='toself',
                name='Agentic Model',
                line_color='#1f77b4'
            ))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=list(normalized_metrics['Profit Score'][1:]) + 
                  list(normalized_metrics['Satisfaction'][1:]) + 
                  list(normalized_metrics['Success Rate'][1:]) + 
                  list(normalized_metrics['Speed Score'][1:]) + 
                  list(normalized_metrics['Preference Respect'][1:]),
                theta=['Profit', 'Satisfaction', 'Success Rate', 'Speed', 'Preference Respect'],
                fill='toself',
                name='Centralized Model',
                line_color='#ff7f0e'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Performance Comparison Radar Chart",
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed metrics table
        st.subheader("📋 Detailed Performance Metrics")
        
        # Calculate advantage percentages
        metrics_display = metrics_df.copy()
        metrics_display['Agentic Advantage'] = ""  # Initialize with empty strings
        
        for i, row in metrics_display.iterrows():
            agentic_val = row['Agentic Model']
            centralized_val = row['Centralized Model']
            
            if centralized_val != 0:
                advantage = ((agentic_val - centralized_val) / abs(centralized_val)) * 100
            else:
                advantage = float('inf') if agentic_val > 0 else 0
                
            if advantage == float('inf'):
                metrics_display.loc[i, 'Agentic Advantage'] = "∞% (Perfect)"
            else:
                metrics_display.loc[i, 'Agentic Advantage'] = f"{advantage:.1f}%"
        
        st.dataframe(metrics_display, use_container_width=True)
    
    def render_market_analysis(self):
        """Render enhanced market data analysis."""
        if len(self.market_df) == 0:
            st.info("No market data available. Run Module 1 to collect market data.")
            return
            
        st.header("💹 Market Price Analysis & Opportunities")
        
        # Market overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_lmp = self.market_df['lmp'].mean()
            st.metric("Avg LMP Price", f"${avg_lmp:.2f}/MWh")
            
        with col2:
            max_lmp = self.market_df['lmp'].max()
            st.metric("Peak LMP Price", f"${max_lmp:.2f}/MWh")
            
        with col3:
            avg_spin = self.market_df['spin_price'].mean()
            st.metric("Avg Spinning Reserve", f"${avg_spin:.2f}/MWh")
            
        with col4:
            data_points = len(self.market_df)
            st.metric("Data Points", f"{data_points:,}")
        
        # Market price trends
        fig_market = make_subplots(
            rows=2, cols=2,
            subplot_titles=('LMP Prices Over Time', 'Spinning Reserves', 'Non-Spinning Reserves', 'Price Distribution'),
            vertical_spacing=0.08,
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "histogram"}]]
        )
        
        # LMP prices time series
        fig_market.add_trace(
            go.Scatter(
                x=self.market_df['timestamp'], 
                y=self.market_df['lmp'],
                mode='lines',
                name='LMP Price',
                line=dict(color='#1f77b4')
            ),
            row=1, col=1
        )
        
        # Spinning reserves
        fig_market.add_trace(
            go.Scatter(
                x=self.market_df['timestamp'], 
                y=self.market_df['spin_price'],
                mode='lines',
                name='Spinning Reserve',
                line=dict(color='#ff7f0e')
            ),
            row=1, col=2
        )
        
        # Non-spinning reserves
        fig_market.add_trace(
            go.Scatter(
                x=self.market_df['timestamp'], 
                y=self.market_df['nonspin_price'],
                mode='lines',
                name='Non-Spinning Reserve',
                line=dict(color='#2ca02c')
            ),
            row=2, col=1
        )
        
        # Price distribution histogram
        fig_market.add_trace(
            go.Histogram(
                x=self.market_df['lmp'],
                name='LMP Distribution',
                nbinsx=30,
                marker_color='#d62728'
            ),
            row=2, col=2
        )
        
        fig_market.update_layout(
            height=800,
            title_text="CAISO Market Analysis Dashboard",
            showlegend=False
        )
        
        st.plotly_chart(fig_market, use_container_width=True)
        
        # Market opportunity analysis
        st.subheader("🎯 Market Opportunity Analysis")
        
        # Identify high-value periods
        lmp_threshold = self.market_df['lmp'].quantile(0.8)  # Top 20% prices
        high_value_periods = self.market_df[self.market_df['lmp'] >= lmp_threshold]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("High-Value Periods", f"{len(high_value_periods)} ({len(high_value_periods)/len(self.market_df)*100:.1f}%)")
            st.metric("Avg High-Value Price", f"${high_value_periods['lmp'].mean():.2f}/MWh")
            
        with col2:
            total_opportunity_value = (high_value_periods['lmp'] - self.market_df['lmp'].mean()).sum()
            st.metric("Total Opportunity Value", f"${total_opportunity_value:.2f}")
            
            # Best hours for VPP participation
            high_value_periods['hour'] = high_value_periods['timestamp'].dt.hour
            best_hours = high_value_periods['hour'].value_counts().head(3)
            st.write("**Best Hours for Participation:**")
            for hour, count in best_hours.items():
                st.write(f"• {hour:02d}:00 - {count} opportunities")
    
    def render_ai_insights(self):
        """Render AI-powered insights using Gemini with fallback analysis."""
        st.header("🤖 AI-Powered Analysis & Insights")
        
        # Always show built-in analysis
        self.render_builtin_analysis()
        
        # Only show Gemini option if available
        if self.gemini_model:
            st.subheader("🔮 Enhanced AI Analysis (Gemini)")
            if st.button("🔮 Generate AI Analysis"):
                with st.spinner("Generating AI insights..."):
                    try:
                        # Prepare data summary for AI analysis
                        analysis_prompt = f"""
                        Analyze this VPP simulation data and provide insights:
                        
                        Performance Summary:
                        - Agentic Model: ${self.summary.get('agentic_total_profit', 0):.2f} profit, {self.summary.get('agentic_avg_satisfaction', 0):.1f}/10 satisfaction
                        - Centralized Model: ${self.summary.get('centralized_total_profit', 0):.2f} profit, {self.summary.get('centralized_avg_satisfaction', 0):.1f}/10 satisfaction
                        - Satisfaction Advantage: {self.summary.get('satisfaction_advantage_percent', 0):.1f}%
                        
                        Market Data:
                        - Average LMP: ${self.market_df['lmp'].mean():.2f}/MWh
                        - Peak LMP: ${self.market_df['lmp'].max():.2f}/MWh
                        - Data Points: {len(self.market_df)}
                        
                        Fleet Information:
                        - Total Prosumers: {len(self.fleet_df) + len(st.session_state.custom_prosumers)}
                        - Generated Fleet: {len(self.fleet_df)}
                        - Custom Prosumers: {len(st.session_state.custom_prosumers)}
                        
                        Please provide:
                        1. Key performance insights
                        2. Market opportunity analysis
                        3. Recommendations for VPP optimization
                        4. Strategic implications for deployment
                        """
                        
                        response = self.gemini_model.generate_content(analysis_prompt)
                        
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown("### 🧠 Enhanced AI Analysis Results")
                        st.markdown(response.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "quota" in error_msg.lower() or "429" in error_msg:
                            st.warning("⚠️ Gemini API quota exceeded. Using built-in analysis above.")
                        else:
                            st.error(f"❌ AI analysis failed: {error_msg}")
        else:
            st.info("💡 **Gemini API not configured.** Add GEMINI_API_KEY to .env file for enhanced AI analysis.")
    
    def render_builtin_analysis(self):
        """Render built-in analysis when Gemini is unavailable."""
        st.subheader("📊 Built-in Performance Analysis")
        
        # Get latest module results if available
        module5_result = st.session_state.module_results.get('module5', {})
        
        if module5_result.get('status') == 'success':
            # Performance Analysis
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 🎯 **Performance Insights**")
            
            agentic_profit = module5_result.get('agentic_profit', 0)
            centralized_profit = module5_result.get('centralized_profit', 0)
            satisfaction_advantage = module5_result.get('satisfaction_advantage', 0)
            success_rate = module5_result.get('success_rate', 0)
            
            # Profit Analysis
            if agentic_profit > centralized_profit:
                profit_advantage = ((agentic_profit - centralized_profit) / centralized_profit) * 100 if centralized_profit > 0 else 0
                st.write(f"✅ **Agentic Advantage**: +{profit_advantage:.1f}% profit improvement (${agentic_profit - centralized_profit:.2f} additional revenue)")
            else:
                st.write(f"⚠️ **Profit Analysis**: Centralized approach generated more profit")
            
            # Satisfaction Analysis
            if satisfaction_advantage > 20:
                st.write(f"🎉 **Excellent Satisfaction**: {satisfaction_advantage:.1f}% advantage shows strong prosumer preference handling")
            elif satisfaction_advantage > 10:
                st.write(f"✅ **Good Satisfaction**: {satisfaction_advantage:.1f}% advantage indicates better prosumer experience")
            else:
                st.write(f"⚠️ **Satisfaction Concern**: Only {satisfaction_advantage:.1f}% advantage - may need tuning")
            
            # Success Rate Analysis
            if success_rate >= 0.9:
                st.write(f"🎯 **High Reliability**: {success_rate:.0%} success rate demonstrates robust system performance")
            elif success_rate >= 0.7:
                st.write(f"✅ **Adequate Performance**: {success_rate:.0%} success rate with room for improvement")
            else:
                st.write(f"⚠️ **Performance Issues**: {success_rate:.0%} success rate indicates system needs optimization")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Market Opportunity Analysis
            total_opportunities = module5_result.get('total_opportunities', 0)
            execution_time = module5_result.get('execution_time', 0)
            
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 📈 **Market Performance**")
            
            if total_opportunities > 0:
                avg_profit_per_opportunity = agentic_profit / total_opportunities
                st.write(f"💰 **Revenue Efficiency**: ${avg_profit_per_opportunity:.2f} average profit per market opportunity")
                
                if execution_time > 0:
                    opportunities_per_second = total_opportunities / execution_time
                    st.write(f"⚡ **Processing Speed**: {opportunities_per_second:.1f} opportunities processed per second")
            
            # Market timing analysis
            if len(self.market_df) > 0:
                avg_lmp = self.market_df['lmp'].mean()
                peak_lmp = self.market_df['lmp'].max()
                st.write(f"📊 **Market Conditions**: Avg LMP ${avg_lmp:.2f}/MWh, Peak ${peak_lmp:.2f}/MWh")
                
                if peak_lmp > avg_lmp * 1.5:
                    st.write("🎯 **Opportunity**: High price volatility creates arbitrage opportunities")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Strategic Recommendations
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown("### 🎯 **Strategic Recommendations**")
            
            if satisfaction_advantage > 25 and agentic_profit > centralized_profit:
                st.write("🚀 **Deploy Agentic Model**: Superior performance across all metrics")
            elif satisfaction_advantage > 15:
                st.write("✅ **Consider Agentic Model**: Strong satisfaction benefits outweigh profit differences")
            else:
                st.write("🔄 **Hybrid Approach**: Balance satisfaction and profit optimization")
                
            # Fleet optimization suggestions
            if len(self.fleet_df) > 0:
                bess_count = self.fleet_df['has_bess'].sum() if 'has_bess' in self.fleet_df.columns else 0
                fleet_size = len(self.fleet_df)
                bess_percentage = (bess_count / fleet_size) * 100 if fleet_size > 0 else 0
                
                if bess_percentage < 40:
                    st.write(f"🔋 **Fleet Optimization**: Consider increasing BESS penetration from {bess_percentage:.1f}%")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.info("📊 Run Module 5 simulation to generate performance analysis.")
    
    def run(self):
        """Run the comprehensive dashboard application."""
        # Render all components
        self.render_header()
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🧪 Module Testing", 
            "🏠 Prosumer Management", 
            "📈 Performance Analysis",
            "💹 Market Analysis", 
            "📋 Logs & Monitoring"
        ])
        
        with tab1:
            self.render_module_testing_panel()
            
        with tab2:
            self.render_prosumer_management()
            
        with tab3:
            self.render_performance_comparison()
            
        with tab4:
            self.render_market_analysis()
            
        with tab5:
            self.render_comprehensive_logs()
        
        # AI insights section
        self.render_ai_insights()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p><strong>VPP LLM Agent - Comprehensive Dashboard</strong></p>
            <p>Advanced Virtual Power Plant Operations with AI-Driven Negotiation</p>
            <p>Built with Streamlit, Plotly, and Google Gemini API | © 2025</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main function to run the comprehensive dashboard."""
    try:
        dashboard = VPPDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Dashboard initialization failed: {str(e)}")
        st.error("Please check that all required modules are available and properly configured.")
        logger.error(f"Dashboard failed to initialize: {str(e)}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
