"""
VPP Agent PoC - Module 1: Data Dashboard
Interactive dashboard for visualizing and analyzing the collected VPP simulation data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure matplotlib for better plots
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VPPDataDashboard:
    """Interactive dashboard for VPP simulation data analysis."""
    
    def __init__(self, data_dir="data"):
        """Initialize the dashboard with data directory."""
        self.data_dir = Path(data_dir)
        self.market_data = None
        self.solar_data = None
        self.load_profiles = {}
        self.load_data()
    
    def load_data(self):
        """Load all VPP simulation data."""
        logger.info("Loading VPP simulation data...")
        
        # Load market data
        market_path = self.data_dir / "market_data.csv"
        if market_path.exists():
            self.market_data = pd.read_csv(market_path)
            self.market_data['timestamp'] = pd.to_datetime(self.market_data['timestamp'])
            self.market_data.set_index('timestamp', inplace=True)
            logger.info(f"✅ Loaded {len(self.market_data)} market data points")
        
        # Load solar data
        solar_path = self.data_dir / "solar_data.csv"
        if solar_path.exists():
            self.solar_data = pd.read_csv(solar_path)
            self.solar_data['timestamp'] = pd.to_datetime(self.solar_data['timestamp'])
            self.solar_data.set_index('timestamp', inplace=True)
            logger.info(f"✅ Loaded {len(self.solar_data)} solar data points")
        
        # Load load profiles
        load_profiles_dir = self.data_dir / "load_profiles"
        if load_profiles_dir.exists():
            profile_files = list(load_profiles_dir.glob("profile_*.csv"))
            for profile_file in profile_files:
                profile_name = profile_file.stem
                profile_df = pd.read_csv(profile_file)
                profile_df['timestamp'] = pd.to_datetime(profile_df['timestamp'])
                profile_df.set_index('timestamp', inplace=True)
                self.load_profiles[profile_name] = profile_df
            logger.info(f"✅ Loaded {len(self.load_profiles)} load profiles")
    
    def create_market_analysis(self):
        """Generate market data analysis and visualizations."""
        if self.market_data is None:
            logger.error("Market data not available")
            return
        
        logger.info("Creating market data analysis...")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('CAISO Market Data Analysis\n(August 15-21, 2023)', fontsize=16, fontweight='bold')
        
        # 1. Time series plot
        ax1 = axes[0, 0]
        ax1.plot(self.market_data.index, self.market_data['lmp'], 
                label='LMP', linewidth=1.5, color='#2E86AB')
        ax1.plot(self.market_data.index, self.market_data['spin_price'], 
                label='Spinning Reserve', linewidth=1, alpha=0.7, color='#A23B72')
        ax1.plot(self.market_data.index, self.market_data['nonspin_price'], 
                label='Non-Spinning Reserve', linewidth=1, alpha=0.7, color='#F18F01')
        ax1.set_title('Market Prices Over Time', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price ($/MWh)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Daily patterns
        ax2 = axes[0, 1]
        self.market_data['hour'] = self.market_data.index.hour
        hourly_avg = self.market_data.groupby('hour')['lmp'].mean()
        hourly_std = self.market_data.groupby('hour')['lmp'].std()
        
        ax2.plot(hourly_avg.index, hourly_avg.values, 'o-', linewidth=2, 
                markersize=6, color='#2E86AB', label='Average LMP')
        ax2.fill_between(hourly_avg.index, 
                        hourly_avg.values - hourly_std.values,
                        hourly_avg.values + hourly_std.values, 
                        alpha=0.3, color='#2E86AB')
        ax2.set_title('Average Daily Price Pattern', fontweight='bold')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('LMP ($/MWh)')
        ax2.set_xticks(range(0, 24, 4))
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. Price distribution
        ax3 = axes[1, 0]
        ax3.hist(self.market_data['lmp'], bins=30, alpha=0.7, color='#2E86AB', 
                edgecolor='black', linewidth=0.5)
        ax3.axvline(self.market_data['lmp'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: ${self.market_data["lmp"].mean():.2f}')
        ax3.axvline(self.market_data['lmp'].median(), color='orange', linestyle='--', 
                   linewidth=2, label=f'Median: ${self.market_data["lmp"].median():.2f}')
        ax3.set_title('LMP Distribution', fontweight='bold')
        ax3.set_xlabel('LMP ($/MWh)')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Weekly pattern
        ax4 = axes[1, 1]
        self.market_data['day_of_week'] = self.market_data.index.dayofweek
        daily_avg = self.market_data.groupby('day_of_week')['lmp'].mean()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        bars = ax4.bar(range(len(daily_avg)), daily_avg.values, 
                      color=['#2E86AB' if i < 5 else '#F18F01' for i in range(len(daily_avg))],
                      alpha=0.8, edgecolor='black', linewidth=0.5)
        ax4.set_title('Average Price by Day of Week', fontweight='bold')
        ax4.set_xlabel('Day of Week')
        ax4.set_ylabel('Average LMP ($/MWh)')
        ax4.set_xticks(range(len(days)))
        ax4.set_xticklabels(days)
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, daily_avg.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'${value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('vpp_market_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print summary statistics
        print("\n" + "="*60)
        print("📊 MARKET DATA SUMMARY STATISTICS")
        print("="*60)
        print(f"📈 LMP Statistics:")
        print(f"   Mean: ${self.market_data['lmp'].mean():.2f}/MWh")
        print(f"   Median: ${self.market_data['lmp'].median():.2f}/MWh")
        print(f"   Std Dev: ${self.market_data['lmp'].std():.2f}/MWh")
        print(f"   Min: ${self.market_data['lmp'].min():.2f}/MWh")
        print(f"   Max: ${self.market_data['lmp'].max():.2f}/MWh")
        print(f"   Peak Hours (16-20): ${self.market_data[self.market_data.index.hour.isin([16,17,18,19,20])]['lmp'].mean():.2f}/MWh")
        print(f"   Off-Peak Hours (22-06): ${self.market_data[self.market_data.index.hour.isin([22,23,0,1,2,3,4,5,6])]['lmp'].mean():.2f}/MWh")
        
    def create_solar_analysis(self):
        """Generate solar data analysis and visualizations."""
        if self.solar_data is None:
            logger.error("Solar data not available")
            return
        
        logger.info("Creating solar data analysis...")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Solar Generation Analysis\n(Los Angeles, CA - August 15-21, 2023)', 
                    fontsize=16, fontweight='bold')
        
        # 1. Time series plot
        ax1 = axes[0, 0]
        ax1.plot(self.solar_data.index, 
                self.solar_data['generation_kw_per_kw_installed'] * 1000,  # Convert to W/kW
                linewidth=1.5, color='#F18F01', alpha=0.8)
        ax1.fill_between(self.solar_data.index, 
                        self.solar_data['generation_kw_per_kw_installed'] * 1000,
                        alpha=0.3, color='#F18F01')
        ax1.set_title('Solar Generation Over Time', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Generation (W/kW installed)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Daily generation patterns
        ax2 = axes[0, 1]
        self.solar_data['hour'] = self.solar_data.index.hour
        hourly_avg = self.solar_data.groupby('hour')['generation_kw_per_kw_installed'].mean()
        hourly_max = self.solar_data.groupby('hour')['generation_kw_per_kw_installed'].max()
        
        ax2.plot(hourly_avg.index, hourly_avg.values * 1000, 'o-', 
                linewidth=2, markersize=6, color='#F18F01', label='Average')
        ax2.plot(hourly_max.index, hourly_max.values * 1000, 's-', 
                linewidth=1, markersize=4, color='#A23B72', alpha=0.7, label='Peak')
        ax2.fill_between(hourly_avg.index, hourly_avg.values * 1000, 
                        alpha=0.3, color='#F18F01')
        ax2.set_title('Daily Solar Generation Pattern', fontweight='bold')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Generation (W/kW installed)')
        ax2.set_xticks(range(0, 24, 2))
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Generation distribution
        ax3 = axes[1, 0]
        # Only plot non-zero values for better visualization
        non_zero_gen = self.solar_data[self.solar_data['generation_kw_per_kw_installed'] > 0.01]['generation_kw_per_kw_installed']
        ax3.hist(non_zero_gen * 1000, bins=25, alpha=0.7, color='#F18F01', 
                edgecolor='black', linewidth=0.5)
        ax3.axvline(non_zero_gen.mean() * 1000, color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {non_zero_gen.mean()*1000:.0f} W/kW')
        ax3.set_title('Solar Generation Distribution\n(Daylight Hours Only)', fontweight='bold')
        ax3.set_xlabel('Generation (W/kW installed)')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Daily energy production
        ax4 = axes[1, 1]
        self.solar_data['date'] = self.solar_data.index.date
        daily_energy = self.solar_data.groupby('date')['generation_kw_per_kw_installed'].sum() / 4  # Convert to kWh/kW (15-min intervals)
        
        bars = ax4.bar(range(len(daily_energy)), daily_energy.values, 
                      color='#F18F01', alpha=0.8, edgecolor='black', linewidth=0.5)
        ax4.set_title('Daily Energy Production', fontweight='bold')
        ax4.set_xlabel('Day')
        ax4.set_ylabel('Energy (kWh/kW/day)')
        ax4.set_xticks(range(len(daily_energy)))
        ax4.set_xticklabels([f'Day {i+1}' for i in range(len(daily_energy))])
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, daily_energy.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('vpp_solar_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print summary statistics
        print("\n" + "="*60)
        print("☀️ SOLAR GENERATION SUMMARY STATISTICS")
        print("="*60)
        print(f"🔆 Generation Statistics (per kW installed):")
        print(f"   Peak Generation: {self.solar_data['generation_kw_per_kw_installed'].max()*1000:.0f} W/kW")
        print(f"   Average (All Hours): {self.solar_data['generation_kw_per_kw_installed'].mean()*1000:.0f} W/kW")
        print(f"   Average (Daylight): {non_zero_gen.mean()*1000:.0f} W/kW")
        print(f"   Daily Energy: {daily_energy.mean():.2f} kWh/kW/day")
        print(f"   Capacity Factor: {(self.solar_data['generation_kw_per_kw_installed'].mean() * 100):.1f}%")
        print(f"   Solar Hours/Day: ~{(self.solar_data['generation_kw_per_kw_installed'] > 0.01).sum() / len(daily_energy) / 4:.1f} hours")
        
    def create_load_analysis(self):
        """Generate load profile analysis and visualizations."""
        if not self.load_profiles:
            logger.error("Load profiles not available")
            return
        
        logger.info("Creating load profile analysis...")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Residential Load Profile Analysis\n(20 Households - August 15-21, 2023)', 
                    fontsize=16, fontweight='bold')
        
        # Combine all load profiles for analysis
        all_loads = pd.DataFrame()
        for profile_name, profile_data in self.load_profiles.items():
            all_loads[profile_name] = profile_data['load_kw']
        
        # 1. Individual load profiles (sample)
        ax1 = axes[0, 0]
        sample_profiles = list(self.load_profiles.keys())[:5]  # Show first 5 profiles
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83']
        
        for i, profile_name in enumerate(sample_profiles):
            profile_data = self.load_profiles[profile_name]
            ax1.plot(profile_data.index, profile_data['load_kw'], 
                    linewidth=1, alpha=0.8, color=colors[i], label=profile_name.replace('_', ' ').title())
        
        ax1.set_title('Sample Individual Load Profiles', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Load (kW)')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Average daily pattern
        ax2 = axes[0, 1]
        all_loads['hour'] = all_loads.index.hour
        hourly_avg = all_loads.groupby('hour').mean().mean(axis=1)  # Average across households and hours
        hourly_std = all_loads.groupby('hour').mean().std(axis=1)
        
        ax2.plot(hourly_avg.index, hourly_avg.values, 'o-', 
                linewidth=2, markersize=6, color='#2E86AB', label='Average Load')
        ax2.fill_between(hourly_avg.index, 
                        hourly_avg.values - hourly_std.values,
                        hourly_avg.values + hourly_std.values, 
                        alpha=0.3, color='#2E86AB', label='±1 Std Dev')
        ax2.set_title('Average Daily Load Pattern', fontweight='bold')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Average Load (kW)')
        ax2.set_xticks(range(0, 24, 4))
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Load distribution across households
        ax3 = axes[1, 0]
        household_averages = all_loads.mean(axis=0)
        ax3.hist(household_averages, bins=15, alpha=0.7, color='#2E86AB', 
                edgecolor='black', linewidth=0.5)
        ax3.axvline(household_averages.mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {household_averages.mean():.2f} kW')
        ax3.axvline(household_averages.median(), color='orange', linestyle='--', 
                   linewidth=2, label=f'Median: {household_averages.median():.2f} kW')
        ax3.set_title('Household Average Load Distribution', fontweight='bold')
        ax3.set_xlabel('Average Load (kW)')
        ax3.set_ylabel('Number of Households')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Peak vs off-peak analysis
        ax4 = axes[1, 1]
        peak_hours = [18, 19, 20, 21]  # 6-9 PM
        offpeak_hours = [0, 1, 2, 3, 4, 5]  # Midnight - 6 AM
        
        peak_loads = all_loads[all_loads.index.hour.isin(peak_hours)].mean(axis=0)
        offpeak_loads = all_loads[all_loads.index.hour.isin(offpeak_hours)].mean(axis=0)
        
        x_pos = np.arange(len(peak_loads))
        width = 0.35
        
        bars1 = ax4.bar(x_pos - width/2, peak_loads, width, 
                       label='Peak (6-9 PM)', color='#A23B72', alpha=0.8)
        bars2 = ax4.bar(x_pos + width/2, offpeak_loads, width,
                       label='Off-Peak (12-6 AM)', color='#2E86AB', alpha=0.8)
        
        ax4.set_title('Peak vs Off-Peak Load Comparison', fontweight='bold')
        ax4.set_xlabel('Household')
        ax4.set_ylabel('Average Load (kW)')
        ax4.set_xticks(x_pos[::4])  # Show every 4th household
        ax4.set_xticklabels([f'HH{i+1}' for i in range(0, len(peak_loads), 4)])
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('vpp_load_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print summary statistics
        print("\n" + "="*60)
        print("🏠 LOAD PROFILE SUMMARY STATISTICS")
        print("="*60)
        print(f"📊 Load Statistics:")
        print(f"   Households: {len(self.load_profiles)}")
        print(f"   Average Load: {household_averages.mean():.2f} kW")
        print(f"   Load Range: {household_averages.min():.2f} - {household_averages.max():.2f} kW")
        print(f"   Peak Hour Load: {peak_loads.mean():.2f} kW (6-9 PM)")
        print(f"   Off-Peak Load: {offpeak_loads.mean():.2f} kW (12-6 AM)")
        print(f"   Peak/Off-Peak Ratio: {peak_loads.mean()/offpeak_loads.mean():.1f}x")
        print(f"   Total Portfolio: {household_averages.sum():.1f} kW")
        
    def create_integrated_analysis(self):
        """Create integrated analysis showing market, solar, and load interactions."""
        if self.market_data is None or self.solar_data is None or not self.load_profiles:
            logger.error("Some data not available for integrated analysis")
            return
        
        logger.info("Creating integrated VPP analysis...")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Integrated VPP Analysis\n(Market Prices vs Solar Generation vs Load)', 
                    fontsize=16, fontweight='bold')
        
        # Combine all load profiles
        all_loads = pd.DataFrame()
        for profile_name, profile_data in self.load_profiles.items():
            all_loads[profile_name] = profile_data['load_kw']
        total_load = all_loads.sum(axis=1)
        
        # 1. Market prices vs solar generation
        ax1 = axes[0, 0]
        ax1_twin = ax1.twinx()
        
        # Plot market prices
        ax1.plot(self.market_data.index, self.market_data['lmp'], 
                color='#2E86AB', linewidth=1.5, label='LMP', alpha=0.8)
        ax1.set_ylabel('LMP ($/MWh)', color='#2E86AB')
        ax1.tick_params(axis='y', labelcolor='#2E86AB')
        
        # Plot solar generation
        solar_kw = self.solar_data['generation_kw_per_kw_installed'] * 50  # Assume 50kW total solar
        ax1_twin.fill_between(self.solar_data.index, solar_kw, 
                             alpha=0.3, color='#F18F01', label='Solar (50kW system)')
        ax1_twin.set_ylabel('Solar Generation (kW)', color='#F18F01')
        ax1_twin.tick_params(axis='y', labelcolor='#F18F01')
        
        ax1.set_title('Market Prices vs Solar Generation', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.grid(True, alpha=0.3)
        
        # Add legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # 2. Net load analysis (load - solar)
        ax2 = axes[0, 1]
        net_load = total_load - solar_kw
        
        ax2.plot(total_load.index, total_load, linewidth=1.5, 
                color='#A23B72', label='Total Load', alpha=0.8)
        ax2.plot(solar_kw.index, solar_kw, linewidth=1.5, 
                color='#F18F01', label='Solar Generation', alpha=0.8)
        ax2.plot(net_load.index, net_load, linewidth=1.5, 
                color='#2E86AB', label='Net Load', alpha=0.8)
        ax2.fill_between(net_load.index, net_load, alpha=0.3, color='#2E86AB')
        
        ax2.set_title('Load vs Solar vs Net Load', fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Power (kW)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Daily patterns comparison
        ax3 = axes[1, 0]
        
        # Calculate hourly averages for all data
        market_hourly = self.market_data.groupby(self.market_data.index.hour)['lmp'].mean()
        solar_hourly = self.solar_data.groupby(self.solar_data.index.hour)['generation_kw_per_kw_installed'].mean() * 50
        load_hourly = total_load.groupby(total_load.index.hour).mean()
        
        # Normalize for comparison (0-1 scale)
        market_norm = (market_hourly - market_hourly.min()) / (market_hourly.max() - market_hourly.min())
        solar_norm = solar_hourly / solar_hourly.max()
        load_norm = (load_hourly - load_hourly.min()) / (load_hourly.max() - load_hourly.min())
        
        ax3.plot(market_norm.index, market_norm.values, 'o-', 
                linewidth=2, markersize=6, color='#2E86AB', label='Market Prices (normalized)')
        ax3.plot(solar_norm.index, solar_norm.values, 's-', 
                linewidth=2, markersize=4, color='#F18F01', label='Solar Generation (normalized)')
        ax3.plot(load_norm.index, load_norm.values, '^-', 
                linewidth=2, markersize=4, color='#A23B72', label='Load (normalized)')
        
        ax3.set_title('Normalized Daily Patterns Comparison', fontweight='bold')
        ax3.set_xlabel('Hour of Day')
        ax3.set_ylabel('Normalized Value (0-1)')
        ax3.set_xticks(range(0, 24, 4))
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Value analysis (solar production value)
        ax4 = axes[1, 1]
        solar_value_hourly = (self.solar_data['generation_kw_per_kw_installed'] * 50 * 
                             self.market_data['lmp'] / 1000)  # $/hour for 50kW system
        
        daily_value = solar_value_hourly.groupby(solar_value_hourly.index.date).sum()
        
        bars = ax4.bar(range(len(daily_value)), daily_value.values, 
                      color='#F18F01', alpha=0.8, edgecolor='black', linewidth=0.5)
        ax4.set_title('Daily Solar Revenue (50kW System)', fontweight='bold')
        ax4.set_xlabel('Day')
        ax4.set_ylabel('Revenue ($/day)')
        ax4.set_xticks(range(len(daily_value)))
        ax4.set_xticklabels([f'Day {i+1}' for i in range(len(daily_value))])
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, daily_value.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'${value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('vpp_integrated_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print integrated analysis summary
        print("\n" + "="*60)
        print("🔄 INTEGRATED VPP ANALYSIS SUMMARY")
        print("="*60)
        print(f"⚖️ Supply-Demand Balance:")
        print(f"   Total Load Portfolio: {total_load.mean():.1f} kW average")
        print(f"   Solar Capacity (50kW): {solar_kw.mean():.1f} kW average generation")
        print(f"   Net Load: {net_load.mean():.1f} kW average")
        print(f"   Solar Penetration: {(solar_kw.mean()/total_load.mean()*100):.1f}%")
        
        print(f"\n💰 Economic Analysis (50kW Solar System):")
        print(f"   Daily Revenue: ${daily_value.mean():.2f}/day average")
        print(f"   Weekly Revenue: ${daily_value.sum():.2f}")
        print(f"   Revenue/kW: ${daily_value.sum()/50:.2f}/kW/week")
        
        print(f"\n⏰ Timing Analysis:")
        peak_solar_hour = solar_hourly.idxmax()
        peak_price_hour = market_hourly.idxmax()
        peak_load_hour = load_hourly.idxmax()
        print(f"   Peak Solar: {peak_solar_hour}:00")
        print(f"   Peak Price: {peak_price_hour}:00")
        print(f"   Peak Load: {peak_load_hour}:00")
        print(f"   Solar-Price Alignment: {'Good' if abs(peak_solar_hour - peak_price_hour) <= 2 else 'Poor'}")
    
    def generate_complete_dashboard(self):
        """Generate all analysis charts and summaries."""
        logger.info("🚀 Generating Complete VPP Data Dashboard...")
        
        print("\n" + "="*80)
        print("🎯 VPP LLM AGENT - DATA DASHBOARD")
        print("="*80)
        print("📅 Dataset: CAISO Market Data | August 15-21, 2023")
        print("📍 Location: Los Angeles, CA (34.05°N, -118.24°W)")
        print("⏱️  Resolution: 15-minute intervals")
        print("🏠 Portfolio: 20 residential households + solar generation")
        
        try:
            # Generate all analyses
            self.create_market_analysis()
            self.create_solar_analysis()
            self.create_load_analysis()
            self.create_integrated_analysis()
            
            print("\n" + "="*80)
            print("✅ DASHBOARD GENERATION COMPLETE")
            print("="*80)
            print("📊 Generated Charts:")
            print("   • vpp_market_analysis.png - Market price analysis")
            print("   • vpp_solar_analysis.png - Solar generation analysis")
            print("   • vpp_load_analysis.png - Load profile analysis")
            print("   • vpp_integrated_analysis.png - Integrated VPP analysis")
            print("\n💡 Dashboard provides comprehensive insights for VPP operations!")
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            raise

def main():
    """Main execution function."""
    dashboard = VPPDataDashboard()
    dashboard.generate_complete_dashboard()

if __name__ == "__main__":
    main()
