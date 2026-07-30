# Focus area — "Guardrails that protect a non-technical user from themselves"

*One of the optional focus areas under [`project.md`](project.md) — a suggestion the team may
fold in, not a standalone assignment. It has a genuine research half, so it also stands as a
BP/DP topic on its own if a single strong student wants it.*


Here's what keeps me up about handing it to real people: the system is driven by an LLM agent
with real power over a local repository, & the users I most want are **not technical**. A
technical user knows what the tool can't safely do. A normal person doesn't — & they'll ask for
it in perfect good faith.

## The problem

**A well-meaning request can quietly wreck the setup.** Picture a non-technical user telling the
agent: *"I use Google Keep — can you sync my notes into this?"* They think it's trivial. But the
infrastructure may have no Google integration at that moment, & a naive agent, trying to be
helpful, can thrash the local repository into a mess chasing a request it was never equipped to
fulfil. The user did nothing wrong. The system had no guardrail between *innocent intent* &
*destructive action* — & without one, the project simply isn't safe to put in ordinary hands.

## What I want (the outcome, not the how)

A **guardrail layer** that sits between a user's request & the agent's power, & keeps a
non-technical user from harming their own setup — recognizing when a request is outside what the
system can safely do, & declining or redirecting **gracefully** instead of failing destructively.

## Rough shape (to size it — not to design it)

Two halves that make this a real project, not a patch:

- **Research half.** Survey how existing agent systems handle this — the honest state of the art
  in keeping an autonomous agent inside safe bounds (policy layers, capability gating,
  intent-risk classification, prompt-level defenses). Bring back what's actually good practice,
  not folklore.
- **Build half.** A guardrail component with both **deterministic** rules (hard "this cannot
  happen" boundaries) & a **semantic** layer (judging the intent & risk of a free-text request).
  A first honest cut could be as simple as an on-prompt hook running a cheap model as a filter —
  but where the line between deterministic & semantic falls is the team's to design.

## What "done" looks like

- A non-technical user makes an unsupported or dangerous request (the Google Keep case, & a set
  of others like it) & the system **protects the setup** — refuses or redirects safely, repo
  intact — instead of thrashing it.
- The behavior is demonstrated against a batch of "innocent but unsafe" prompts, not a single
  happy-path demo.
- The guardrail is a real seam a maintainer can point to & extend, not scattered `if` checks.
- Technical user shall still be able to do their crazy things

## Explicitly out of scope

- **Don't build the integrations users ask for.** The point is a guardrail that *declines
  gracefully* — not actually wiring up Google Keep & every other service. Fulfilling the request
  is a different (endless) project; safely *not* fulfilling it is this one.
- **Don't re-architect the agent.** This is a protective layer over the existing system, not a
  redesign of how it works.

## What the team gets from me

- **A repo built to be read by a machine cold.** `CLAUDE.md` is the map; skills, pipelines & MCP
  tools are self-describing. Point an LLM at the repo & ask where a thing lives — that's the
  intended onboarding path, so nobody inherits a black box.
- **The hook surface already exists.** The project already enforces some invariants through
  agent hooks (pre-tool gates, prompt-submit hooks) — a real anchor point for a guardrail layer,
  handed over as customer input rather than as the design.
- **Real failure cases from a real user** — me. I run this daily & can hand over the actual
  "innocent request that hurt" moments, which are worth more than an invented threat model.
- **Me, as customer** — reachable for direction against clear milestones; upfront that I steer &
  unblock rather than hand-hold daily, so the brief is milestone-shaped on purpose.

## Helpful background (not gatekeeping)

Interest in agent/LLM safety & the "how do you keep an autonomous system inside the lines"
question; comfort with git, Python & the command line. An appetite for research-plus-build — the
person who wants to read what the field actually does before writing the filter.
