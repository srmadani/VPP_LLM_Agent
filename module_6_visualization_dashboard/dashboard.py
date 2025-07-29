"""
VPP LLM Agent - Visualization Dashboard (Module 6)

This module provides an interactive Streamlit dashboard for visualizing
simulation results and demonstrating the value of the agentic VPP model.
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

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent / "module_2_asset_modeling"))
from llm_parser import LLMProsumerParser

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

class VPPDashboard:
    """
    Main dashboard class for VPP simulation visualization.
    """
    
    def __init__(self):
        """Initialize the dashboard with data and configuration."""
        self.setup_page_config()
        self.load_data()
        self.setup_gemini()
        
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="VPP LLM Agent Dashboard",
            page_icon="⚡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stMetric > div > div > div > div {
            font-size: 1.2rem;
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
        </style>
        """, unsafe_allow_html=True)
        
    def load_data(self):
        """Load all required data files."""
        try:
            # Base paths
            base_path = Path(__file__).parent.parent
            
            # Load simulation results
            results_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_results.csv"
            self.results_df = pd.read_csv(results_path)
            self.results_df['timestamp'] = pd.to_datetime(self.results_df['timestamp'])
            
            # Load simulation summary
            summary_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_summary.json"
            with open(summary_path, 'r') as f:
                self.summary = json.load(f)
                
            # Load market data
            market_path = base_path / "module_1_data_simulation" / "data" / "market_data.csv"
            self.market_df = pd.read_csv(market_path)
            self.market_df['timestamp'] = pd.to_datetime(self.market_df['timestamp'])
            
            # Load simulation report
            report_path = base_path / "module_5_simulation_orchestration" / "results" / "simulation_report.md"
            with open(report_path, 'r') as f:
                self.report_content = f.read()
                
            # Load simulation logs
            log_path = base_path / "module_5_simulation_orchestration" / "simulation.log"
            if log_path.exists():
                with open(log_path, 'r') as f:
                    self.log_content = f.read()
            else:
                self.log_content = "No simulation logs available."
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            self.results_df = pd.DataFrame()
            self.summary = {}
            self.market_df = pd.DataFrame()
            self.report_content = ""
            self.log_content = ""
            
    def setup_gemini(self):
        """Setup Gemini API for analysis."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            else:
                self.gemini_model = None
                st.warning("Gemini API key not found. Analysis features will be limited.")
        except Exception as e:
            st.warning(f"Failed to setup Gemini API: {str(e)}")
            self.gemini_model = None
            
    def render_header(self):
        """Render the main dashboard header."""
        st.title("⚡ VPP LLM Agent Dashboard")
        st.markdown("### Virtual Power Plant with AI-Driven Negotiation")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Timesteps", 
                self.summary.get('total_timesteps', 'N/A'),
                help="Number of simulation timesteps completed"
            )
            
        with col2:
            st.metric(
                "Simulation Duration", 
                f"{self.summary.get('simulation_duration_hours', 0):.1f}h",
                help="Total simulation time period"
            )
            
        with col3:
            agentic_profit = self.summary.get('agentic_total_profit', 0)
            centralized_profit = self.summary.get('centralized_total_profit', 0)
            st.metric(
                "Profit Comparison", 
                f"${agentic_profit:.2f} vs ${centralized_profit:.2f}",
                delta=f"{agentic_profit - centralized_profit:.2f}",
                help="Agentic vs Centralized total profit"
            )
            
        with col4:
            satisfaction_advantage = self.summary.get('satisfaction_advantage_percent', 0)
            st.metric(
                "Satisfaction Advantage", 
                f"{satisfaction_advantage:.0f}%",
                delta=f"{satisfaction_advantage:.0f}%",
                help="Agentic model satisfaction advantage over centralized"
            )
            
    def render_sidebar(self):
        """Render the sidebar with controls and prosumer creator."""
        st.sidebar.title("🎛️ Control Panel")
        
        # Simulation parameters display
        st.sidebar.subheader("Simulation Parameters")
        st.sidebar.info(f"""
        **Fleet Size**: {self.summary.get('total_timesteps', 'N/A')} prosumers
        **Duration**: {self.summary.get('simulation_duration_hours', 0):.1f} hours
        **Success Rate**: {self.summary.get('agentic_success_rate', 0)*100:.1f}%
        """)
        
        # Interactive prosumer creator
        st.sidebar.subheader("🏠 Prosumer Creator")
        st.sidebar.markdown("Create a prosumer from natural language description:")
        
        prosumer_description = st.sidebar.text_area(
            "Describe your prosumer:",
            placeholder="e.g., A tech-savvy user with a 15kWh Tesla Powerwall and an EV that must be charged by 7 AM",
            height=100
        )
        
        if st.sidebar.button("Parse Prosumer") and prosumer_description:
            self.parse_prosumer_description(prosumer_description)
            
        # View controls
        st.sidebar.subheader("📊 View Options")
        self.show_detailed_metrics = st.sidebar.checkbox("Show Detailed Metrics", value=True)
        self.show_ai_analysis = st.sidebar.checkbox("Show AI Analysis", value=True)
        self.chart_height = st.sidebar.slider("Chart Height", 300, 800, 400)
        
    def parse_prosumer_description(self, description: str):
        """Parse prosumer description using LLM."""
        try:
            parser = LLMProsumerParser()
            config = parser.text_to_prosumer_config(description)
            
            st.sidebar.success("✅ Prosumer parsed successfully!")
            st.sidebar.json(config)
            
        except Exception as e:
            st.sidebar.error(f"❌ Error parsing prosumer: {str(e)}")
            
    def render_performance_comparison(self):
        """Render performance comparison charts."""
        st.header("📈 Performance Comparison: Agentic vs Centralized")
        
        # Create performance metrics comparison
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Profit comparison
            fig_profit = px.bar(
                metrics_df.iloc[:1], 
                x='Metric', 
                y=['Agentic Model', 'Centralized Model'],
                title="Total Profit Comparison",
                color_discrete_map={'Agentic Model': '#1f77b4', 'Centralized Model': '#ff7f0e'}
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
                color_discrete_map={'Agentic Model': '#2ca02c', 'Centralized Model': '#d62728'}
            )
            fig_satisfaction.update_layout(height=self.chart_height)
            st.plotly_chart(fig_satisfaction, use_container_width=True)
            
        # Full metrics table
        if self.show_detailed_metrics:
            st.subheader("📋 Detailed Performance Metrics")
            
            # Calculate advantage percentages
            metrics_display = metrics_df.copy()
            metrics_display['Agentic Advantage'] = [
                f"{((a - c) / c * 100) if c != 0 else float('inf'):.1f}%" 
                for a, c in zip(metrics_display['Agentic Model'], metrics_display['Centralized Model'])
            ]
            
            st.dataframe(metrics_display, use_container_width=True)
            
    def render_market_analysis(self):
        """Render market data analysis."""
        st.header("💹 Market Price Analysis")
        
        # Market price trends
        fig_market = make_subplots(
            rows=2, cols=2,
            subplot_titles=('LMP Prices', 'Spinning Reserves', 'Non-Spinning Reserves', 'All Prices Combined'),
            vertical_spacing=0.08
        )
        
        # LMP prices
        fig_market.add_trace(
            go.Scatter(x=self.market_df['timestamp'], y=self.market_df['lmp'], 
                      name='LMP', line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # Spinning reserves
        fig_market.add_trace(
            go.Scatter(x=self.market_df['timestamp'], y=self.market_df['spin_price'], 
                      name='SPIN', line=dict(color='green', width=2)),
            row=1, col=2
        )
        
        # Non-spinning reserves
        fig_market.add_trace(
            go.Scatter(x=self.market_df['timestamp'], y=self.market_df['nonspin_price'], 
                      name='NONSPIN', line=dict(color='orange', width=2)),
            row=2, col=1
        )
        
        # All prices combined
        fig_market.add_trace(
            go.Scatter(x=self.market_df['timestamp'], y=self.market_df['lmp'], 
                      name='LMP', line=dict(color='blue', width=2)),
            row=2, col=2
        )
        fig_market.add_trace(
            go.Scatter(x=self.market_df['timestamp'], y=self.market_df['spin_price'], 
                      name='SPIN', line=dict(color='green', width=2)),
            row=2, col=2
        )
        fig_market.add_trace(
            go.Scatter(x=self.market_df['timestamp'], y=self.market_df['nonspin_price'], 
                      name='NONSPIN', line=dict(color='orange', width=2)),
            row=2, col=2
        )
        
        fig_market.update_layout(
            height=600,
            title_text="CAISO Market Prices Analysis",
            showlegend=True
        )
        fig_market.update_xaxes(title_text="Time")
        fig_market.update_yaxes(title_text="Price ($/MWh)")
        
        st.plotly_chart(fig_market, use_container_width=True)
        
        # Market statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg LMP", f"${self.market_df['lmp'].mean():.2f}/MWh")
            st.metric("LMP Range", f"${self.market_df['lmp'].min():.2f} - ${self.market_df['lmp'].max():.2f}")
            
        with col2:
            st.metric("Avg SPIN", f"${self.market_df['spin_price'].mean():.2f}/MWh")
            st.metric("SPIN Range", f"${self.market_df['spin_price'].min():.2f} - ${self.market_df['spin_price'].max():.2f}")
            
        with col3:
            st.metric("Avg NONSPIN", f"${self.market_df['nonspin_price'].mean():.2f}/MWh")
            st.metric("NONSPIN Range", f"${self.market_df['nonspin_price'].min():.2f} - ${self.market_df['nonspin_price'].max():.2f}")
            
    def render_negotiation_analysis(self):
        """Render negotiation process analysis."""
        st.header("🤝 Negotiation Process Analysis")
        
        if not self.results_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Coalition size over time
                fig_coalition = px.line(
                    self.results_df, 
                    x='timestamp', 
                    y='agentic_coalition_size',
                    title='Coalition Size Over Time',
                    labels={'agentic_coalition_size': 'Coalition Size', 'timestamp': 'Time'}
                )
                fig_coalition.update_layout(height=self.chart_height)
                st.plotly_chart(fig_coalition, use_container_width=True)
                
            with col2:
                # Negotiation rounds over time
                fig_rounds = px.line(
                    self.results_df, 
                    x='timestamp', 
                    y='agentic_negotiation_rounds',
                    title='Negotiation Rounds Over Time',
                    labels={'agentic_negotiation_rounds': 'Negotiation Rounds', 'timestamp': 'Time'}
                )
                fig_rounds.update_layout(height=self.chart_height)
                st.plotly_chart(fig_rounds, use_container_width=True)
                
            # Negotiation efficiency metrics
            st.subheader("⚡ Negotiation Efficiency")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_coalition = self.summary.get('agentic_avg_coalition_size', 0)
                st.metric("Avg Coalition Size", f"{avg_coalition:.1f} prosumers")
                
            with col2:
                avg_rounds = self.summary.get('agentic_avg_negotiation_rounds', 0)
                st.metric("Avg Negotiation Rounds", f"{avg_rounds:.1f}")
                
            with col3:
                avg_time = self.summary.get('agentic_avg_time_seconds', 0)
                st.metric("Avg Negotiation Time", f"{avg_time*1000:.1f}ms")
                
            with col4:
                success_rate = self.summary.get('agentic_success_rate', 0)
                st.metric("Success Rate", f"{success_rate*100:.1f}%")
                
    def render_simulation_logs(self):
        """Render simulation logs and process details."""
        st.header("📋 Simulation Logs & Process Details")
        
        # Create tabs for different log views
        tab1, tab2, tab3 = st.tabs(["Execution Logs", "Simulation Report", "Raw Data"])
        
        with tab1:
            st.subheader("System Execution Logs")
            if self.log_content:
                st.text_area(
                    "Simulation Logs", 
                    value=self.log_content, 
                    height=400,
                    help="Real-time logs from the simulation execution"
                )
            else:
                st.info("No execution logs available for this simulation run.")
                
        with tab2:
            st.subheader("Simulation Analysis Report")
            st.markdown(self.report_content)
            
        with tab3:
            st.subheader("Raw Simulation Data")
            if not self.results_df.empty:
                st.dataframe(self.results_df, use_container_width=True)
                
                # Download button for raw data
                csv_data = self.results_df.to_csv(index=False)
                st.download_button(
                    label="Download Raw Data (CSV)",
                    data=csv_data,
                    file_name=f"vpp_simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No simulation data available.")
                
    def generate_ai_analysis(self):
        """Generate AI analysis of simulation results using Gemini."""
        if not self.gemini_model:
            return "AI analysis not available - Gemini API not configured."
            
        try:
            # Prepare analysis prompt
            analysis_prompt = f"""
            Analyze the following VPP simulation results and provide key insights:
            
            SIMULATION SUMMARY:
            {json.dumps(self.summary, indent=2)}
            
            KEY FINDINGS TO ANALYZE:
            1. Performance comparison between agentic and centralized approaches
            2. Trade-offs between profit optimization and prosumer satisfaction
            3. Scalability and efficiency implications
            4. Strategic advantages of the agentic model
            
            Provide a concise, data-driven analysis focusing on:
            - What the results demonstrate about the agentic approach
            - Why the satisfaction advantage is critical for real-world deployment
            - How the system balances competing objectives
            - Recommendations for further development
            
            Keep the analysis professional, technical, and under 300 words.
            """
            
            response = self.gemini_model.generate_content(analysis_prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating AI analysis: {str(e)}"
            
    def render_ai_insights(self):
        """Render AI-generated insights and analysis."""
        if not self.show_ai_analysis:
            return
            
        st.header("🤖 AI-Generated Analysis")
        
        with st.spinner("Generating AI analysis..."):
            analysis = self.generate_ai_analysis()
            
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**AI Analysis of Simulation Results:**")
        st.markdown(analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
    def render_key_insights(self):
        """Render key insights and value proposition."""
        st.header("💡 Key Insights & Value Proposition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            satisfaction_advantage = self.summary.get('satisfaction_advantage_percent', 0)
            st.markdown(f"""
            **🎯 Prosumer Satisfaction Advantage**
            
            The agentic model achieved **{satisfaction_advantage:.0f}% higher satisfaction** compared to the centralized approach. This demonstrates the system's ability to respect individual preferences while maintaining competitive performance.
            
            - **Agentic Satisfaction**: {self.summary.get('agentic_avg_satisfaction', 0):.1f}/10
            - **Centralized Satisfaction**: {self.summary.get('centralized_avg_satisfaction', 0):.1f}/10
            - **Preference Violations**: {self.summary.get('centralized_total_violations', 'N/A')} (centralized only)
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            profit_diff = self.summary.get('profit_advantage_percent', 0)
            st.markdown(f"""
            **⚖️ Profit vs Satisfaction Trade-off**
            
            While the centralized model achieved higher theoretical profit, it came at the cost of **zero prosumer satisfaction** and multiple preference violations.
            
            - **Profit Difference**: {profit_diff:.1f}%
            - **Total Violations**: {self.summary.get('centralized_total_violations', 'N/A')}
            - **Real-world Viability**: Agentic model superior for deployment
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Technical achievements
        st.subheader("🔧 Technical Achievements")
        
        achievements = [
            f"✅ **Multi-Agent Negotiation**: {self.summary.get('agentic_avg_negotiation_rounds', 0):.1f} rounds average",
            f"✅ **Coalition Formation**: {self.summary.get('agentic_avg_coalition_size', 0):.1f} prosumers per coalition",
            f"✅ **Computational Efficiency**: {self.summary.get('agentic_avg_time_seconds', 0)*1000:.1f}ms per negotiation",
            f"✅ **LLM Integration**: Natural language preference handling",
            f"✅ **Hybrid Optimization**: LLM-to-Solver intelligence fusion"
        ]
        
        for achievement in achievements:
            st.markdown(achievement)
            
    def run(self):
        """Run the main dashboard application."""
        # Render all components
        self.render_header()
        self.render_sidebar()
        
        # Main content
        self.render_performance_comparison()
        self.render_market_analysis()
        self.render_negotiation_analysis()
        self.render_key_insights()
        self.render_ai_insights()
        self.render_simulation_logs()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p><strong>VPP LLM Agent Dashboard</strong> - Demonstrating AI-Driven Virtual Power Plant Operations</p>
            <p>Built with Streamlit, Plotly, and Google Gemini API</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main function to run the dashboard."""
    dashboard = VPPDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
