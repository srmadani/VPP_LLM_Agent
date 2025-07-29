"""
Prosumer Parser Example for Dashboard

This script demonstrates how the natural language prosumer parser
integrates with the dashboard functionality.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent / "module_2_asset_modeling"))

def test_prosumer_parser():
    """Test the prosumer parser with sample descriptions."""
    try:
        from llm_parser import LLMProsumerParser
        
        # Initialize parser
        parser = LLMProsumerParser()
        
        # Sample descriptions to test
        test_descriptions = [
            "Tech-savvy homeowner with a 13.5kWh Tesla Powerwall and Model 3",
            "Environmentally conscious family with 8kW rooftop solar and small battery",
            "Senior citizen needing reliable backup power for medical equipment"
        ]
        
        print("🏠 Testing Prosumer Parser Integration")
        print("=" * 50)
        
        for i, description in enumerate(test_descriptions, 1):
            print(f"\n📝 Test {i}: {description}")
            print("-" * 30)
            
            try:
                config = parser.text_to_prosumer_config(description)
                print("✅ Parsing successful!")
                
                # Display key extracted attributes
                if 'bess_capacity_kwh' in config:
                    print(f"   Battery: {config['bess_capacity_kwh']}kWh")
                if 'solar_capacity_kw' in config:
                    print(f"   Solar: {config['solar_capacity_kw']}kW")
                if 'has_ev' in config and config['has_ev']:
                    print("   EV: Yes")
                    
            except Exception as e:
                print(f"❌ Parsing failed: {e}")
                
        print("\n✅ Prosumer parser integration test complete!")
        
    except ImportError:
        print("❌ LLM parser not available - check Module 2 setup")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_dashboard_integration():
    """Show how the parser integrates with the dashboard."""
    print("\n🔧 Dashboard Integration Details")
    print("=" * 50)
    
    print("""
The prosumer parser integrates with the dashboard through:

1. 📝 Sidebar Input Widget
   - Text area for natural language descriptions
   - Parse button to trigger LLM processing
   - Results display in expandable JSON format

2. 🧠 LLM Processing Pipeline
   - Gemini API for natural language understanding
   - Structured output generation
   - Error handling and validation

3. 📊 Visual Feedback
   - Success/error status indicators
   - Formatted configuration display
   - Integration with simulation parameters

4. 💾 Data Integration
   - Parsed configurations can be saved
   - Integration with fleet generation
   - Real-time parameter updates

Example Dashboard Code:
```python
# In dashboard.py sidebar
prosumer_description = st.sidebar.text_area(
    "Describe your prosumer:",
    placeholder="e.g., Tech-savvy user with Tesla Powerwall..."
)

if st.sidebar.button("Parse Prosumer"):
    parser = LLMProsumerParser()
    config = parser.text_to_prosumer_config(prosumer_description)
    st.sidebar.json(config)
```
    """)

if __name__ == "__main__":
    test_prosumer_parser()
    show_dashboard_integration()
