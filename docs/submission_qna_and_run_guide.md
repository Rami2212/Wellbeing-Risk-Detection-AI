# Submission Q&A and Run Guide

This document answers common submission questions for the sandbox and evaluation flow.

## 1) Training dataset uploads: what for, what next, and session ID

### What are training uploads for?
- Training uploads are for practice and score feedback.
- You can upload multiple times in sandbox mode to improve your approach.
- Use this phase to tune features, thresholds, and model settings.

### What next after training upload?
1. Check the score/feedback on the challenge page.
2. Compare with previous attempts.
3. Improve the pipeline and run again.
4. Repeat until your training score is stable and good.
5. Then prepare your evaluation submission (one-shot rule).

### How to find the session ID to upload?
- In this project, every run prints a session ID in terminal output:
  - `Session ID: public-lev-1-xxxxxxxx`
- Use that exact run session ID in the challenge upload field.
- In Langfuse dashboard, search/filter records by that same session ID string.
- Optional validation: run `python "original langfuse code/main.py" <session_id>` to verify Langfuse can query traces for that session.

## 2) Evaluation dataset: what is it and what to upload?

Evaluation is the official scoring phase.

### Required uploads
1. **Output file(s)** first:
   - Plain text file.
   - One `CitizenID` per line.
   - Only IDs predicted as class `1`.
2. **Source code zip** after output upload:
   - Zip your full reproducible project (agent pipeline + dependencies + docs).
3. **Langfuse Session ID** in the modal field:
   - Use the session ID from the exact run used to generate the uploaded output file.

### Important rule
- For evaluation datasets, accepted submission is final (one-shot per dataset). Submit only when you are sure.

## 3) Langfuse dashboard shows 15 records: what to do?

That usually means you ran multiple experiments.

Use this process:
1. Pick the exact run that produced your final output file.
2. Note its session ID from terminal output.
3. In Langfuse dashboard, filter/search with that session ID.
4. Ignore older/non-final experiment records.
5. Submit the matching session ID with the matching output file.

Practical tip:
- Keep a small table locally with columns: `timestamp`, `session_id`, `output_file`, `notes`.

## 4) How to run this project

Run from repository root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then run dataset 1 pipeline:

```powershell
python run_pipeline.py --dataset-dir data/public_lev_1 --output-file outputs/public_lev_1_predictions.txt
```

Run smoke test:

```powershell
python tests/smoke_test.py
```

Optional: run other sandbox datasets with same pipeline:

```powershell
python run_pipeline.py --dataset-dir data/public_lev_2 --output-file outputs/public_lev_2_predictions.txt
python run_pipeline.py --dataset-dir data/public_lev_3 --output-file outputs/public_lev_3_predictions.txt
```

## Submission checklist (quick)
- Output file format is correct (one `CitizenID` per line, text file).
- Output file and session ID come from the same run.
- Source zip is complete and reproducible.
- You are ready before evaluation upload (one-shot).

## If upload says "The session ID is not valid"

This usually means the submitted ID is not found as a valid Langfuse session for that run.

Do this in order:
1. Reinstall project dependencies to ensure compatible Langfuse version:

```powershell
pip install -r requirements.txt --upgrade --force-reinstall
```

2. Run the pipeline once and capture the printed `Session ID`.
3. Wait 10-30 seconds to let telemetry flush.
4. In Langfuse UI, verify records from that run exist.
5. Submit the same run's output file and that same `Session ID`.

Avoid these common mistakes:
- Using a session ID from a different run than the uploaded output file.
- Submitting a trace/event ID instead of the printed session ID.
- Uploading immediately before Langfuse has ingested the run.
