# ORIGIN Probability Engine

This is a runnable ORIGIN engine implementation (not just a concept note).

It executes the full loop:

**Sense → Simulate → Rank → Recommend → Observe → Update**

## What it does now

- Ingests real signal payloads and hypothesis definitions.
- Detects live regime (`calm`, `panic`, `narrative_shock`, `liquidity_stress`, `institutional_fracture`).
- Scores hypotheses with deterministic, explainable weighted logic.
- Emits:
  - `primary_pick`
  - `counterfactuals` (top rivals)
  - `first_confirming_sign`
  - `next_confirming_sign`
  - `kill_condition`
  - `changelog` (what changed vs prior run)
- Includes replay metrics support for lead-time and baseline edge.

## Run it

```bash
python -m origin.cli --input origin/examples/scenario.json
```

Optional flags:

```bash
python -m origin.cli \
  --input origin/examples/scenario.json \
  --output origin/examples/output.json \
  --abstain-threshold 0.57 \
  --margin-threshold 0.06
```

## Test it

```bash
python -m unittest origin.tests.test_origin_engine
```

## JSON input contract

- `hypotheses[]`
  - `key`, `label`
  - `feature_weights` (map of feature → signed weight)
  - `confirming_signs[]`
  - `invalidators[]`
  - `time_window`
- `signals[]`
  - `key`, `value`, optional `momentum`, `reliability`, `updated_at`
- `receipts[]` (optional)
  - `hypothesis_key`, `first_flag_at`, `confirmed_at`, `baseline_confirmed_at`

Use `origin/examples/scenario.json` as a starting template.
