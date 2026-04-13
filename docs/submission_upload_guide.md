# Submission Upload Guide

This guide answers the exact upload questions for the hackathon portal.

## 1) Training dataset upload: what it is for, and what comes next

Training upload is a practice phase.
- You upload your output `.txt` for `public_lev_1` / `public_lev_2` / `public_lev_3`.
- The platform returns feedback/score so you can improve your pipeline.
- You can submit training multiple times.

After each training upload:
1. Check score and errors.
2. Improve model/agents/features.
3. Re-run pipeline and generate a new output file.
4. Keep the matching run `session_id`.

### How to find session ID to upload
- Run the pipeline and copy the printed line:
  - `Session ID: <value>`
- Use that exact value in the portal field.
- Confirm in Langfuse dashboard by filtering with this `session_id`.
- Optional check with reference script:
  - `python "original langfuse code/main.py" <session_id>`

## 2) Evaluation dataset section: what to upload

Evaluation is official and one-shot per dataset.

Upload order:
1. Upload output file(s) first (`.txt`, one `CitizenID` per line, only predicted class `1`).
2. Then upload source code `.zip` of the full reproducible project.
3. Provide the Langfuse `session_id` from the exact run that produced that output.

Important:
- First accepted evaluation submission is final for that dataset.
- Do not use training session IDs for a different output file.

## 3) I see many records in Langfuse (example: 15). What should I do?

That is normal when you run multiple experiments.

Do this:
1. Select your final output file.
2. Identify the matching run `session_id` from terminal output.
3. In Langfuse, filter traces/events by that `session_id`.
4. Ignore other runs.
5. Submit only the session ID and output file from the same run.

If upload still says invalid session ID:
- Wait ~30 seconds after run.
- Re-check that the ID is session ID (not trace/observation ID).
- Re-run once, then verify with `original langfuse code/main.py`.

## 4) How to run this project

From repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Run dataset 1:

```powershell
python run_pipeline.py --dataset-dir data/public_lev_1 --output-file outputs/public_lev_1_predictions.txt
```

Optional other sandbox datasets:

```powershell
python run_pipeline.py --dataset-dir data/public_lev_2 --output-file outputs/public_lev_2_predictions.txt
python run_pipeline.py --dataset-dir data/public_lev_3 --output-file outputs/public_lev_3_predictions.txt
```

Run smoke test:

```powershell
python tests/smoke_test.py
```

