# Module 5 Results Directory

This directory contains all simulation results and analysis outputs from the VPP LLM Agent Module 5 implementation.

## Generated Files

When you run the simulation (`python simulation.py`), the following files will be generated:

- **`simulation_results.csv`**: Detailed timestep-by-timestep data comparing agentic vs centralized approaches
- **`simulation_summary.json`**: Aggregated performance statistics and key metrics
- **`simulation_report.md`**: Human-readable analysis with insights and conclusions
- **`simulation.log`**: Detailed execution logs and debugging information

## Key Performance Indicators (KPIs)

The results will include comprehensive metrics across multiple dimensions:

### Financial Performance
- Total profit comparison between approaches
- Success rates and bid clearing statistics
- Price competitiveness and market responsiveness

### Prosumer Satisfaction
- Average satisfaction scores (key differentiator)
- Preference violation tracking
- User experience quantification

### Operational Efficiency
- Coalition formation patterns
- Negotiation complexity metrics
- Computational performance benchmarks

## Usage

After running simulations, use these results for:

1. **Performance Analysis**: Compare agentic vs centralized approaches
2. **Value Proposition Validation**: Quantify trade-offs between profit and satisfaction
3. **Module 6 Input**: Provide data for visualization dashboard
4. **Research Insights**: Support academic and industry research

## Example Results Structure

```csv
timestamp,lmp_price,agentic_success,agentic_actual_profit,centralized_actual_profit,profit_difference,satisfaction_difference
2023-08-15 00:00:00,42.56,True,125.50,138.75,-13.25,0.82
2023-08-15 01:00:00,37.03,True,98.20,105.30,-7.10,0.79
...
```

Results demonstrate the core value proposition: while centralized optimization may achieve higher theoretical profits, the agentic approach maintains prosumer satisfaction through preference consideration, making it superior for real-world deployment.
