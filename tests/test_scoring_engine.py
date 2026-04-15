from api.app.modules.scoring_engine import compute_score
from api.app.schemas.opportunity import OpportunityScore


def test_scoring_rule_matches_formula():
    s = OpportunityScore(
        freshness=10, urgency=8, profit=7, probability=6, effort=2, risk=2, complexity=2
    )
    assert compute_score(s) == (10 * 8 * 7 * 6) / (2 * 2 * 2)
