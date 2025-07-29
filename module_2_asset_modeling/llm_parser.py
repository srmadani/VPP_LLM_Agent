"""
LLM Parser for VPP LLM Agent - Module 2

This module uses the Gemini API to parse natural language descriptions
of prosumers and convert them to structured configuration dictionaries.
"""

import os
import json
import re
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv


class LLMProsumerParser:
    """
    Uses Gemini API to parse natural language prosumer descriptions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM parser with Gemini API.
        
        Args:
            api_key: Gemini API key (if not provided, loads from .env)
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in .env file")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Define the system prompt for parsing prosumer descriptions
        self.system_prompt = """
You are an expert system for parsing natural language descriptions of residential energy prosumers into structured configuration data.

Your task is to extract technical specifications and preferences from text descriptions and convert them into a standardized JSON format.

## Output Format
Return a JSON object with the following structure:

```json
{
    "bess_capacity_kwh": <float or null>,
    "bess_max_power_kw": <float or null>,
    "bess_initial_soc_percent": <float between 0-100>,
    "has_ev": <boolean>,
    "ev_battery_capacity_kwh": <float or null>,
    "ev_max_charge_power_kw": <float or null>,
    "ev_charge_deadline": <string "HH:MM" or null>,
    "ev_target_soc_percent": <float between 0-100>,
    "has_solar": <boolean>,
    "solar_capacity_kw": <float or null>,
    "solar_efficiency": <float between 0-1>,
    "participation_willingness": <float between 0-1>,
    "min_compensation_per_kwh": <float>,
    "backup_power_hours": <float>,
    "max_discharge_percent": <float between 0-100>,
    "ev_priority": <string: "low", "medium", or "high">
}
```

## Parsing Guidelines

### Battery Energy Storage System (BESS):
- Common residential sizes: 5kWh (small), 10kWh (medium), 13.5kWh (Tesla Powerwall), 16kWh (large), 20kWh+ (very large)
- Power ratings typically 3-10kW
- If no battery mentioned, set capacity and power to null
- Initial SOC: assume 50% unless specified

### Electric Vehicle (EV):
- Common capacities: 40kWh (Nissan Leaf), 64kWh (Chevy Bolt), 75kWh (Tesla Model 3), 82kWh (Model Y), 100kWh (Model S)
- Charging power: typically 7.2-11.5kW for home charging
- Departure times: usually 6:00-9:00 AM for work commute
- Target SOC: typically 80-90% for daily driving

### Solar PV:
- Common residential sizes: 4kW (small), 6kW (medium), 8kW (large), 10kW+ (very large)
- Efficiency: typically 0.80-0.90 for modern systems
- If no solar mentioned, set has_solar to false and capacity to null

### User Preferences:
- Conservative users: low participation (0.3-0.6), high compensation needs ($0.20-0.35/kWh), long backup requirements (6-12h)
- Moderate users: medium participation (0.6-0.8), reasonable compensation ($0.12-0.25/kWh), moderate backup (3-8h)
- Aggressive users: high participation (0.8-0.95), low compensation needs ($0.08-0.18/kWh), short backup (1-4h)
- EV priority: "high" if mentioned as essential, "medium" for normal use, "low" if flexible

### Keywords to look for:
- BESS: "battery", "storage", "Powerwall", "backup power", "energy storage"
- EV: "electric vehicle", "EV", "Tesla", "Nissan Leaf", "Chevy Bolt", "car charging"
- Solar: "solar", "panels", "PV", "photovoltaic", "rooftop"
- Preferences: "conservative", "risk-averse", "aggressive", "tech-savvy", "flexible", "essential", "backup"

## Examples:

Input: "A tech-savvy user with a large 15kWh battery and an EV that must be charged by 7 AM."
Output:
```json
{
    "bess_capacity_kwh": 15.0,
    "bess_max_power_kw": 7.5,
    "bess_initial_soc_percent": 50.0,
    "has_ev": true,
    "ev_battery_capacity_kwh": 75.0,
    "ev_max_charge_power_kw": 11.0,
    "ev_charge_deadline": "07:00",
    "ev_target_soc_percent": 90.0,
    "has_solar": false,
    "solar_capacity_kw": null,
    "solar_efficiency": 0.85,
    "participation_willingness": 0.85,
    "min_compensation_per_kwh": 0.12,
    "backup_power_hours": 3.0,
    "max_discharge_percent": 70.0,
    "ev_priority": "high"
}
```

