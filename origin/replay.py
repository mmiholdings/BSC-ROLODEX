from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from origin.origin_engine import Receipt


@dataclass(frozen=True)
class ReplaySummary:
    scenarios: int
    avg_lead_hours: float
    avg_baseline_edge_hours: float
    positive_edge_rate: float


def summarize_receipts(receipts: Sequence[Receipt]) -> ReplaySummary:
    if not receipts:
        return ReplaySummary(0, 0.0, 0.0, 0.0)

    lead = [r.lead_hours for r in receipts]
    edge = [r.baseline_edge_hours for r in receipts]
    positive = [e for e in edge if e > 0]

    return ReplaySummary(
        scenarios=len(receipts),
        avg_lead_hours=round(mean(lead), 4),
        avg_baseline_edge_hours=round(mean(edge), 4),
        positive_edge_rate=round(len(positive) / len(edge), 4),
    )
