from datetime import datetime, timezone

from api.app.schemas.opportunity import OpportunityScore


def compute_score(s: OpportunityScore) -> float:
    denominator = max(s.effort * s.risk * s.complexity, 0.1)
    return (s.freshness * s.urgency * s.profit * s.probability) / denominator


def freshness_factor(created_at_source):
    if not created_at_source:
        return 1.0
    age_hours = (datetime.now(timezone.utc) - created_at_source).total_seconds() / 3600
    if age_hours <= 2:
        return 10.0
    if age_hours <= 24:
        return 6.0
    if age_hours <= 48:
        return 3.0
    return 1.0


def estimate_features(text: str) -> OpportunityScore:
    t = text.lower()
    urgency = 8.0 if any(x in t for x in ['asap', 'today', 'urgent']) else 4.0
    profit = 8.0 if any(x in t for x in ['$500', '$1000', 'budget']) else 5.0
    probability = 7.0 if any(x in t for x in ['ready to hire', 'need now']) else 5.0
    effort = 2.0 if any(x in t for x in ['logo', 'edit', 'fix']) else 4.0
    risk = 2.0 if any(x in t for x in ['escrow', 'upwork', 'contract']) else 4.0
    complexity = 2.0 if any(x in t for x in ['single page', 'one task']) else 4.0
    return OpportunityScore(
        freshness=1.0,
        urgency=urgency,
        profit=profit,
        probability=probability,
        effort=effort,
        risk=risk,
        complexity=complexity,
    )
