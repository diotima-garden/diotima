# Focus area — "Replace LLM orchestration with deterministic code where an LLM isn't needed"

*One of the optional focus areas under [`project.md`](project.md) — a suggestion the team may
fold in, not a standalone assignment.*

I'll be honest about how it was built: fast, with one single focus — getting the *architecture*
right at the macro level. Optimization, token efficiency & edge cases were foreseen &, frankly,
ruthlessly sacrificed to get the platform standing. That trade bought me a working system; now
it's costing me on the parts that were never tightened.

## The problem

**The system leans on an LLM for work that doesn't need one.** Many steps are orchestrated by
the language model where a deterministic hook, script, or plain executable would do the same job
— faster, at zero token cost, & far more reliably. Every one of those is a place the system is
slower, more expensive, & more prone to non-deterministic failure than it has any reason to be.
Nobody has systematically found those seams & moved them from "the LLM decides" to "code
decides."

## What I want (the outcome, not the how)

The system **leaner & more deterministic** — the operations that don't genuinely require
reasoning moved off the LLM & onto deterministic code, so the same behavior costs fewer tokens,
runs faster, & fails less randomly. Where an LLM *is* genuinely doing the thinking, it stays.

## Rough shape (to size it — not to design it)

- **Find the seams.** Go through the system & identify where LLM orchestration is doing work a
  script or hook could do deterministically. The judgment call — "does this step actually need a
  model, or is it just convenient to ask one?" — is the heart of the project.
- **Convert them.** Move a meaningful set of those from LLM-driven to deterministic (hooks,
  utilities, executables) without losing capability, & show the difference.

## What "done" looks like

- A concrete set of previously LLM-orchestrated operations now run deterministically, with a
  **before/after** on token cost, latency, &/or reliability — a measured win, not a vibe.
- No capability lost: the system does the same things, just leaner. Verified by driving the real
  flows end-to-end, not only by "tests pass."
- The changes leave a pattern others can follow — a documented sense of "here's when a step
  should be code, not a prompt."

## Explicitly out of scope

- **Don't lobotomize it.** The goal is not "remove the LLM." Where genuine reasoning happens, it
  stays. Stripping a model out of a step that needs it is a regression, not an optimization.
- **Not a rewrite.** This is targeted conversion of specific seams, not rebuilding the platform.
- **Not a coordination role.** This is a standalone deliverable — a set of converted seams &
  their measurement — not an ongoing "watch the other teams" function.

## What the team gets from me

- **A repo built to be read by a machine cold.** `CLAUDE.md` is the map; skills, pipelines & MCP
  tools are self-describing. Point an LLM at the repo & ask where a thing lives — the intended
  onboarding path, so nobody inherits a black box.
- **Candidate seams from the customer.** I already have a sense of which parts lean on the LLM
  unnecessarily — handed over as a starting list, not as the answer; validating & extending it is
  the team's job.
- **Me, as customer** — reachable for direction against clear milestones; upfront that I steer &
  unblock rather than hand-hold daily, so the brief is milestone-shaped on purpose.

## Helpful background (not gatekeeping)

The person who enjoys making things lean — profiling, measuring, & the taste to tell "needs a
model" from "just asked one out of habit." Comfort with git, Python, the command line, & a bit of
appetite for agent/LLM plumbing (hooks, tool invocation).
