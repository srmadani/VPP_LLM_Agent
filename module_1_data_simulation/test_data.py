"""
Test script for Module 1: Data & Simulation Environment
Validates the data collection functionality and output formats.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_integrity():
    """Test that all required data files exist and have correct format."""
    logger.info("Testing data integrity...")
    
    data_dir = Path("data")
    errors = []
    
    # Test market data
    market_file = data_dir / "market_data.csv"
    if market_file.exists():
        try:
            market_df = pd.read_csv(market_file)
            required_cols = ['timestamp', 'lmp', 'spin_price', 'nonspin_price']
            
            if not all(col in market_df.columns for col in required_cols):
                errors.append(f"Market data missing required columns: {required_cols}")
            
            if len(market_df) == 0:
                errors.append("Market data is empty")
            
            # Check timestamp format
            market_df['timestamp'] = pd.to_datetime(market_df['timestamp'])
            
            # Check price values are reasonable
            if market_df['lmp'].min() < 0:
                errors.append("Market data contains negative LMP values")
            
            logger.info(f"✅ Market data: {len(market_df)} records")
            
        except Exception as e:
            errors.append(f"Error reading market data: {e}")
    else:
        errors.append("Market data file not found")
    
    # Test solar data
    solar_file = data_dir / "solar_data.csv"
    if solar_file.exists():
        try:
            solar_df = pd.read_csv(solar_file)
            required_cols = ['timestamp', 'generation_kw_per_kw_installed']
            
            if not all(col in solar_df.columns for col in required_cols):
                errors.append(f"Solar data missing required columns: {required_cols}")
            
            if len(solar_df) == 0:
                errors.append("Solar data is empty")
            
            # Check generation values are reasonable (0-1.2 kW per kW installed)
            gen_values = solar_df['generation_kw_per_kw_installed']
            if gen_values.min() < 0 or gen_values.max() > 1.5:
                errors.append("Solar generation values out of reasonable range")
            
            logger.info(f"✅ Solar data: {len(solar_df)} records")
            
        except Exception as e:
            errors.append(f"Error reading solar data: {e}")
    else:
        errors.append("Solar data file not found")
    
    # Test load profiles
    load_profiles_dir = data_dir / "load_profiles"
    if load_profiles_dir.exists():
        profile_files = list(load_profiles_dir.glob("profile_*.csv"))
        
        if len(profile_files) == 0:
            errors.append("No load profile files found")
        else:
            # Test a few profiles
            for i, profile_file in enumerate(profile_files[:3]):
                try:
                    profile_df = pd.read_csv(profile_file)
                    required_cols = ['timestamp', 'load_kw']
                    
                    if not all(col in profile_df.columns for col in required_cols):
                        errors.append(f"Profile {profile_file.name} missing required columns")
                    
                    if len(profile_df) == 0:
                        errors.append(f"Profile {profile_file.name} is empty")
                    
                    # Check load values are reasonable (0.1-10 kW for residential)
                    load_values = profile_df['load_kw']
                    if load_values.min() < 0 or load_values.max() > 15:
                        errors.append(f"Profile {profile_file.name} has unreasonable load values")
                        
                except Exception as e:
                    errors.append(f"Error reading profile {profile_file.name}: {e}")
            
            logger.info(f"✅ Load profiles: {len(profile_files)} files")
    else:
        errors.append("Load profiles directory not found")
    
    return errors

def test_data_consistency():
    """Test that all data has consistent timestamps and intervals."""
    logger.info("Testing data consistency...")
    
    data_dir = Path("data")
    errors = []
    
    try:
        # Load all data
        market_df = pd.read_csv(data_dir / "market_data.csv")
        solar_df = pd.read_csv(data_dir / "solar_data.csv")
        
        market_df['timestamp'] = pd.to_datetime(market_df['timestamp'])
        solar_df['timestamp'] = pd.to_datetime(solar_df['timestamp'])
        
        # Check if timestamps align
        market_timestamps = set(market_df['timestamp'])
        solar_timestamps = set(solar_df['timestamp'])
        
        if market_timestamps != solar_timestamps:
            errors.append("Market and solar data have different timestamps")
        
        # Check 15-minute intervals
        market_df = market_df.sort_values('timestamp')
        time_diffs = market_df['timestamp'].diff().dropna()
        expected_interval = timedelta(minutes=15)
        
        if not all(diff == expected_interval for diff in time_diffs):
            errors.append("Data is not at consistent 15-minute intervals")
        
        # Test load profile consistency
        load_profiles_dir = data_dir / "load_profiles"
        profile_files = list(load_profiles_dir.glob("profile_*.csv"))
        
        if profile_files:
            sample_profile = pd.read_csv(profile_files[0])
            sample_profile['timestamp'] = pd.to_datetime(sample_profile['timestamp'])
            profile_timestamps = set(sample_profile['timestamp'])
            
            if market_timestamps != profile_timestamps:
                errors.append("Load profiles have different timestamps than market data")
        
        logger.info("✅ Data consistency check completed")
        
    except Exception as e:
        errors.append(f"Error in consistency check: {e}")
    
    return errors

def generate_data_summary():
    """Generate a summary report of the collected data."""
    logger.info("Generating data summary...")
    
    data_dir = Path("data")
    
    try:
        # Load data
        market_df = pd.read_csv(data_dir / "market_data.csv")
        solar_df = pd.read_csv(data_dir / "solar_data.csv")
        
        market_df['timestamp'] = pd.to_datetime(market_df['timestamp'])
        solar_df['timestamp'] = pd.to_datetime(solar_df['timestamp'])
        
        load_profiles_dir = data_dir / "load_profiles"
        profile_files = list(load_profiles_dir.glob("profile_*.csv"))
        
        print("\n" + "="*60)
        print("VPP DATA COLLECTION SUMMARY REPORT")
        print("="*60)
        
        print(f"\n📊 DATASET OVERVIEW")
        print(f"   Time Period: {market_df['timestamp'].min()} to {market_df['timestamp'].max()}")
        print(f"   Duration: {(market_df['timestamp'].max() - market_df['timestamp'].min()).days} days")
        print(f"   Data Points: {len(market_df)} (15-minute intervals)")
        print(f"   Load Profiles: {len(profile_files)} households")
        
        print(f"\n💰 MARKET DATA STATISTICS")
        print(f"   LMP Range: ${market_df['lmp'].min():.2f} - ${market_df['lmp'].max():.2f} /MWh")
        print(f"   LMP Average: ${market_df['lmp'].mean():.2f} /MWh")
        print(f"   Spinning Reserve: ${market_df['spin_price'].mean():.2f} /MWh (avg)")
        print(f"   Non-Spinning Reserve: ${market_df['nonspin_price'].mean():.2f} /MWh (avg)")
        
        print(f"\n☀️ SOLAR DATA STATISTICS")
        print(f"   Peak Generation: {solar_df['generation_kw_per_kw_installed'].max():.3f} kW/kW")
        print(f"   Average Generation: {solar_df['generation_kw_per_kw_installed'].mean():.3f} kW/kW")
        print(f"   Daily Solar Hours: ~{(solar_df['generation_kw_per_kw_installed'] > 0.01).sum() / len(profile_files) / 4:.1f} hours/day")
        
        if profile_files:
            # Analyze load profiles
            sample_loads = []
            for pf in profile_files[:5]:  # Sample first 5 profiles
                load_df = pd.read_csv(pf)
                sample_loads.append(load_df['load_kw'].mean())
            
            print(f"\n🏠 LOAD PROFILE STATISTICS")
            print(f"   Average Household Load: {np.mean(sample_loads):.2f} kW")
            print(f"   Load Range: {np.min(sample_loads):.2f} - {np.max(sample_loads):.2f} kW")
        
        print(f"\n📁 OUTPUT FILES")
        print(f"   ├── data/market_data.csv ({len(market_df)} records)")
        print(f"   ├── data/solar_data.csv ({len(solar_df)} records)")
        print(f"   └── data/load_profiles/ ({len(profile_files)} files)")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")

def main():
    """Run all tests and generate summary."""
    logger.info("Starting Module 1 validation tests...")
    
    # Test data integrity
    integrity_errors = test_data_integrity()
    
    # Test data consistency
    consistency_errors = test_data_consistency()
    
    # Combine all errors
    all_errors = integrity_errors + consistency_errors
    
    if all_errors:
        logger.error("❌ Validation failed with errors:")
        for error in all_errors:
            logger.error(f"   - {error}")
        return 1
    else:
        logger.info("✅ All validation tests passed!")
        generate_data_summary()
        return 0

if __name__ == "__main__":
    exit(main())
