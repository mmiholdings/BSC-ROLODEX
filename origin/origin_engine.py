"""Production-ready ORIGIN probability engine.

This module implements the operating loop:
Sense -> Simulate -> Rank -> Recommend -> Observe -> Update.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import math
from typing import Any, Mapping, Sequence


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


@dataclass(frozen=True)
class Signal:
    key: str
    value: float
    momentum: float = 0.0
    reliability: float = 1.0
    updated_at: datetime | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Signal":
        updated_at = payload.get("updated_at")
        return cls(
            key=str(payload["key"]),
            value=float(payload["value"]),
            momentum=float(payload.get("momentum", 0.0)),
            reliability=float(payload.get("reliability", 1.0)),
            updated_at=_parse_dt(updated_at) if updated_at else None,
        )


@dataclass(frozen=True)
class Hypothesis:
    key: str
    label: str
    feature_weights: dict[str, float]
    confirming_signs: list[str]
    invalidators: list[str]
    time_window: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Hypothesis":
        return cls(
            key=str(payload["key"]),
            label=str(payload["label"]),
            feature_weights={k: float(v) for k, v in dict(payload.get("feature_weights", {})).items()},
            confirming_signs=list(payload.get("confirming_signs", [])),
            invalidators=list(payload.get("invalidators", [])),
            time_window=str(payload.get("time_window", "24-72h")),
        )


@dataclass(frozen=True)
class Receipt:
    hypothesis_key: str
    first_flag_at: datetime
    confirmed_at: datetime
    baseline_confirmed_at: datetime

    @property
    def lead_hours(self) -> float:
        return (self.confirmed_at - self.first_flag_at).total_seconds() / 3600.0

    @property
    def baseline_edge_hours(self) -> float:
        return (self.baseline_confirmed_at - self.confirmed_at).total_seconds() / 3600.0


@dataclass(frozen=True)
class RankedPick:
    key: str
    label: str
    probability: float
    confidence: float
    score: float
    time_window: str
    first_confirming_sign: str
    next_confirming_sign: str
    kill_condition: str
    why_it_won: str
    abstain: bool


@dataclass(frozen=True)
class ChangeLog:
    ranking_changed: bool
    confidence_delta: float
    probability_delta: float
    reason: str


@dataclass(frozen=True)
class EngineOutput:
    generated_at: datetime
    regime: str
    primary_pick: RankedPick
    counterfactuals: list[RankedPick]
    receipts: list[Receipt]
    changelog: ChangeLog

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at.isoformat(),
            "regime": self.regime,
            "primary_pick": asdict(self.primary_pick),
            "counterfactuals": [asdict(p) for p in self.counterfactuals],
            "receipts": [
                {
                    "hypothesis_key": r.hypothesis_key,
                    "first_flag_at": r.first_flag_at.isoformat(),
                    "confirmed_at": r.confirmed_at.isoformat(),
                    "baseline_confirmed_at": r.baseline_confirmed_at.isoformat(),
                    "lead_hours": r.lead_hours,
                    "baseline_edge_hours": r.baseline_edge_hours,
                }
                for r in self.receipts
            ],
            "changelog": asdict(self.changelog),
        }


class OriginProbabilityEngine:
    def __init__(self, abstain_threshold: float = 0.55, margin_threshold: float = 0.05) -> None:
        self.abstain_threshold = abstain_threshold
        self.margin_threshold = margin_threshold

    def detect_regime(self, signal_map: Mapping[str, Signal]) -> str:
        volatility = signal_map.get("volatility", Signal("volatility", 0.0)).value
        liquidity = signal_map.get("liquidity", Signal("liquidity", 0.0)).value
        narrative = signal_map.get("narrative_velocity", Signal("narrative_velocity", 0.0)).value
        trust = signal_map.get("institutional_trust", Signal("institutional_trust", 0.0)).value

        if trust < -0.7:
            return "institutional_fracture"
        if volatility > 0.65 and liquidity < -0.4:
            return "liquidity_stress"
        if volatility > 0.55:
            return "panic"
        if narrative > 0.7:
            return "narrative_shock"
        return "calm"

    def _score_hypothesis(self, hypothesis: Hypothesis, signal_map: Mapping[str, Signal]) -> tuple[float, float, float]:
        weighted = 0.0
        total_weight = 0.0
        agreement = 0

        for feature, weight in hypothesis.feature_weights.items():
            signal = signal_map.get(feature)
            if signal is None:
                continue
            contribution = weight * signal.value * signal.reliability
            weighted += contribution
            total_weight += abs(weight)
            if contribution > 0:
                agreement += 1

        normalized = weighted / total_weight if total_weight else 0.0
        probability = 1.0 / (1.0 + math.exp(-3.0 * normalized))

        coverage = min(1.0, len(hypothesis.feature_weights) and (agreement / len(hypothesis.feature_weights)) or 0.0)
        confidence = min(0.99, max(0.05, 0.4 + 0.6 * coverage))
        return probability, confidence, normalized

    def _mk_pick(
        self,
        hypothesis: Hypothesis,
        probability: float,
        confidence: float,
        score: float,
        top_gap: float,
    ) -> RankedPick:
        first = hypothesis.confirming_signs[0] if hypothesis.confirming_signs else "No confirming sign configured"
        nxt = hypothesis.confirming_signs[1] if len(hypothesis.confirming_signs) > 1 else "No second confirming sign configured"
        kill = hypothesis.invalidators[0] if hypothesis.invalidators else "No explicit kill condition configured"
        why = f"Composite score {score:.3f}; lead over runner-up {top_gap:.3f}."
        return RankedPick(
            key=hypothesis.key,
            label=hypothesis.label,
            probability=round(probability, 4),
            confidence=round(confidence, 4),
            score=round(score, 4),
            time_window=hypothesis.time_window,
            first_confirming_sign=first,
            next_confirming_sign=nxt,
            kill_condition=kill,
            why_it_won=why,
            abstain=False,
        )

    def run(
        self,
        hypotheses: Sequence[Hypothesis],
        signals: Sequence[Signal],
        receipts: Sequence[Receipt] | None = None,
        previous_output: EngineOutput | None = None,
    ) -> EngineOutput:
        if not hypotheses:
            raise ValueError("At least one hypothesis is required")

        signal_map = {s.key: s for s in signals}
        regime = self.detect_regime(signal_map)
        scored: list[tuple[Hypothesis, float, float, float]] = []

        for h in hypotheses:
            probability, confidence, score = self._score_hypothesis(h, signal_map)
            scored.append((h, probability, confidence, score))

        scored.sort(key=lambda item: (item[1], item[2], item[3]), reverse=True)

        leader = scored[0]
        runner_prob = scored[1][1] if len(scored) > 1 else 0.0
        margin = leader[1] - runner_prob
        primary_pick = self._mk_pick(leader[0], leader[1], leader[2], leader[3], margin)

        should_abstain = leader[1] < self.abstain_threshold or margin < self.margin_threshold
        if should_abstain:
            primary_pick = RankedPick(**{**asdict(primary_pick), "abstain": True, "why_it_won": primary_pick.why_it_won + " Abstain: weak edge."})

        counterfactuals: list[RankedPick] = []
        for h, p, c, s in scored[1:4]:
            gap = leader[1] - p
            counterfactuals.append(self._mk_pick(h, p, c, s, gap))

        changelog = self._build_changelog(previous_output, primary_pick, counterfactuals)

        return EngineOutput(
            generated_at=_utc_now(),
            regime=regime,
            primary_pick=primary_pick,
            counterfactuals=counterfactuals,
            receipts=list(receipts or []),
            changelog=changelog,
        )

    def _build_changelog(
        self,
        previous_output: EngineOutput | None,
        primary: RankedPick,
        counterfactuals: Sequence[RankedPick],
    ) -> ChangeLog:
        if previous_output is None:
            return ChangeLog(
                ranking_changed=False,
                confidence_delta=0.0,
                probability_delta=0.0,
                reason="Initial run; no prior ranking.",
            )

        prev = previous_output.primary_pick
        ranking_changed = prev.key != primary.key
        confidence_delta = round(primary.confidence - prev.confidence, 4)
        probability_delta = round(primary.probability - prev.probability, 4)

        if ranking_changed:
            reason = f"Primary changed from {prev.key} to {primary.key}."
        elif probability_delta > 0:
            reason = "Primary survived; conviction increased."
        elif probability_delta < 0:
            reason = "Primary survived; conviction decreased due to new evidence."
        elif counterfactuals:
            reason = "No material change in ranking."
        else:
            reason = "Single-hypothesis mode; no counterfactuals available."

        return ChangeLog(
            ranking_changed=ranking_changed,
            confidence_delta=confidence_delta,
            probability_delta=probability_delta,
            reason=reason,
        )


def load_hypotheses(payload: Sequence[Mapping[str, Any]]) -> list[Hypothesis]:
    return [Hypothesis.from_dict(item) for item in payload]


def load_signals(payload: Sequence[Mapping[str, Any]]) -> list[Signal]:
    return [Signal.from_dict(item) for item in payload]


def load_receipts(payload: Sequence[Mapping[str, Any]]) -> list[Receipt]:
    parsed: list[Receipt] = []
    for item in payload:
        parsed.append(
            Receipt(
                hypothesis_key=str(item["hypothesis_key"]),
                first_flag_at=_parse_dt(item["first_flag_at"]),
                confirmed_at=_parse_dt(item["confirmed_at"]),
                baseline_confirmed_at=_parse_dt(item["baseline_confirmed_at"]),
            )
        )
    return parsed
