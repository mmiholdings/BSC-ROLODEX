from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from origin.origin_engine import Hypothesis, OriginProbabilityEngine, Signal


class OriginEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = OriginProbabilityEngine(abstain_threshold=0.5, margin_threshold=0.03)
        self.hypotheses = [
            Hypothesis(
                key="alpha",
                label="Alpha branch",
                feature_weights={"search": 1.0, "checkout": 1.0, "risk": -0.7},
                confirming_signs=["search uptick"],
                invalidators=["risk spikes"],
                time_window="24h",
            ),
            Hypothesis(
                key="beta",
                label="Beta branch",
                feature_weights={"search": 0.2, "checkout": -0.8, "risk": 1.1},
                confirming_signs=["mentions spike"],
                invalidators=["checkout recovers"],
                time_window="24h",
            ),
        ]

    def test_rank_selects_primary_and_counterfactual(self) -> None:
        signals = [
            Signal("search", 0.7),
            Signal("checkout", 0.6),
            Signal("risk", -0.2),
            Signal("volatility", 0.3),
            Signal("liquidity", 0.1),
            Signal("institutional_trust", 0.2),
        ]
        output = self.engine.run(self.hypotheses, signals)

        self.assertEqual(output.primary_pick.key, "alpha")
        self.assertEqual(len(output.counterfactuals), 1)
        self.assertFalse(output.primary_pick.abstain)

    def test_regime_detection_liquidity_stress(self) -> None:
        signals = [
            Signal("search", 0.1),
            Signal("checkout", 0.0),
            Signal("risk", 0.2),
            Signal("volatility", 0.8),
            Signal("liquidity", -0.8),
            Signal("institutional_trust", 0.0),
        ]
        output = self.engine.run(self.hypotheses, signals)
        self.assertEqual(output.regime, "liquidity_stress")

    def test_cli_smoke(self) -> None:
        sample = Path("origin/examples/scenario.json")
        result = subprocess.run(
            [sys.executable, "-m", "origin.cli", "--input", str(sample)],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn("primary_pick", payload)
        self.assertIn("counterfactuals", payload)


if __name__ == "__main__":
    unittest.main()
