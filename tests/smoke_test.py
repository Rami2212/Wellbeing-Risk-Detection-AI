from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.wellbeing_pipeline.config import PipelineConfig
from src.wellbeing_pipeline.pipeline import run_pipeline


def main() -> None:
    config = PipelineConfig(
        dataset_dir=Path("data/public_lev_1"),
        output_file=Path("outputs/smoke_predictions.txt"),
        model_path=Path("artifacts/models/smoke_isolation_forest.pkl"),
        model_dir=Path("artifacts/models"),
        session_id="smoke-test-session",
    )

    decisions, flagged = run_pipeline(config)
    assert len(decisions) > 0, "Decisions should not be empty"
    assert config.output_file.exists(), "Output file must be generated"

    print("Smoke test passed")
    print(f"Citizens analyzed: {len(decisions)}")
    print(f"Flagged: {len(flagged)}")


if __name__ == "__main__":
    main()
