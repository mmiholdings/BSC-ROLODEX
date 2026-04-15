"""ORIGIN probability engine.

A lightweight, deterministic engine that turns raw signals into ranked calls with:
- regime detection
- primary pick + counterfactual ladder
- first-confirming-sign and kill-condition guidance
- lead-time receipts for historical replay validation
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Signal:
    name: str
    value: float
    weight: float = 1.0


@dataclass(frozen=True)
class Hypothesis:
    key: str
    label: str
    confirming_sign: str
    kill_condition: str
    time_window: str


@dataclass(frozen=True)
class Receipt:
    hypothesis_key: str
    first_flag_at: datetime
    confirmed_at: datetime
    baseline_confirmed_at: datetime

    @property
    def lead_hours(self) -> float:
        return (self.confirmed_at - self.first_flag_at).total_seconds() / 3600

    @property
    def edge_vs_baseline_hours(self) -> float:
        return (self.baseline_confirmed_at - self.confirmed_at).total_seconds() / 3600


@dataclass(frozen=True)
class RankedPick:
    key: str
    label: str
    probability: float
    confidence: float
    reason: str
    confirming_sign: str
    kill_condition: str
    time_window: str
    abstain: bool


@dataclass(frozen=True)
class EngineOutput:
    generated_at: datetime
    regime: str
    primary: RankedPick
    counterfactuals: list[RankedPick]
    receipts: list[Receipt]


class OriginProbabilityEngine:
    """Deterministic scoring engine intended for explainable, replayable decisions."""

    def detect_regime(self, signals: Sequence[Signal]) -> str:
        pressure = sum(s.value * s.weight for s in signals)
        if pressure <= -0.5:
            return "panic"
        if pressure <= 0.3:
            return "calm"
        if pressure <= 1.5:
            return "narrative_shock"
        return "liquidity_stress"

    def score_hypothesis(self, hypothesis: Hypothesis, signals: Sequence[Signal]) -> tuple[float, float, str]:
        weighted = [s.value * s.weight for s in signals]
        raw = 0.5 + (mean(weighted) if weighted else 0.0)
        probability = max(0.01, min(0.99, raw))
        dispersion = max(weighted) - min(weighted) if len(weighted) > 1 else 0.05
        confidence = max(0.05, min(0.99, 1 - min(0.95, dispersion / 2)))
        reason = f"signal_mean={mean(weighted):.3f} dispersion={dispersion:.3f}"
        return probability, confidence, reason

    def rank(
        self,
        hypotheses: Sequence[Hypothesis],
        signals_by_hypothesis: dict[str, Sequence[Signal]],
        receipts: Iterable[Receipt] | None = None,
        abstain_threshold: float = 0.52,
    ) -> EngineOutput:
        now = datetime.now(timezone.utc)
        picks: list[RankedPick] = []

        for hypothesis in hypotheses:
            signals = signals_by_hypothesis.get(hypothesis.key, [])
            prob, conf, reason = self.score_hypothesis(hypothesis, signals)
            picks.append(
                RankedPick(
                    key=hypothesis.key,
                    label=hypothesis.label,
                    probability=prob,
                    confidence=conf,
                    reason=reason,
                    confirming_sign=hypothesis.confirming_sign,
                    kill_condition=hypothesis.kill_condition,
                    time_window=hypothesis.time_window,
                    abstain=prob < abstain_threshold,
                )
            )

        if not picks:
            raise ValueError("at least one hypothesis is required")

        picks.sort(key=lambda p: (p.abstain, -p.probability, -p.confidence))
        primary = picks[0]
        counterfactuals = picks[1:4]

        regime_signals = signals_by_hypothesis.get(primary.key, [])
        regime = self.detect_regime(regime_signals)

        return EngineOutput(
            generated_at=now,
            regime=regime,
            primary=primary,
            counterfactuals=counterfactuals,
            receipts=list(receipts or []),
        )