Input: "Conservative homeowner with Tesla Powerwall and 8kW solar system, needs reliable backup power"
Output:
```json
{
    "bess_capacity_kwh": 13.5,
    "bess_max_power_kw": 7.0,
    "bess_initial_soc_percent": 50.0,
    "has_ev": false,
    "ev_battery_capacity_kwh": null,
    "ev_max_charge_power_kw": null,
    "ev_charge_deadline": null,
    "ev_target_soc_percent": 80.0,
    "has_solar": true,
    "solar_capacity_kw": 8.0,
    "solar_efficiency": 0.85,
    "participation_willingness": 0.45,
    "min_compensation_per_kwh": 0.25,
    "backup_power_hours": 8.0,
    "max_discharge_percent": 40.0,
    "ev_priority": "medium"
}
```

Parse the following description and return only the JSON object:
"""

    def text_to_prosumer_config(self, description: str) -> Dict[str, Any]:
        """
        Convert natural language prosumer description to structured config.
        
        Args:
            description: Natural language description of prosumer
            
        Returns:
            Dict: Structured prosumer configuration
        """
        try:
            # Construct the full prompt
            full_prompt = self.system_prompt + f"\n\nDescription: {description}"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle case where model adds extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = response_text
            
            # Parse JSON
            config = json.loads(json_str)
            
            # Validate and clean the configuration
            cleaned_config = self._validate_and_clean_config(config)
            
            return cleaned_config
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response_text}")
            # Return default configuration on parse error
            return self._get_default_config()
        
        except Exception as e:
            print(f"Error in LLM parsing: {e}")
            return self._get_default_config()
    
    def _validate_and_clean_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the parsed configuration.
        
        Args:
            config: Raw configuration from LLM
            
        Returns:
            Dict: Cleaned and validated configuration
        """
        # Define expected fields with defaults
        defaults = {
            "bess_capacity_kwh": None,
            "bess_max_power_kw": None,
            "bess_initial_soc_percent": 50.0,
            "has_ev": False,
            "ev_battery_capacity_kwh": None,
            "ev_max_charge_power_kw": None,
            "ev_charge_deadline": None,
            "ev_target_soc_percent": 80.0,
            "has_solar": False,
            "solar_capacity_kw": None,
            "solar_efficiency": 0.85,
            "participation_willingness": 0.7,
            "min_compensation_per_kwh": 0.15,
            "backup_power_hours": 4.0,
            "max_discharge_percent": 60.0,
            "ev_priority": "medium"
        }
        
        # Start with defaults and update with parsed values
        cleaned = defaults.copy()
        
        for key, value in config.items():
            if key in defaults:
                # Handle null values
                if value == "null" or value == "" or value is None:
                    cleaned[key] = None
                else:
                    cleaned[key] = value
        
        # Validation and constraint enforcement
        if cleaned["bess_capacity_kwh"] is not None:
            cleaned["bess_capacity_kwh"] = max(1.0, min(50.0, float(cleaned["bess_capacity_kwh"])))
            
            # Auto-calculate power if not provided
            if cleaned["bess_max_power_kw"] is None:
                cleaned["bess_max_power_kw"] = cleaned["bess_capacity_kwh"] * 0.5  # 0.5C rate
            else:
                cleaned["bess_max_power_kw"] = max(1.0, min(20.0, float(cleaned["bess_max_power_kw"])))
        
        if cleaned["ev_battery_capacity_kwh"] is not None:
            cleaned["has_ev"] = True
            cleaned["ev_battery_capacity_kwh"] = max(20.0, min(150.0, float(cleaned["ev_battery_capacity_kwh"])))
            
            if cleaned["ev_max_charge_power_kw"] is None:
                cleaned["ev_max_charge_power_kw"] = 11.0  # Standard home charging
            else:
                cleaned["ev_max_charge_power_kw"] = max(3.0, min(22.0, float(cleaned["ev_max_charge_power_kw"])))
        
        if cleaned["solar_capacity_kw"] is not None:
            cleaned["has_solar"] = True
            cleaned["solar_capacity_kw"] = max(1.0, min(30.0, float(cleaned["solar_capacity_kw"])))
        
        # Constrain percentage values
        cleaned["bess_initial_soc_percent"] = max(10.0, min(90.0, float(cleaned["bess_initial_soc_percent"])))
        cleaned["ev_target_soc_percent"] = max(50.0, min(100.0, float(cleaned["ev_target_soc_percent"])))
        cleaned["participation_willingness"] = max(0.1, min(1.0, float(cleaned["participation_willingness"])))
        cleaned["max_discharge_percent"] = max(10.0, min(90.0, float(cleaned["max_discharge_percent"])))
        cleaned["solar_efficiency"] = max(0.7, min(0.95, float(cleaned["solar_efficiency"])))
        
        # Constrain financial values
        cleaned["min_compensation_per_kwh"] = max(0.05, min(0.50, float(cleaned["min_compensation_per_kwh"])))
        cleaned["backup_power_hours"] = max(0.5, min(24.0, float(cleaned["backup_power_hours"])))
        
        # Validate string values
        if cleaned["ev_priority"] not in ["low", "medium", "high"]:
            cleaned["ev_priority"] = "medium"
        
        # Validate time format for EV deadline
        if cleaned["ev_charge_deadline"] is not None:
            time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
            if not re.match(time_pattern, str(cleaned["ev_charge_deadline"])):
                cleaned["ev_charge_deadline"] = "07:00"  # Default to 7 AM
        
        return cleaned
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return a default prosumer configuration."""
        return {
            "bess_capacity_kwh": 10.0,
            "bess_max_power_kw": 5.0,
            "bess_initial_soc_percent": 50.0,
            "has_ev": False,
            "ev_battery_capacity_kwh": None,
            "ev_max_charge_power_kw": None,
            "ev_charge_deadline": None,
            "ev_target_soc_percent": 80.0,
            "has_solar": False,
            "solar_capacity_kw": None,
            "solar_efficiency": 0.85,
            "participation_willingness": 0.7,
            "min_compensation_per_kwh": 0.15,
            "backup_power_hours": 4.0,
            "max_discharge_percent": 60.0,
            "ev_priority": "medium"
        }
    
    def batch_parse(self, descriptions: list[str]) -> list[Dict[str, Any]]:
        """
        Parse multiple prosumer descriptions in batch.
        
        Args:
            descriptions: List of natural language descriptions
            
        Returns:
            List of parsed configurations
        """
        configs = []
        for i, description in enumerate(descriptions):
            print(f"Parsing description {i+1}/{len(descriptions)}")
            config = self.text_to_prosumer_config(description)
            configs.append(config)
        
        return configs


def main():
    """Example usage of the LLM parser."""
    parser = LLMProsumerParser()
    
    # Test descriptions
    test_descriptions = [
        "A tech-savvy user with a large 15kWh battery and an EV that must be charged by 7 AM.",
        "Conservative homeowner with Tesla Powerwall and 8kW solar system, needs reliable backup power",
        "Apartment resident with just a Chevy Bolt EV, very flexible with charging times",
        "Suburban family with 6kW solar, 10kWh battery, and Tesla Model 3, moderate risk tolerance",
        "Early adopter with 20kWh battery system, 12kW solar array, and two EVs, wants maximum grid participation"
    ]
    
    print("Testing LLM Prosumer Parser:")
    print("=" * 60)
    
    for i, description in enumerate(test_descriptions, 1):
        print(f"\nTest {i}: {description}")
        print("-" * 40)
        
        config = parser.text_to_prosumer_config(description)
        
        # Pretty print the result
        for key, value in config.items():
            print(f"{key}: {value}")
    
    # Test batch parsing
    print(f"\n\nBatch parsing {len(test_descriptions)} descriptions...")
    configs = parser.batch_parse(test_descriptions)
    print(f"Successfully parsed {len(configs)} configurations")


if __name__ == "__main__":
    main()
