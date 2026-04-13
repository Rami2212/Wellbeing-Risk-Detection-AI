# Implementation Report

This report documents the current baseline implementation for sandbox datasets, with focus on data flow, multi-agent behavior, Langfuse integration, and OpenRouter usage.

## Scope implemented
- End-to-end ML + multi-agent decision pipeline for dataset folders such as `data/public_lev_1`.
- Challenge-compliant ASCII output writer (one `CitizenID` per line for predicted class `1`).
- Optional Langfuse tracing with explicit `session_id` binding.
- Optional OpenRouter LLM review for borderline decisions.
- Reusable CLI entrypoint and smoke test.

## High-level data flow
1. `DataIngestionAgent` loads `status.csv`, `users.json`, and `locations.json`.
2. `FeatureAgent` builds citizen-level aggregates and trend features.
3. `MLRiskAgent` trains/scores an `IsolationForest` risk model.
4. `RuleRiskAgent` computes interpretable rule scores and flags.
5. `DecisionAgent` fuses ML + rules into a composite score and final flag.
6. Optional OpenRouter review is applied only to borderline cases near threshold.
7. Final flagged IDs are written to output `.txt`; model artifact is persisted.
8. Langfuse run is flushed at the end to ensure session visibility.

## File-by-file responsibilities
- `src/wellbeing_pipeline/config.py`
  - Defines `PipelineConfig`, `LangfuseConfig`, `OpenRouterConfig`.
  - Loads env-driven settings for Langfuse/OpenRouter.
- `src/wellbeing_pipeline/data_loader.py`
  - Reads and normalizes source files into DataFrames.
- `src/wellbeing_pipeline/features.py`
  - Builds feature matrix: temporal trends, exposure/sleep/activity stats, mobility features, demographic enrichments.
- `src/wellbeing_pipeline/model.py`
  - Wraps `IsolationForest` training/scoring and artifact save/load.
- `src/wellbeing_pipeline/openrouter_client.py`
  - Implements `OpenRouterDecisionClient`.
  - Sends compact JSON payload for uncertain cases and parses strict `0/1` response.
  - Fails safely (returns `None`) when disabled/API unavailable.
- `src/wellbeing_pipeline/langfuse_utils.py`
  - Creates Langfuse client and root trace with `session_id`.
  - Provides safe `@observe` wrapper and step-level event emission.
  - Flushes context/client to reduce delayed-ingestion issues.
- `src/wellbeing_pipeline/agents.py`
  - Contains cooperative agent classes and `AgentContext`.
  - Emits structured run summaries (`ingestion_summary`, `feature_summary`, `ml_scoring`, `rule_scoring`, `decision_summary`).
- `src/wellbeing_pipeline/pipeline.py`
  - Orchestrates all agents and integrations.
  - Saves model and writes final output file.
- `src/wellbeing_pipeline/cli.py`
  - Parses CLI args and auto-generates session ID when omitted.
- `run_pipeline.py`
  - Minimal top-level runner.
- `tests/smoke_test.py`
  - Fast functional check for pipeline execution/output creation.

## Langfuse implementation details
- A unique `session_id` is created per run (or passed via CLI).
- Root trace is created with this `session_id` to support dashboard filtering and challenge upload validation.
- Each pipeline step logs summary event payloads.
- `langfuse_context.update_current_trace(session_id=...)` is used inside observed steps when available.

## OpenRouter implementation details
- OpenRouter is optional and enabled only when `OPENROUTER_API_KEY` is present.
- Model, site URL, and site title are configurable via env.
- LLM review is intentionally constrained to near-threshold decisions to limit cost/latency.
- If OpenRouter fails, baseline ML+rule decision remains unchanged.

## Runtime artifacts
- Predictions: `outputs/<dataset>_predictions.txt`
- Model: `artifacts/models/isolation_forest.pkl` (or custom CLI path)

## Notes for submission reliability
- Use the printed CLI session ID from the same run that generated the uploaded output.
- Wait briefly after run completion so Langfuse ingestion/flush is complete.
- Validate session visibility in Langfuse before uploading.
