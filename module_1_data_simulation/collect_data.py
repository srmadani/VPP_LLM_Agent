"""
VPP Agent PoC - Module 1: Data & Simulation Environment
Data collection script for CAISO market data, NREL solar data, and load profiles.
"""

import os
import sys
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Tuple
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VPPDataCollector:
    """Main class for collecting all VPP simulation data."""
    
    def __init__(self, config: Dict):
        """Initialize the data collector with configuration."""
        self.config = config
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.load_profiles_dir = self.data_dir / "load_profiles"
        self.load_profiles_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv(dotenv_path="../.env")
        self.nrel_api_key = os.getenv("NREL_API_KEY")
        
        if not self.nrel_api_key or self.nrel_api_key == "your_nrel_api_key_here":
            logger.warning("NREL API key not set. Some features may not work.")
    
    def fetch_caiso_market_data(self) -> pd.DataFrame:
        """Fetch CAISO market data using gridstatus library."""
        logger.info("Fetching CAISO market data...")
        
        try:
            import gridstatus
            
            # Initialize CAISO client
            caiso = gridstatus.CAISO()
            
            # Parse dates
            start_date = datetime.strptime(self.config["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(self.config["end_date"], "%Y-%m-%d")
            
            # Fetch LMP data
            logger.info("Fetching LMP data...")
            lmp_data = caiso.get_lmp(
                start=start_date,
                end=end_date,
                market="DAM",  # Day-Ahead Market
                locations=["TH_NP15_GEN-APND"]  # NP15 trading hub
            )
            
            # Fetch ancillary services data
            logger.info("Fetching ancillary services data...")
            as_data = caiso.get_as_prices(
                start=start_date,
                end=end_date,
                market="DAM"
            )
            
            # Process LMP data
            lmp_df = pd.DataFrame(lmp_data)
            if not lmp_df.empty:
                lmp_df = lmp_df[lmp_df['Location'] == 'TH_NP15_GEN-APND']
                lmp_df = lmp_df[['Time', 'LMP']].rename(columns={'Time': 'timestamp', 'LMP': 'lmp'})
                lmp_df['timestamp'] = pd.to_datetime(lmp_df['timestamp'])
            
            # Process ancillary services data
            as_df = pd.DataFrame(as_data)
            spin_df = as_df[as_df['Product'] == 'SPIN'][['Time', 'Price']].rename(
                columns={'Time': 'timestamp', 'Price': 'spin_price'}
            )
            nonspin_df = as_df[as_df['Product'] == 'NONSPIN'][['Time', 'Price']].rename(
                columns={'Time': 'timestamp', 'Price': 'nonspin_price'}
            )
            
            # Merge all market data
            market_df = lmp_df
            if not spin_df.empty:
                market_df = market_df.merge(spin_df, on='timestamp', how='left')
            if not nonspin_df.empty:
                market_df = market_df.merge(nonspin_df, on='timestamp', how='left')
            
            # Fill missing values with reasonable defaults
            market_df['spin_price'] = market_df['spin_price'].fillna(market_df['lmp'] * 0.15)
            market_df['nonspin_price'] = market_df['nonspin_price'].fillna(market_df['lmp'] * 0.10)
            
            # Convert to 15-minute intervals
            market_df = self._resample_to_15min(market_df)
            
            logger.info(f"Successfully fetched {len(market_df)} market data points")
            return market_df
            
        except Exception as e:
            logger.error(f"Error fetching CAISO data: {e}")
            # Generate synthetic market data as fallback
            return self._generate_synthetic_market_data()
    
    def fetch_solar_data(self) -> pd.DataFrame:
        """Fetch solar generation data from NREL PVWatts API."""
        logger.info("Fetching solar generation data...")
        
        if not self.nrel_api_key or self.nrel_api_key == "your_nrel_api_key_here":
            logger.warning("NREL API key not available. Generating synthetic solar data.")
            return self._generate_synthetic_solar_data()
        
        try:
            # PVWatts API endpoint
            url = "https://developer.nrel.gov/api/pvwatts/v8.json"
            
            # System configurations for different sizes
            system_sizes = [4, 7, 10]  # kW
            all_solar_data = []
            
            for size in system_sizes:
                params = {
                    'api_key': self.nrel_api_key,
                    'lat': self.config["latitude"],
                    'lon': self.config["longitude"],
                    'system_capacity': size,
                    'azimuth': 180,  # South-facing
                    'tilt': 20,      # Optimal for California
                    'array_type': 1,  # Fixed - Open Rack
                    'module_type': 1, # Standard
                    'losses': 14,     # System losses
                    'dataset': 'tmy3',
                    'timeframe': 'hourly'
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if 'outputs' in data:
                    hourly_ac = data['outputs']['ac']
                    all_solar_data.extend(hourly_ac)
            
            # Create normalized solar profile (per kW installed)
            if all_solar_data:
                avg_generation = np.mean(np.array(all_solar_data).reshape(-1, len(system_sizes)), axis=1)
                normalized_generation = avg_generation / np.mean(system_sizes)  # Per kW
                
                # Create timestamp series for a full year, then extract our target period
                start_year = datetime.strptime(self.config["start_date"], "%Y-%m-%d").year
                timestamps = pd.date_range(
                    start=f"{start_year}-01-01",
                    periods=8760,
                    freq='h'
                )
                
                solar_df = pd.DataFrame({
                    'timestamp': timestamps,
                    'generation_kw_per_kw_installed': normalized_generation / 1000  # Convert W to kW
                })
                
                # Filter to target period and convert to 15-minute intervals
                start_date = pd.to_datetime(self.config["start_date"])
                end_date = pd.to_datetime(self.config["end_date"]) + timedelta(days=1)
                
                solar_df = solar_df[
                    (solar_df['timestamp'] >= start_date) & 
                    (solar_df['timestamp'] < end_date)
                ]
                
                # Ensure we have the exact timestamps as market data by resampling
                target_timestamps = pd.date_range(start=start_date, end=end_date, freq='15min')[:-1]
                solar_df = solar_df.set_index('timestamp').reindex(target_timestamps, method='ffill').reset_index()
                solar_df.columns = ['timestamp', 'generation_kw_per_kw_installed']
                
                logger.info(f"Successfully fetched {len(solar_df)} solar data points")
                return solar_df
            
        except Exception as e:
            logger.error(f"Error fetching solar data: {e}")
        
        # Fallback to synthetic data
        return self._generate_synthetic_solar_data()
    
    def generate_load_profiles(self) -> None:
        """Generate residential load profiles."""
        logger.info("Generating residential load profiles...")
        
        # Generate 200 diverse residential load profiles to support scaled fleet
        num_profiles = 200
        
        start_date = pd.to_datetime(self.config["start_date"])
        end_date = pd.to_datetime(self.config["end_date"]) + timedelta(days=1)
        timestamps = pd.date_range(start=start_date, end=end_date, freq='15min')[:-1]
        
        for i in range(1, num_profiles + 1):
            load_profile = self._generate_single_load_profile(timestamps, profile_id=i)
            
            profile_df = pd.DataFrame({
                'timestamp': timestamps,
                'load_kw': load_profile
            })
            
            # Save individual profile
            profile_path = self.load_profiles_dir / f"profile_{i}.csv"
            profile_df.to_csv(profile_path, index=False)
            
        logger.info(f"Generated {num_profiles} load profiles")
    
    def _generate_single_load_profile(self, timestamps: pd.DatetimeIndex, profile_id: int) -> np.ndarray:
        """Generate a single realistic residential load profile."""
        np.random.seed(profile_id)  # For reproducibility
        
        # Base load characteristics
        base_load = 0.5 + np.random.normal(0, 0.1)  # 0.3-0.7 kW base load
        
        # Daily pattern coefficients
        morning_peak = 1.5 + np.random.normal(0, 0.3)  # 6-9 AM
        evening_peak = 2.0 + np.random.normal(0, 0.4)  # 6-10 PM
        
        load_profile = []
        
        for ts in timestamps:
            hour = ts.hour
            minute = ts.minute
            day_of_week = ts.weekday()
            
            # Base load
            load = base_load
            
            # Daily patterns
            if 6 <= hour <= 9:  # Morning peak
                load += morning_peak * np.exp(-((hour - 7.5) ** 2) / 2)
            elif 18 <= hour <= 22:  # Evening peak
                load += evening_peak * np.exp(-((hour - 20) ** 2) / 4)
            elif 22 <= hour or hour <= 6:  # Night/early morning
                load *= 0.6
            
            # Weekend patterns (slightly different)
            if day_of_week >= 5:  # Weekend
                if 8 <= hour <= 11:  # Late morning
                    load += 0.5 * morning_peak
                if 12 <= hour <= 14:  # Afternoon
                    load += 0.3 * evening_peak
            
            # Add some randomness
            load += np.random.normal(0, 0.1)
            
            # Ensure non-negative
            load = max(0.1, load)
            
            load_profile.append(load)
        
        return np.array(load_profile)
    
    def _resample_to_15min(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert data to 15-minute intervals."""
        df = df.copy()
        df.set_index('timestamp', inplace=True)
        
        # Resample to 15-minute intervals
        df_resampled = df.resample('15min').mean()
        
        # Forward fill any NaN values
        df_resampled = df_resampled.ffill()
        
        # Reset index
        df_resampled.reset_index(inplace=True)
        
        return df_resampled
    
    def _generate_synthetic_market_data(self) -> pd.DataFrame:
        """Generate synthetic market data as fallback."""
        logger.info("Generating synthetic market data...")
        
        start_date = pd.to_datetime(self.config["start_date"])
        end_date = pd.to_datetime(self.config["end_date"]) + timedelta(days=1)
        timestamps = pd.date_range(start=start_date, end=end_date, freq='15min')[:-1]
        
        # Generate realistic price patterns
        base_lmp = 50.0
        lmp_values = []
        
        for ts in timestamps:
            hour = ts.hour
            day_of_week = ts.weekday()
            
            # Base price with daily pattern
            price = base_lmp
            
            # Peak hours (higher prices)
            if 16 <= hour <= 20:  # Evening peak
                price *= 1.8
            elif 6 <= hour <= 10:  # Morning ramp
                price *= 1.4
            elif 22 <= hour or hour <= 6:  # Off-peak
                price *= 0.7
            
            # Weekend discount
            if day_of_week >= 5:
                price *= 0.85
            
            # Add volatility
            price += np.random.normal(0, price * 0.1)
            
            lmp_values.append(max(price, 10.0))  # Floor price
        
        market_df = pd.DataFrame({
            'timestamp': timestamps,
            'lmp': lmp_values,
            'spin_price': [lmp * 0.15 for lmp in lmp_values],
            'nonspin_price': [lmp * 0.10 for lmp in lmp_values]
        })
        
        return market_df
    
    def _generate_synthetic_solar_data(self) -> pd.DataFrame:
        """Generate synthetic solar data as fallback."""
        logger.info("Generating synthetic solar data...")
        
        start_date = pd.to_datetime(self.config["start_date"])
        end_date = pd.to_datetime(self.config["end_date"]) + timedelta(days=1)
        timestamps = pd.date_range(start=start_date, end=end_date, freq='15min')[:-1]
        
        solar_values = []
        
        for ts in timestamps:
            hour = ts.hour + ts.minute / 60.0
            
            # Simple solar model - bell curve during daylight hours
            if 6 <= hour <= 19:
                # Peak at solar noon (13:00)
                solar_factor = np.exp(-((hour - 13) ** 2) / 25)
                # Add some cloud variability
                cloud_factor = 0.8 + 0.2 * np.random.random()
                generation = solar_factor * cloud_factor
            else:
                generation = 0.0
            
            solar_values.append(max(generation, 0.0))
        
        solar_df = pd.DataFrame({
            'timestamp': timestamps,
            'generation_kw_per_kw_installed': solar_values
        })
        
        return solar_df
    
    def save_data(self, market_df: pd.DataFrame, solar_df: pd.DataFrame) -> None:
        """Save all collected data to CSV files."""
        logger.info("Saving data to CSV files...")
        
        # Save market data
        market_path = self.data_dir / "market_data.csv"
        market_df.to_csv(market_path, index=False)
        logger.info(f"Market data saved to {market_path}")
        
        # Save solar data
        solar_path = self.data_dir / "solar_data.csv"
        solar_df.to_csv(solar_path, index=False)
        logger.info(f"Solar data saved to {solar_path}")
    
    def validate_data(self) -> bool:
        """Validate all generated data."""
        logger.info("Validating generated data...")
        
        try:
            # Check market data
            market_df = pd.read_csv(self.data_dir / "market_data.csv")
            assert len(market_df) > 0, "Market data is empty"
            assert all(col in market_df.columns for col in ['timestamp', 'lmp', 'spin_price', 'nonspin_price'])
            
            # Check solar data
            solar_df = pd.read_csv(self.data_dir / "solar_data.csv")
            assert len(solar_df) > 0, "Solar data is empty"
            assert all(col in solar_df.columns for col in ['timestamp', 'generation_kw_per_kw_installed'])
            
            # Check load profiles
            load_files = list(self.load_profiles_dir.glob("profile_*.csv"))
            assert len(load_files) > 0, "No load profiles generated"
            
            # Validate a sample load profile
            sample_profile = pd.read_csv(load_files[0])
            assert all(col in sample_profile.columns for col in ['timestamp', 'load_kw'])
            
            logger.info("Data validation successful!")
            return True
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return False

def main():
    """Main execution function."""
    
    # Configuration - Extended to full month for realistic simulation
    config = {
        "start_date": "2023-08-01",
        "end_date": "2023-08-31",
        "latitude": 34.05,
        "longitude": -118.24
    }
    
    logger.info("Starting VPP Data Collection Process...")
    logger.info(f"Target period: {config['start_date']} to {config['end_date']}")
    logger.info(f"Target location: {config['latitude']}, {config['longitude']}")
    
    # Initialize collector
    collector = VPPDataCollector(config)
    
    try:
        # Collect all data
        market_data = collector.fetch_caiso_market_data()
        solar_data = collector.fetch_solar_data()
        collector.generate_load_profiles()
        
        # Save data
        collector.save_data(market_data, solar_data)
        
        # Validate results
        if collector.validate_data():
            logger.info("✅ Data collection completed successfully!")
            
            # Print summary statistics
            print("\n" + "="*50)
            print("DATA COLLECTION SUMMARY")
            print("="*50)
            print(f"Market data points: {len(market_data)}")
            print(f"Solar data points: {len(solar_data)}")
            print(f"Load profiles generated: {len(list(collector.load_profiles_dir.glob('profile_*.csv')))}")
            print(f"Time range: {market_data['timestamp'].min()} to {market_data['timestamp'].max()}")
            print("\nSample market data:")
            print(market_data.head())
            print("\nSample solar data:")
            print(solar_data.head())
            
        else:
            logger.error("❌ Data validation failed!")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Data collection failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
