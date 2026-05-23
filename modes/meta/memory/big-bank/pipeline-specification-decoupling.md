# Why: pipeline-specification decoupling

Pipeline handles live in `.claude/commands/pipe/` and get auto-loaded into context on every session. Pipeline specifications live in `.claude/pipeline-specifications/` and are only read when a pipeline is actually invoked.

The split exists because pipeline specifications can grow long — multi-step logic, error handling rules, branching conditions. Loading all of that on every session would burn tokens for no benefit most of the time. The handle is intentionally thin: just enough to know the command exists and where to find the implementation.

The cost: one extra file per pipeline and an indirection to follow. Worth it once specifications get non-trivial.
