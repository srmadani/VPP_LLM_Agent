"""
Communication Schemas for VPP LLM Agent - Module 3

This module defines Pydantic models for all inter-agent communication
messages to ensure strict schema validation between AggregatorAgent and ProsumerAgents.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class MarketOpportunityType(str, Enum):
    """Types of market opportunities available in CAISO."""
    ENERGY = "energy"
    SPIN = "spin"
    NONSPIN = "nonspin"


class MarketOpportunity(BaseModel):
    """
    Market opportunity announced by AggregatorAgent to all ProsumerAgents.
    
    Represents a specific market opportunity in CAISO with timing,
    capacity requirements, and pricing information.
    """
    
    opportunity_id: str = Field(..., description="Unique identifier for this opportunity")
    market_type: MarketOpportunityType = Field(..., description="Type of market service")
    timestamp: datetime = Field(..., description="Market delivery timestamp")
    duration_hours: float = Field(..., description="Duration of service delivery in hours")
    required_capacity_mw: float = Field(..., description="Total capacity needed in MW")
    market_price_mwh: float = Field(..., description="Current market clearing price per MWh")
    deadline: datetime = Field(..., description="Deadline for bid responses")
    
    # Market-specific parameters
    ramp_rate_required: Optional[float] = Field(None, description="Required ramp rate for ancillary services")
    minimum_duration: Optional[float] = Field(None, description="Minimum service duration")
    location_constraint: Optional[str] = Field(None, description="Geographic constraint if any")


class ProsumerBid(BaseModel):
    """
    Bid response from ProsumerAgent to AggregatorAgent.
    
    Contains the prosumer's availability, capacity offer, and pricing requirements
    for the announced market opportunity.
    """
    
    prosumer_id: str = Field(..., description="Unique prosumer identifier")
    opportunity_id: str = Field(..., description="Reference to the market opportunity")
    is_available: bool = Field(..., description="Whether prosumer can participate")
    
    # Capacity and technical constraints
    available_capacity_kw: float = Field(default=0.0, description="Available capacity in kW")
    minimum_capacity_kw: float = Field(default=0.0, description="Minimum dispatch if selected")
    maximum_capacity_kw: float = Field(default=0.0, description="Maximum capacity available")
    ramp_rate_kw_per_min: Optional[float] = Field(None, description="Asset ramp rate capability")
    
    # Pricing requirements
    minimum_price_per_mwh: float = Field(..., description="Minimum acceptable price per MWh")
    startup_cost: float = Field(default=0.0, description="Fixed cost for participation")
    variable_cost_per_mwh: float = Field(default=0.0, description="Variable operating cost")
    
    # Prosumer-specific constraints
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="Qualitative user constraints")
    asset_constraints: Dict[str, Any] = Field(default_factory=dict, description="Technical asset limitations")
    availability_window: Optional[Dict[str, datetime]] = Field(None, description="Time window constraints")


class AggregatorOffer(BaseModel):
    """
    Counter-offer from AggregatorAgent to specific ProsumerAgents during negotiation.
    
    Used to negotiate better terms or request specific capacity allocations
    from prosumers during the multi-round negotiation process.
    """
    
    offer_id: str = Field(..., description="Unique offer identifier")
    opportunity_id: str = Field(..., description="Reference to the market opportunity")
    target_prosumer_ids: List[str] = Field(..., description="Prosumers receiving this offer")
    
    # Proposed terms
    offered_price_per_mwh: float = Field(..., description="Proposed price per MWh")
    requested_capacity_kw: float = Field(..., description="Specific capacity request")
    dispatch_schedule: Optional[Dict[str, float]] = Field(None, description="Proposed dispatch profile")
    
    # Negotiation context
    round_number: int = Field(..., description="Negotiation round number")
    total_rounds_planned: int = Field(..., description="Total rounds in negotiation")
    competing_offers: int = Field(..., description="Number of competing bids received")
    
    # Incentives and flexibility
    bonus_payment: float = Field(default=0.0, description="Additional incentive payment")
    flexibility_request: Optional[str] = Field(None, description="Request for operational flexibility")
    urgency_level: str = Field(default="normal", description="Urgency of response needed")


class ProsumerResponse(BaseModel):
    """
    Response from ProsumerAgent to AggregatorOffer during negotiation rounds.
    
    Contains the prosumer's decision on the counter-offer with updated
    terms or rejection reasons.
    """
    
    response_id: str = Field(..., description="Unique response identifier")
    offer_id: str = Field(..., description="Reference to the aggregator offer")
    prosumer_id: str = Field(..., description="Responding prosumer identifier")
    
    # Response decision
    is_accepted: bool = Field(..., description="Whether offer is accepted")
    counter_offer: bool = Field(default=False, description="Whether this is a counter-offer")
    
    # Updated terms (if counter-offering)
    updated_price_per_mwh: Optional[float] = Field(None, description="Counter-offered price")
    updated_capacity_kw: Optional[float] = Field(None, description="Modified capacity offer")
    updated_constraints: Optional[Dict[str, Any]] = Field(None, description="Additional constraints")
    
    # Response reasoning
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if declined")
    flexibility_offered: Optional[str] = Field(None, description="Additional flexibility offered")
    user_feedback: Optional[str] = Field(None, description="Qualitative user input")
    
    # Negotiation metadata
    response_timestamp: datetime = Field(default_factory=datetime.now, description="When response was sent")
    confidence_level: float = Field(default=1.0, description="Confidence in this response (0-1)")


class CoalitionMember(BaseModel):
    """
    Details of a prosumer committed to the final coalition.
    
    Used by AggregatorAgent to track committed resources and their
    agreed terms for bid formulation.
    """
    
    prosumer_id: str = Field(..., description="Prosumer identifier")
    committed_capacity_kw: float = Field(..., description="Final committed capacity")
    agreed_price_per_mwh: float = Field(..., description="Final agreed price")
    dispatch_schedule: Dict[str, float] = Field(..., description="Agreed dispatch profile")
    
    # Settlement terms
    startup_payment: float = Field(default=0.0, description="Fixed startup payment")
    performance_bonus: float = Field(default=0.0, description="Performance incentive")
    penalty_terms: Dict[str, float] = Field(default_factory=dict, description="Penalty structure")
    
    # Asset details for optimization
    asset_type: str = Field(..., description="Primary asset type (BESS, EV, Solar)")
    technical_constraints: Dict[str, Any] = Field(..., description="Technical limitations")
    ramp_capabilities: Optional[Dict[str, float]] = Field(None, description="Ramp rate capabilities")


class NegotiationSummary(BaseModel):
    """
    Summary of completed negotiation for logging and analysis.
    
    Contains all key metrics and outcomes from the negotiation process
    for performance tracking and optimization.
    """
    
    opportunity_id: str = Field(..., description="Market opportunity identifier")
    total_rounds: int = Field(..., description="Number of negotiation rounds completed")
    total_prosumers_contacted: int = Field(..., description="Total prosumers that received opportunity")
    total_bids_received: int = Field(..., description="Total initial bids received")
    
    # Coalition results
    final_coalition_size: int = Field(..., description="Number of prosumers in final coalition")
    total_committed_capacity_mw: float = Field(..., description="Total capacity secured")
    average_price_per_mwh: float = Field(..., description="Weighted average price")
    
    # Negotiation efficiency
    negotiation_duration_seconds: float = Field(..., description="Total negotiation time")
    rounds_to_convergence: int = Field(..., description="Rounds needed to reach agreement")
    prosumer_satisfaction_score: float = Field(..., description="Average satisfaction score")
    
    # Market competitiveness
    price_improvement_percent: float = Field(..., description="Price improvement through negotiation")
    capacity_utilization_percent: float = Field(..., description="Percentage of requested capacity secured")
    coalition_stability_score: float = Field(..., description="Predicted coalition stability")


class AgentState(BaseModel):
    """
    Central state object for LangGraph containing all negotiation state.
    
    This serves as the single source of truth for the entire negotiation
    process, tracking all messages, decisions, and outcomes.
    """
    
    # Current market opportunity
    current_opportunity: Optional[MarketOpportunity] = Field(None, description="Active market opportunity")
    
    # Prosumer fleet
    available_prosumers: List[str] = Field(default_factory=list, description="List of prosumer IDs available for bidding")
    prosumer_details: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Prosumer asset and preference details")
    
    # Negotiation tracking
    initial_bids: List[ProsumerBid] = Field(default_factory=list, description="All initial prosumer bids")
    aggregator_offers: List[AggregatorOffer] = Field(default_factory=list, description="All aggregator counter-offers")
    prosumer_responses: List[ProsumerResponse] = Field(default_factory=list, description="All prosumer responses")
    
    # Coalition building
    committed_coalition: List[CoalitionMember] = Field(default_factory=list, description="Final committed prosumers")
    rejected_prosumers: List[str] = Field(default_factory=list, description="Prosumers that declined participation")
    pending_negotiations: Dict[str, str] = Field(default_factory=dict, description="Ongoing negotiation status by prosumer")
    
    # Negotiation metadata
    current_round: int = Field(default=0, description="Current negotiation round")
    max_rounds: int = Field(default=3, description="Maximum negotiation rounds allowed")
    negotiation_start_time: Optional[datetime] = Field(None, description="When negotiation started")
    deadline: Optional[datetime] = Field(None, description="Bid submission deadline")
    
    # Performance tracking
    total_capacity_target_mw: float = Field(default=0.0, description="Target capacity to secure")
    current_capacity_secured_mw: float = Field(default=0.0, description="Currently committed capacity")
    target_price_ceiling: float = Field(default=0.0, description="Maximum acceptable average price")
    
    # Final outputs
    final_bid: Optional[Dict[str, Any]] = Field(None, description="Generated VPP bid for market submission")
    negotiation_summary: Optional[NegotiationSummary] = Field(None, description="Final negotiation summary")
    success: bool = Field(default=False, description="Whether negotiation was successful")
    
    class Config:
        arbitrary_types_allowed = True
