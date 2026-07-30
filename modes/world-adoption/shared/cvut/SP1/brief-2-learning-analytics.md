# Focus area — "A learning-observability surface over Diotima"

*One of the optional focus areas under [`project.md`](project.md) — a suggestion the team may
fold in, not a standalone assignment.*


Here's the gap that bothers me. The system is busy *doing* — adding cards, running reviews — but
I have almost no honest view of whether the learning is actually *working*. Am I getting faster?
Where am I stuck? Which deck is quietly plateauing while I keep grinding it? The data to answer
all of that already exists — every review is recorded, & the system already exposes it — but
there's no surface that turns it into insight. It's a dashboard-shaped hole, & filling it is a
clean, self-contained thing for a team to own.

## The problem

A learner (me, & anyone who adopts this) is flying with the instruments covered. The raw signal
is all there — review history, per-deck statistics, a "learning velocity" measure, a vocabulary
snapshot over time — but it lives as numbers behind tool calls, not as anything a human can look
at & understand. Without that view you can't tell effort from progress, you can't see a plateau
until you're deep in it, & you can't decide where to intervene.

## What I want (the outcome, not the how)

A **learning-observability surface** — a dashboard / reporting layer — that reads the learning
data the system already exposes & shows a person, at a glance:

- **Am I progressing?** velocity & retention over time, per grove / per deck.
- **Where am I stuck?** plateau & struggle detection — the decks or card-clusters that aren't
  moving.
- **Where should I put effort next?** at least one *actionable* signal, not just pretty charts.

The long horizon — stated so the design leaves room for it, **not** as a semester requirement — is
adapting to **motivation curves & plateaus**: noticing not just what's hard but when a learner is
about to disengage. Treat that as the north star the architecture should not foreclose.

## Rough shape (to size it — not to design it)

- The **data already exists** & is exposed through the project's Anki integration — review history,
  per-deck & collection statistics, a learning-velocity measure, a vocabulary snapshot. The team's
  job is not to invent data collection; it's to turn existing signal into an honest, legible product.
- This is a real product with real **users & metrics** — which means genuine requirements work
  (what does a learner actually need to see?), genuine data/UX design (how do you show a plateau so
  a person *believes* it?), & a surface someone would open more than once.

## What "done" looks like

- A learner opens the surface & within a minute understands their progress & where they're stuck,
  from **their real Anki data** — not a mockup with fake numbers.
- At least one intervention-worthy signal (e.g. plateau / struggling-deck detection) is surfaced &
  is trustworthy enough that I'd act on it.
- It reads from live data through the existing integration — reproducible on someone else's
  collection, not hard-wired to mine.

## Explicitly out of scope

- **Don't touch the generation or review pipeline.** This surface is **read-mostly** over data
  that's already produced. Changing how cards are made or scheduled is a different project.
- **No ML research required.** Simple, honest, legible statistics beat a black box a learner won't
  trust. The motivation-curve modeling is a stretch/north-star, not an ask — nobody is graded on a
  research result.

## What the team gets from me

- **The data, already exposed.** The project's Anki integration hands over the raw signal — review
  history, per-deck & collection statistics — no scraping, no reverse-engineering. On top of that
  there's a first stab at the *computed* metrics: [`analytics.py`](../../../../../plugins/anki-mcp/tools/analytics.py)
  (`vocabulary_snapshot`, `learning_velocity`). Fair warning — it was never tested, & honestly probably
  doesn't work as it stands. But the idea behind it is sound, & it's a real starting point rather than a
  blank page. Treat it as a sketch to validate & fix, not a dependency to trust.
- **Real sample data to build against.** A snapshot of one of my actual decks lives in
  [`deck_quality_bootstrapping/`](../../../../../groves/languages/spanish/deck_quality_bootstrapping/)
  (387 cards, 3.5 months in, 211 mature) — so you can develop the surface against a real learner's
  history from day one, not invent numbers.
- **An idea bank.** [`creative-usages.md`](../../../../../groves/languages/creative-usages.md) is my rough,
  unordered list of what becomes possible once an AI can reason over a full deck — vocabulary mapping,
  plateau detection, study recommendations & more. Plenty of it is analytics-shaped; mine it for
  inspiration, ignore what doesn't fit.
- **A repo built to be read by a machine cold.** `CLAUDE.md` is the map; skills, pipelines & MCP
  tools are self-describing. Point an LLM at the repo & ask it where a thing lives — that's the
  intended onboarding path, so nobody inherits a black box.
- **A real user on the other end** — me. I run the system daily, so the team gets a customer who can
  say "no, that's not what a learner feels," which is worth more than a spec. Being upfront about my
  time: I steer against clear milestones, not daily hand-holding — the brief is milestone-shaped on
  purpose.

## Helpful background (not gatekeeping)

An eye for turning data into something a human trusts — some comfort with a data/vis or web-UI
stack, & interest in the honest-statistics side of "is this person actually learning?" You don't
need to know Anki; you need to care that a chart tells the truth.
