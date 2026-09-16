# system/

Host-level subsystems shared across hooks and skills.

| Where | What |
|---|---|
| `scm-integration/` | Policy gates for `gh` — PreToolUse hook enforcing the labeling strategy (≥1 label per issue) |
| `managed-models.json` | Orchestrator config for the `anki-mcp` plugin's `--managed-config` flag — which note types this deployment manages |
