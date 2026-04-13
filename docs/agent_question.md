# Problem Question for the Multi-Agent System

Use this canonical question to align all agents:

> Given citizen-level trends from longitudinal status events, user context, and mobility signals, should the system recommend proactive preventive support (`1`) or keep standard monitoring (`0`) for each citizen while minimizing unnecessary activations?

## Agent-specific sub-questions
- **Data Agent**: Are the three input sources complete, parseable, and aligned by citizen/time?
- **Feature Agent**: Which temporal and behavioral features best capture deterioration or instability?
- **ML Risk Agent**: Which citizens are statistical anomalies relative to peer trajectories?
- **Rule Risk Agent**: Do interpretable high-risk conditions exist (sharp drops, high exposure, poor sleep)?
- **Decision Agent**: How should ML and rule evidence be fused into final binary recommendations?

