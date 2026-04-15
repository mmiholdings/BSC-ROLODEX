from __future__ import annotations

import argparse
import json
from pathlib import Path

from origin.origin_engine import (
    OriginProbabilityEngine,
    load_hypotheses,
    load_receipts,
    load_signals,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ORIGIN probability engine on a JSON payload")
    parser.add_argument("--input", required=True, help="Path to input JSON")
    parser.add_argument("--output", default="-", help="Path to write output JSON, or '-' for stdout")
    parser.add_argument("--abstain-threshold", type=float, default=0.55)
    parser.add_argument("--margin-threshold", type=float, default=0.05)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text())
    hypotheses = load_hypotheses(payload.get("hypotheses", []))
    signals = load_signals(payload.get("signals", []))
    receipts = load_receipts(payload.get("receipts", []))

    engine = OriginProbabilityEngine(
        abstain_threshold=args.abstain_threshold,
        margin_threshold=args.margin_threshold,
    )
    output = engine.run(hypotheses=hypotheses, signals=signals, receipts=receipts).to_dict()

    serialized = json.dumps(output, indent=2)
    if args.output == "-":
        print(serialized)
    else:
        Path(args.output).write_text(serialized + "\n")


if __name__ == "__main__":
    main()
