# ORIGIN Probability Engine

ORIGIN is a compact probability engine that follows a practical loop:

**Sense → Simulate → Rank → Recommend → Observe → Update**

The implementation in this folder focuses on four concrete outputs:

1. **Regime detection** (`calm`, `panic`, `narrative_shock`, `liquidity_stress`)
2. **Primary pick ranking** (best current call + abstain logic)
3. **Counterfactual ladder** (nearest rival branches)
4. **Lead-time receipts** (first flag, confirmation, baseline edge)

## Files

- `origin_engine.py` — core scoring, ranking, and regime logic.
- `replay.py` — historical replay helpers for lead-time benchmarking.

## Quick start

```bash
python - <<'PY'
from origin_engine import OriginProbabilityEngine, Hypothesis, Signal

engine = OriginProbabilityEngine()

hypotheses = [
    Hypothesis(
        key="launch_demand_up",
        label="Launch demand acceleration",
        confirming_sign="search volume up before social chatter",
        kill_condition="conversion declines for 2 consecutive windows",
        time_window="24-72h",
    ),
    Hypothesis(
        key="false_spike",
        label="Headline-only spike fades",
        confirming_sign="sentiment decays without checkout intent",
        kill_condition="repeat buyer cohort expands",
        time_window="12-48h",
    ),
]

signals = {
    "launch_demand_up": [Signal("search", 0.18, 1.0), Signal("checkout_intent", 0.11, 1.2)],
    "false_spike": [Signal("mentions", 0.08, 1.0), Signal("return_rate", -0.02, 1.0)],
}

result = engine.rank(hypotheses, signals)
print(result.regime)
print(result.primary.label, round(result.primary.probability, 3))
PY
```

## Product constraints baked in

- The engine favors **explainable, deterministic scoring** over opaque decisions.
- It supports **abstention** when confidence/probability is weak.
- It provides a structure for proving **lead-time advantage** via replay receipts.
