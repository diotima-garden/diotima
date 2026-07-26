# Customer brief — "A learning-observability surface over Diotima"

> **Draft scaffold, not a final send.** AI-assisted, written to your voice (`voice.md`) —
> run the read-aloud test and rework by hand before this reaches Mlejnek or any student.
> Language: English, matching `cvut_mail.txt`. Whether the version students see should be
> Czech is an open decision (Mlejnek formalizes the official `zadání` either way).
>
> This is a **customer brief**: it states the problem I want solved and what "done" feels
> like. The requirements analysis, the product design, and the UI are the team's to make —
> that is the part the course is there to teach, so I deliberately don't pre-solve it here.

> **Source of truth.** This brief is the customer problem statement — the canonical scope &
> "what done looks like" that Mlejnek formally lists as the BI-SP1 `zadání`, and it stays
> stable for the semester. The *build backlog* (how it gets made, PRs, good-first-issues)
> lives in GitHub issue [#12](https://github.com/diotima-garden/diotima/issues/12); that
> issue tracks implementation, this brief owns the problem. Note the altitude gap: #12
> pre-commits to one narrow slice (a weekly stats *digest*), while this brief keeps the
> surface open (dashboard / reporting, the team's to design). Read #12 as one candidate
> starting point a contributor sketched — customer input, not the scope you're handed.

---

## Who's asking, & why

I'm a FIT graduate (Teoretická informatika, uid: baturvit). In my spare time I built an
open-source project called **Diotima** — a context-engineering system with deep integration of a
spaced-repetition database (Anki) to help a person actually learn a skill. It generates cards,
schedules reviews, & takes feedback. I use it every day.

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

- **The data, already exposed.** The project's Anki integration already surfaces the raw signal
  (learning velocity, vocabulary snapshot, review history, deck & collection statistics). No scraping,
  no reverse-engineering — the inputs are handed over.
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
