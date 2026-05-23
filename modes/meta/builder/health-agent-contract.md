# Builder–Health-Agent Contract

Every builder principle must have a complementing detector.

The health-agent is the enforcement arm of the builder law. A rule that exists only in
`meta/builder/` but has no corresponding detector in `.claude/health-agent/detectors/`
is unenforceable — it will never be automatically caught.

## When adding a new builder rule

1. Write the rule in its canonical location (`security.md`, `user_experience.md`, etc.)
2. Create a detector in `.claude/health-agent/detectors/<rule_name>.py`
   - Export a single `detect(ctx) -> list[dict]` function
   - Return findings with `{rule, severity, evidence, suggested_fix}`
   - `severity` is one of: `violation`, `warning`, `anomaly`
3. Import the detector in `detect-health-issues.py` → `ALL_DETECTORS` list
4. Add the rule→law mapping to the `health-agent.md` lazy-load table

## Detector context object

```python
ctx = {
    "skill": str,                # skill name from run-summary.json
    "started_at": datetime,      # UTC, skill window start
    "transcript_path": str,      # path to session JSONL transcript
    "tool_uses": list[dict],     # tool_use blocks from assistant messages in window
    "tool_results": list[dict],  # tool_result events in window
    "permission_events": list[dict],  # from permission-events.jsonl, pre-filtered
    "claude_dir": str,           # absolute path to .claude/
}
```

## Severity guide

| Severity | Meaning | Agent verdict |
|---|---|---|
| `violation` | Clear breach of a builder rule | `confirmed_violation` or agent resolves |
| `warning` | Likely problem, needs judgment | `confirmed_violation` or `false_positive` |
| `anomaly` | Unexpected behavior, not a rule violation | `behavioral_anomaly` |
