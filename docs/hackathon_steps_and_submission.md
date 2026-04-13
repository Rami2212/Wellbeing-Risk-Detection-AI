# Hackathon Steps and Submission Process

This document translates `guidelines/hackathon guidelines.txt` and `guidelines/question.txt` into an actionable checklist.

## 1) Understand the challenge objective
- Build an adaptive **AI multi-agent** system that classifies each citizen-time trajectory:
  - `0`: standard monitoring
  - `1`: activate personalized preventive support
- Optimize for:
  - strong F1 score (precision-recall balance)
  - temporal robustness (distribution/drift resilience)
  - efficient runtime/cost behavior

## 2) Prepare your environment
- Create/Open your OpenRouter account for sandbox practice (free models can be used).
- Configure Langfuse credentials for observability:
  - `LANGFUSE_PUBLIC_KEY`
  - `LANGFUSE_SECRET_KEY`
  - `LANGFUSE_HOST` (optional, default cloud endpoint)
- Ensure your pipeline can generate a unique `session_id` for each run.

## 3) Study the input data format
- `status.csv` contains monitoring events with:
  - `EventID`, `CitizenID`, `EventType`, activity/sleep/exposure indices, `Timestamp`
- `locations.json` contains GPS traces:
  - citizen id, datetime, lat/lng, city
- `users.json` contains demographics and residence data.
- Build citizen-level and temporal features from these sources.

## 4) Implement the solution workflow
- In sandbox training mode:
  - use dataset(s) 1-3 for iterative development
  - submit outputs repeatedly to estimate score
- For each run:
  - execute pipeline
  - collect Langfuse traces with the run `session_id`
  - produce output txt in required format

## 5) Output format requirements (strict)
- Output must be a plain ASCII/UTF-8 text file.
- Each line = one `CitizenID` predicted as class `1`.
- No extra columns, separators, JSON, or metadata in the output file.

## 6) Training submission flow (sandbox)
- Upload output file(s) for one or more provided inputs.
- Review score feedback and iterate.
- Keep a record of best-performing configuration + session ID.

## 7) Evaluation submission flow (official)
- Step 1: upload output file(s) for at least one provided evaluation input.
- Step 2: upload source code zip (complete agentic system).
- Include Langfuse Session ID in the upload modal field.
- Important rule: **evaluation submission is one-shot per dataset** (first accepted submission is final).

## 8) Final packaging checklist before evaluation upload
- Confirm output file is correctly encoded and format-compliant.
- Confirm source zip includes full reproducible project.
- Confirm `session_id` maps to traces in Langfuse.
- Confirm run command and dependency file are included.
- Confirm no placeholder API keys remain in committed files.

## 9) Scoring priorities to optimize
- Primary: F1 quality (avoid both false positives and false negatives).
- Secondary/complementary: speed, cost, operational efficiency.
- Design agents for practical production-style trade-offs.

