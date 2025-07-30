"""
Agentic Framework for VPP LLM Agent - Module 3

This module defines the multi-agent system structure using LangGraph,
including agent initialization, communication protocols, and the main
negotiation graph workflow.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Import from other modules
# Use dynamic path resolution instead of hardcoded relative paths
import os
module_2_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'module_2_asset_modeling')
if module_2_path not in sys.path:
    sys.path.insert(0, module_2_path)
    
from prosumer_models import Prosumer
from fleet_generator import FleetGenerator

# Import schemas
from schemas import (
    AgentState, MarketOpportunity, ProsumerBid, AggregatorOffer, 
    ProsumerResponse, CoalitionMember, NegotiationSummary
)


class VPPAgentFramework:
    """
    Main framework class managing the multi-agent VPP negotiation system.
    
    This class initializes the LangGraph-based agent system, manages
    agent state, and orchestrates the negotiation workflow between
    AggregatorAgent and ProsumerAgents.
    """
    
    def __init__(self, api_key: Optional[str] = None, data_path: Optional[str] = None):
        """
        Initialize the VPP agent framework.
        
        Args:
            api_key: Gemini API key (loads from .env if not provided)
            data_path: Path to Module 1 data directory (uses default if not provided)
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in .env file")
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1  # Low temperature for consistent decision-making
        )
        
        # Load agent prompts
        self.aggregator_prompt = self._load_prompt("aggregator_prompt.txt")
        self.prosumer_prompt = self._load_prompt("prosumer_prompt.txt")
        
        # Initialize prosumer fleet (will be populated when needed)
        self.prosumer_fleet: Dict[str, Prosumer] = {}
        
        # Initialize fleet generator with data path
        if data_path:
            self.fleet_generator = FleetGenerator(data_path=data_path)
        else:
            self.fleet_generator = FleetGenerator()  # Use default path
        
        # Create the LangGraph workflow
        self.workflow = self._create_workflow()
        
    def _load_prompt(self, filename: str) -> str:
        """Load system prompt from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", filename)
        with open(prompt_path, 'r') as f:
            return f.read()
    
    def _create_workflow(self) -> StateGraph:
        """
        Create the LangGraph workflow for VPP agent negotiation.
        
        The workflow defines the sequence of agent interactions:
        1. Aggregator announces market opportunity
        2. Prosumers submit initial bids
        3. Multi-round negotiation process
        4. Coalition formation and bid optimization
        """
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("announce_opportunity", self._announce_opportunity)
        workflow.add_node("collect_initial_bids", self._collect_initial_bids)
        workflow.add_node("evaluate_bids", self._evaluate_bids)
        workflow.add_node("make_counter_offers", self._make_counter_offers)
        workflow.add_node("collect_responses", self._collect_responses)
        workflow.add_node("form_coalition", self._form_coalition)
        workflow.add_node("finalize_negotiation", self._finalize_negotiation)
        
        # Define workflow edges
        workflow.set_entry_point("announce_opportunity")
        
        workflow.add_edge("announce_opportunity", "collect_initial_bids")
        workflow.add_edge("collect_initial_bids", "evaluate_bids")
        
        # Add conditional edge for negotiation rounds
        workflow.add_conditional_edges(
            "evaluate_bids",
            self._should_continue_negotiation,
            {
                "make_offers": "make_counter_offers",
                "form_coalition": "form_coalition"
            }
        )
        
        workflow.add_edge("make_counter_offers", "collect_responses")
        workflow.add_edge("collect_responses", "evaluate_bids")
        workflow.add_edge("form_coalition", "finalize_negotiation")
        workflow.add_edge("finalize_negotiation", END)
        
        return workflow.compile()
    
    def initialize_prosumer_fleet(self, fleet_size: int = 50) -> None:
        """
        Initialize a fleet of prosumers for the negotiation.
        
        Args:
            fleet_size: Number of prosumers to create
        """
        # Generate diverse prosumer fleet
        prosumers = self.fleet_generator.create_prosumer_fleet(fleet_size)
        
        # Convert to dictionary with string IDs
        self.prosumer_fleet = {
            f"prosumer_{i+1:03d}": prosumer 
            for i, prosumer in enumerate(prosumers)
        }
        
        print(f"Initialized fleet of {len(self.prosumer_fleet)} prosumers")
    
    def create_market_opportunity(
        self, 
        market_type: str = "energy",
        required_capacity_mw: float = 5.0,
        market_price_mwh: float = 75.0,
        duration_hours: float = 1.0
    ) -> MarketOpportunity:
        """
        Create a sample market opportunity for testing.
        
        Args:
            market_type: Type of market (energy, spin, nonspin)
            required_capacity_mw: Required capacity in MW
            market_price_mwh: Market clearing price per MWh
            duration_hours: Service duration in hours
            
        Returns:
            MarketOpportunity object
        """
        return MarketOpportunity(
            opportunity_id=f"opp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            market_type=market_type,
            timestamp=datetime.now() + timedelta(hours=1),
            duration_hours=duration_hours,
            required_capacity_mw=required_capacity_mw,
            market_price_mwh=market_price_mwh,
            deadline=datetime.now() + timedelta(minutes=30)
        )
    
    # Node functions for the LangGraph workflow
    
    def _announce_opportunity(self, state: AgentState) -> AgentState:
        """
        Aggregator announces market opportunity to all prosumers.
        """
        print(f"🏢 AggregatorAgent: Announcing market opportunity {state.current_opportunity.opportunity_id}")
        
        # Initialize available prosumers
        state.available_prosumers = list(self.prosumer_fleet.keys())
        
        # Store prosumer details for reference
        state.prosumer_details = {
            prosumer_id: {
                "has_bess": prosumer.bess is not None,
                "has_ev": prosumer.ev is not None,
                "has_solar": prosumer.solar is not None,
                "load_profile_id": prosumer.load_profile_id,
                "participation_willingness": prosumer.participation_willingness
            }
            for prosumer_id, prosumer in self.prosumer_fleet.items()
        }
        
        # Set negotiation parameters
        state.negotiation_start_time = datetime.now()
        state.current_round = 1
        state.total_capacity_target_mw = state.current_opportunity.required_capacity_mw
        
        print(f"   📢 Opportunity: {state.current_opportunity.market_type.upper()} market")
        print(f"   📊 Required: {state.current_opportunity.required_capacity_mw:.1f} MW")
        print(f"   💰 Price: ${state.current_opportunity.market_price_mwh:.2f}/MWh")
        print(f"   ⏰ Duration: {state.current_opportunity.duration_hours:.1f} hours")
        print(f"   👥 Prosumers contacted: {len(state.available_prosumers)}")
        
        return state
    
    def _collect_initial_bids(self, state: AgentState) -> AgentState:
        """
        Collect initial bids from all prosumers.
        """
        print(f"📥 Collecting initial bids from {len(state.available_prosumers)} prosumers...")
        
        initial_bids = []
        
        for prosumer_id in state.available_prosumers:
            prosumer = self.prosumer_fleet[prosumer_id]
            
            # Simulate prosumer bid decision
            bid = self._simulate_prosumer_bid(prosumer_id, prosumer, state.current_opportunity)
            
            if bid.is_available and bid.available_capacity_kw > 0:
                initial_bids.append(bid)
                print(f"   ✅ {prosumer_id}: {bid.available_capacity_kw:.1f} kW @ ${bid.minimum_price_per_mwh:.2f}/MWh")
            else:
                print(f"   ❌ {prosumer_id}: Not available")
        
        state.initial_bids = initial_bids
        
        # Calculate total offered capacity
        total_offered_kw = sum(bid.available_capacity_kw for bid in initial_bids)
        total_offered_mw = total_offered_kw / 1000
        
        print(f"📊 Initial bidding results:")
        print(f"   Bids received: {len(initial_bids)}")
        print(f"   Total capacity: {total_offered_mw:.2f} MW")
        print(f"   Target capacity: {state.total_capacity_target_mw:.2f} MW")
        print(f"   Coverage: {(total_offered_mw/state.total_capacity_target_mw)*100:.1f}%")
        
        return state
    
    def _simulate_prosumer_bid(
        self, 
        prosumer_id: str, 
        prosumer: Prosumer, 
        opportunity: MarketOpportunity
    ) -> ProsumerBid:
        """
        Simulate a prosumer's bidding decision using asset characteristics.
        
        This is a simplified simulation that will be replaced with actual
        LLM-powered agent reasoning in Module 4.
        """
        
        # Check basic availability based on prosumer characteristics
        is_available = prosumer.participation_willingness > 0.3
        
        if not is_available:
            return ProsumerBid(
                prosumer_id=prosumer_id,
                opportunity_id=opportunity.opportunity_id,
                is_available=False,
                minimum_price_per_mwh=0.0
            )
        
        # Calculate available capacity from assets
        available_capacity_kw = 0.0
        
        # Battery contribution
        if prosumer.bess:
            # Use 70% of available discharge capacity for grid services
            bess_capacity = prosumer.bess.get_available_discharge_capacity_kw() * 0.7
            available_capacity_kw += bess_capacity
        
        # EV contribution (simplified - assume 50% availability when plugged in)
        if prosumer.ev and prosumer.ev.is_plugged_in:
            ev_capacity = prosumer.ev.max_charge_power_kw * 0.5
            available_capacity_kw += ev_capacity
        
        # Solar curtailment (if applicable during high generation periods)
        if prosumer.solar and opportunity.market_type == "energy":
            # Simplified solar curtailment potential
            solar_curtailment = prosumer.solar.capacity_kw * 0.2
            available_capacity_kw += solar_curtailment
        
        # Determine minimum price based on asset costs and market conditions
        base_price = opportunity.market_price_mwh * 0.8  # Start at 80% of market price
        
        # Add prosumer-specific premium based on willingness
        willingness_premium = (1.0 - prosumer.participation_willingness) * 20  # 0-20 $/MWh premium
        minimum_price = base_price + willingness_premium
        
        return ProsumerBid(
            prosumer_id=prosumer_id,
            opportunity_id=opportunity.opportunity_id,
            is_available=available_capacity_kw > 0.1,  # Minimum 0.1 kW threshold
            available_capacity_kw=available_capacity_kw,
            minimum_capacity_kw=min(0.5, available_capacity_kw),  # Minimum dispatch
            maximum_capacity_kw=available_capacity_kw,
            minimum_price_per_mwh=minimum_price,
            user_preferences={
                "participation_level": prosumer.participation_willingness,
                "asset_types": [
                    asset for asset in ["bess", "ev", "solar"] 
                    if getattr(prosumer, asset) is not None
                ]
            }
        )
    
    def _evaluate_bids(self, state: AgentState) -> AgentState:
        """
        Aggregator evaluates received bids and determines next action.
        """
        print(f"🧮 AggregatorAgent: Evaluating bids in round {state.current_round}")
        
        # Sort bids by price (most competitive first)
        sorted_bids = sorted(state.initial_bids, key=lambda x: x.minimum_price_per_mwh)
        
        # Calculate current capacity and pricing
        total_capacity_kw = sum(bid.available_capacity_kw for bid in sorted_bids)
        if sorted_bids:
            avg_price = sum(bid.minimum_price_per_mwh for bid in sorted_bids) / len(sorted_bids)
        else:
            avg_price = 0.0
        
        state.current_capacity_secured_mw = total_capacity_kw / 1000
        
        print(f"   📈 Capacity analysis:")
        print(f"      Available: {state.current_capacity_secured_mw:.2f} MW")
        print(f"      Target: {state.total_capacity_target_mw:.2f} MW")
        print(f"      Average price: ${avg_price:.2f}/MWh")
        print(f"      Market price: ${state.current_opportunity.market_price_mwh:.2f}/MWh")
        
        return state
    
    def _should_continue_negotiation(self, state: AgentState) -> str:
        """
        Determine whether to continue negotiation or form coalition.
        """
        
        # Check if we have sufficient capacity
        capacity_ratio = state.current_capacity_secured_mw / state.total_capacity_target_mw
        
        # Check if we're within round limits
        within_round_limit = state.current_round < state.max_rounds
        
        # Simple decision logic (will be enhanced with LLM reasoning in Module 4)
        if capacity_ratio >= 0.9 and state.current_round >= 2:
            print(f"✅ Sufficient capacity secured ({capacity_ratio:.1%}), forming coalition")
            return "form_coalition"
        elif within_round_limit and capacity_ratio < 1.2:
            print(f"🔄 Continue negotiation (Round {state.current_round + 1})")
            return "make_offers"
        else:
            print(f"⏰ Max rounds reached or excess capacity, forming coalition")
            return "form_coalition"
    
    def _make_counter_offers(self, state: AgentState) -> AgentState:
        """
        Aggregator makes counter-offers to selected prosumers.
        """
        state.current_round += 1
        print(f"💬 AggregatorAgent: Making counter-offers in round {state.current_round}")
        
        # For this module, we'll simulate counter-offers
        # In Module 4, this will use actual LLM reasoning
        
        counter_offers = []
        
        # Target prosumers with competitive bids for better terms
        competitive_bids = [bid for bid in state.initial_bids 
                          if bid.minimum_price_per_mwh <= state.current_opportunity.market_price_mwh * 0.9]
        
        for bid in competitive_bids[:10]:  # Limit to top 10 competitive bids
            offer = AggregatorOffer(
                offer_id=f"offer_{state.current_round}_{bid.prosumer_id}",
                opportunity_id=state.current_opportunity.opportunity_id,
                target_prosumer_ids=[bid.prosumer_id],
                offered_price_per_mwh=bid.minimum_price_per_mwh * 1.05,  # 5% price improvement
                requested_capacity_kw=bid.available_capacity_kw,
                round_number=state.current_round,
                total_rounds_planned=state.max_rounds,
                competing_offers=len(competitive_bids)
            )
            counter_offers.append(offer)
            print(f"   💰 Offer to {bid.prosumer_id}: ${offer.offered_price_per_mwh:.2f}/MWh")
        
        state.aggregator_offers.extend(counter_offers)
        return state
    
    def _collect_responses(self, state: AgentState) -> AgentState:
        """
        Collect responses from prosumers to counter-offers.
        """
        print(f"📩 Collecting responses to counter-offers...")
        
        responses = []
        
        # Simulate prosumer responses to counter-offers
        for offer in state.aggregator_offers:
            if offer.round_number == state.current_round:
                for prosumer_id in offer.target_prosumer_ids:
                    prosumer = self.prosumer_fleet[prosumer_id]
                    
                    # Simplified response logic (will be LLM-powered in Module 4)
                    accepts_offer = (offer.offered_price_per_mwh >= 
                                   state.current_opportunity.market_price_mwh * 0.85 and
                                   prosumer.participation_willingness > 0.4)
                    
                    response = ProsumerResponse(
                        response_id=f"resp_{offer.offer_id}",
                        offer_id=offer.offer_id,
                        prosumer_id=prosumer_id,
                        is_accepted=accepts_offer,
                        response_timestamp=datetime.now()
                    )
                    
                    responses.append(response)
                    
                    status = "✅ Accepted" if accepts_offer else "❌ Declined"
                    print(f"   {status}: {prosumer_id}")
        
        state.prosumer_responses.extend(responses)
        return state
    
    def _form_coalition(self, state: AgentState) -> AgentState:
        """
        Form final coalition from committed prosumers.
        """
        print(f"🤝 Forming final coalition...")
        
        coalition_members = []
        
        # Collect accepted responses
        accepted_responses = [r for r in state.prosumer_responses if r.is_accepted]
        
        # Also include initial bids that meet criteria
        for bid in state.initial_bids:
            prosumer_id = bid.prosumer_id
            
            # Check if prosumer hasn't already responded to counter-offer
            has_response = any(r.prosumer_id == prosumer_id for r in accepted_responses)
            
            # Include if price is acceptable and no counter-offer was made
            if (not has_response and 
                bid.minimum_price_per_mwh <= state.current_opportunity.market_price_mwh * 0.95):
                
                member = CoalitionMember(
                    prosumer_id=prosumer_id,
                    committed_capacity_kw=bid.available_capacity_kw,
                    agreed_price_per_mwh=bid.minimum_price_per_mwh,
                    dispatch_schedule={f"hour_{i}": bid.available_capacity_kw 
                                     for i in range(int(state.current_opportunity.duration_hours))},
                    asset_type=self._get_primary_asset_type(prosumer_id),
                    technical_constraints={}
                )
                coalition_members.append(member)
        
        # Add members from accepted counter-offers
        for response in accepted_responses:
            # Find the corresponding offer
            offer = next(o for o in state.aggregator_offers if o.offer_id == response.offer_id)
            
            member = CoalitionMember(
                prosumer_id=response.prosumer_id,
                committed_capacity_kw=offer.requested_capacity_kw,
                agreed_price_per_mwh=offer.offered_price_per_mwh,
                dispatch_schedule={f"hour_{i}": offer.requested_capacity_kw 
                                 for i in range(int(state.current_opportunity.duration_hours))},
                asset_type=self._get_primary_asset_type(response.prosumer_id),
                technical_constraints={}
            )
            coalition_members.append(member)
        
        state.committed_coalition = coalition_members
        
        # Update secured capacity
        total_committed_kw = sum(m.committed_capacity_kw for m in coalition_members)
        state.current_capacity_secured_mw = total_committed_kw / 1000
        
        print(f"✅ Coalition formed:")
        print(f"   Members: {len(coalition_members)}")
        print(f"   Total capacity: {state.current_capacity_secured_mw:.2f} MW")
        print(f"   Average price: ${sum(m.agreed_price_per_mwh for m in coalition_members) / len(coalition_members):.2f}/MWh")
        
        return state
    
    def _get_primary_asset_type(self, prosumer_id: str) -> str:
        """Get the primary asset type for a prosumer."""
        prosumer = self.prosumer_fleet[prosumer_id]
        
        if prosumer.bess:
            return "BESS"
        elif prosumer.ev:
            return "EV"
        elif prosumer.solar:
            return "Solar"
        else:
            return "Load"
    
    def _finalize_negotiation(self, state: AgentState) -> AgentState:
        """
        Finalize negotiation and prepare summary.
        """
        print(f"🏁 Finalizing negotiation...")
        
        # Calculate negotiation metrics
        negotiation_duration = (datetime.now() - state.negotiation_start_time).total_seconds()
        
        # Create negotiation summary
        summary = NegotiationSummary(
            opportunity_id=state.current_opportunity.opportunity_id,
            total_rounds=state.current_round,
            total_prosumers_contacted=len(state.available_prosumers),
            total_bids_received=len(state.initial_bids),
            final_coalition_size=len(state.committed_coalition),
            total_committed_capacity_mw=state.current_capacity_secured_mw,
            average_price_per_mwh=(
                sum(m.agreed_price_per_mwh for m in state.committed_coalition) / 
                len(state.committed_coalition) if state.committed_coalition else 0.0
            ),
            negotiation_duration_seconds=negotiation_duration,
            rounds_to_convergence=state.current_round,
            prosumer_satisfaction_score=0.85,  # Placeholder - will be calculated in Module 4
            price_improvement_percent=5.0,  # Placeholder
            capacity_utilization_percent=(
                state.current_capacity_secured_mw / state.total_capacity_target_mw * 100
            ),
            coalition_stability_score=0.90  # Placeholder
        )
        
        state.negotiation_summary = summary
        state.success = state.current_capacity_secured_mw >= state.total_capacity_target_mw * 0.8
        
        print(f"📋 Negotiation Summary:")
        print(f"   Success: {'✅ Yes' if state.success else '❌ No'}")
        print(f"   Duration: {negotiation_duration:.1f} seconds")
        print(f"   Capacity secured: {state.current_capacity_secured_mw:.2f} MW ({summary.capacity_utilization_percent:.1f}%)")
        print(f"   Coalition size: {summary.final_coalition_size} prosumers")
        print(f"   Average price: ${summary.average_price_per_mwh:.2f}/MWh")
        
        return state
    
    def run_negotiation(
        self,
        market_opportunity: Optional[MarketOpportunity] = None,
        fleet_size: int = 50
    ) -> AgentState:
        """
        Run a complete negotiation cycle.
        
        Args:
            market_opportunity: Market opportunity to negotiate (creates default if None)
            fleet_size: Size of prosumer fleet to initialize
            
        Returns:
            Final agent state with negotiation results
        """
        
        # Initialize prosumer fleet (reinitialize if size differs)
        current_fleet_size = len(self.prosumer_fleet) if self.prosumer_fleet else 0
        if not self.prosumer_fleet or current_fleet_size != fleet_size:
            self.initialize_prosumer_fleet(fleet_size)
        
        # Create market opportunity if not provided
        if market_opportunity is None:
            market_opportunity = self.create_market_opportunity()
        
        # Initialize agent state with robust schema handling
        try:
            # Try direct initialization first
            initial_state = AgentState(
                current_opportunity=market_opportunity,
                max_rounds=3
            )
        except Exception as e:
            print(f"⚠️  Direct AgentState initialization failed: {e}")
            print("🔄 Attempting with dictionary conversion...")
            
            # Fallback: convert to dict and recreate
            try:
                if hasattr(market_opportunity, 'model_dump'):
                    opp_dict = market_opportunity.model_dump()
                elif hasattr(market_opportunity, 'dict'):
                    opp_dict = market_opportunity.dict()
                else:
                    opp_dict = market_opportunity
                
                # Recreate MarketOpportunity from dict to ensure clean schema
                fresh_opportunity = MarketOpportunity(**opp_dict)
                
                initial_state = AgentState(
                    current_opportunity=fresh_opportunity,
                    max_rounds=3
                )
                print("✅ AgentState initialized with schema refresh")
                
            except Exception as e2:
                print(f"❌ Schema refresh also failed: {e2}")
                # Last resort: initialize without opportunity and set it manually
                initial_state = AgentState(max_rounds=3)
                initial_state.current_opportunity = market_opportunity
                print("⚠️  Using manual assignment fallback")
        
        print(f"🚀 Starting VPP negotiation for opportunity {market_opportunity.opportunity_id}")
        print("=" * 80)
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        print("=" * 80)
        print(f"🎯 Negotiation complete!")
        
        return final_state


def main():
    """Main function for testing the agent framework."""
    
    print("VPP Agent Framework - Module 3")
    print("==============================")
    
    try:
        # Initialize framework
        framework = VPPAgentFramework()
        
        # Create a test market opportunity
        opportunity = framework.create_market_opportunity(
            market_type="energy",
            required_capacity_mw=3.0,
            market_price_mwh=85.0,
            duration_hours=1.0
        )
        
        # Run negotiation
        result = framework.run_negotiation(opportunity, fleet_size=30)
        
        print(f"\n📊 Final Results:")
        print(f"Success: {result.success}")
        print(f"Coalition size: {len(result.committed_coalition)}")
        print(f"Total capacity: {result.current_capacity_secured_mw:.2f} MW")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
