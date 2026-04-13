# Wellbeing-Risk-Detection-AI

ML + multi-agent baseline for detecting suboptimal well-being trajectories from `public_lev_1` data, with Langfuse-ready observability.

## Project layout

- `data/public_lev_1/`: sandbox dataset 1 input files.
- `src/wellbeing_pipeline/`: pipeline implementation (agents, features, model, orchestration).
- `run_pipeline.py`: CLI entrypoint.
- `tests/smoke_test.py`: tiny local validation.
- `docs/hackathon_steps_and_submission.md`: step-by-step competition/submission process.
- `docs/submission_upload_guide.md`: focused upload FAQ (training/evaluation/session ID flow).
- `docs/agent_question.md`: canonical decision question for agents.
- `docs/implementation_report.md`: detailed explanation of all implemented parts.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set optional Langfuse and OpenRouter keys in `.env`.

## Run pipeline on dataset 1

```powershell
python run_pipeline.py --dataset-dir data/public_lev_1 --output-file outputs/public_lev_1_predictions.txt
```

Produced artifacts:
- `outputs/public_lev_1_predictions.txt`
- `artifacts/models/isolation_forest.pkl`

## Run smoke test

```powershell
python tests/smoke_test.py
```

## Notes

- Output format is challenge-compatible: one `CitizenID` per line for predicted class `1`.
- Pipeline combines unsupervised ML anomaly detection + rule-based risk scoring via cooperative agents.
- Langfuse instrumentation is optional and auto-disables when keys are missing.
- OpenRouter review is optional and only applied to borderline decisions when `OPENROUTER_API_KEY` is configured.
