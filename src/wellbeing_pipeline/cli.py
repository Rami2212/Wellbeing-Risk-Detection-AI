from __future__ import annotations

import argparse
import logging
from pathlib import Path
import uuid

from dotenv import load_dotenv

try:
    from .config import PipelineConfig
    from .pipeline import run_pipeline
except ImportError:
    from src.wellbeing_pipeline.config import PipelineConfig
    from src.wellbeing_pipeline.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Well-being risk detection pipeline")
    parser.add_argument("--dataset-dir", default="data/public_lev_1", help="Dataset folder containing status.csv, users.json, locations.json")
    parser.add_argument("--output-file", default="outputs/public_lev_1_predictions.txt", help="ASCII output file path")
    parser.add_argument("--model-path", default="artifacts/models/isolation_forest.pkl", help="Trained model artifact path")
    parser.add_argument("--session-id", default=None, help="Langfuse session id; auto-generated when omitted")
    parser.add_argument("--contamination", type=float, default=0.2, help="Expected anomaly proportion for IsolationForest")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    return parser


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s  %(name)s: %(message)s",
    )
    parser = build_parser()
    args = parser.parse_args()

    session_id = args.session_id or f"public-lev-1-{uuid.uuid4().hex[:8]}"
    config = PipelineConfig(
        dataset_dir=Path(args.dataset_dir),
        output_file=Path(args.output_file),
        model_path=Path(args.model_path),
        model_dir=Path(args.model_path).parent,
        session_id=session_id,
        contamination=args.contamination,
        random_state=args.random_state,
    )

    decisions, flagged_ids = run_pipeline(config)

    print(f"Session ID: {session_id}")
    print(f"Total citizens analyzed: {len(decisions)}")
    print(f"Flagged citizens: {len(flagged_ids)}")
    print(f"Output written to: {args.output_file}")
    if flagged_ids:
        print("Flagged IDs:")
        for cid in flagged_ids:
            print(f"- {cid}")


if __name__ == "__main__":
    main()
