from pydantic import BaseModel


class OpportunityScore(BaseModel):
    freshness: float
    urgency: float
    profit: float
    probability: float
    effort: float
    risk: float
    complexity: float


class OpportunityIn(BaseModel):
    signal_id: int
    title: str
    body: str
    source: str


class CycleResult(BaseModel):
    ingested_signals: int
    qualified_opportunities: int
    replies_sent: int
    routed_deals: int
