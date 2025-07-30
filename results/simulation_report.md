# VPP LLM Agent Simulation Report

**Simulation Date**: 2025-07-29 22:17:11
**Duration**: 24 hours (24 timesteps)
**Fleet Size**: 20 prosumers

## Performance Comparison

| Metric | Agentic Model | Centralized Model | Advantage |
|--------|---------------|-------------------|----------|
| Total Profit | $8.22 | $5.70 | +44.3% |
| Avg Satisfaction | 6.000 | 4.500 | +33.3% |
| Success Rate | 100.0% | 100.0% | - |
| Total Capacity | 0.5 MWh | 0.3 MWh | - |
| Avg Optimization Time | 0.000s | 0.003s | - |

## Key Insights

- **Prosumer Satisfaction**: The agentic model achieved 600.0% average satisfaction vs 450.0% for centralized
- **Preference Violations**: Centralized model violated 337 prosumer preferences
- **Negotiation Complexity**: Average 3.0 rounds with 10.8 prosumers per coalition
- **Computational Efficiency**: Agentic model took 0.1x longer than centralized

## Conclusion

Results show trade-offs between profit optimization and prosumer satisfaction. Further tuning of negotiation strategies may improve the balance.
