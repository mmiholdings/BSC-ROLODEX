from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from origin_engine import Receipt


@dataclass(frozen=True)
class ReplaySummary:
    scenarios: int
    avg_lead_hours: float
    avg_edge_vs_baseline_hours: float


def summarize_receipts(receipts: Sequence[Receipt]) -> ReplaySummary:
    if not receipts:
        return ReplaySummary(scenarios=0, avg_lead_hours=0.0, avg_edge_vs_baseline_hours=0.0)

    lead = [r.lead_hours for r in receipts]
    edge = [r.edge_vs_baseline_hours for r in receipts]
    return ReplaySummary(
        scenarios=len(receipts),
        avg_lead_hours=sum(lead) / len(lead),
        avg_edge_vs_baseline_hours=sum(edge) / len(edge),
    )


if __name__ == "__main__":
    sample = [
        Receipt(
            hypothesis_key="demand_spike",
            first_flag_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            confirmed_at=datetime.fromisoformat("2026-01-01T18:00:00+00:00"),
            baseline_confirmed_at=datetime.fromisoformat("2026-01-02T03:00:00+00:00"),
        )
    ]
    summary = summarize_receipts(sample)
    print(summary)
