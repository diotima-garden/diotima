# Diotima — a team software project (BI-SP1)

## Who's asking, & why

I studied theoretical informatics at FIT (uid: baturvit) just like you.
In my spare time (bored with banking devops & infra & LLM gateway architecture) I built
an open-source project called **Diotima**: a context-engineering OS around a structured
directory context layering, with deep integration of a spaced-repetition
database (Anki) to help a person actually learn a skill. I use it every day. It works, & I
think the architecture is genuinely good. You are welcome to be among the lucky first contributors and
users, immensely boosting your own ability to learn.

The honest part: it works *on my machine*. What exists today is closer to a bare OS kernel with
a few example apps bolted on than to something a normal person installs & uses — a handful of
apps & APIs talking to each other on my PC, a power-user setup, not a product. The job, put
bluntly, is turning that kernel into something like Ubuntu. That gap between "works for me" &
"works for anyone" is the single thing standing between the project & real adoption, & I don't
have the time to close it alone. Quite a shame, considering the potential — which is exactly
why it's a good thing for a team to take on.

## What a *grove* is (one word you'll need)

Diotima separates the **runtime** (the player) from **groves** — self-contained knowledge
areas, one per skill you're learning (Spanish, an instrument, whatever), each with its own
specification & selectively with additional systems (memory management, anki, youtube extraction, ...).
A grove is the *app*; the runtime is the OS it runs on.
Building or adopting a grove is how the system grows.

The part I most want a real implementation to *showcase*: a grove is meant to be **trivially
shareable**, & a new grove is meant to **inherit an existing one** — a language grove built on a
generic deck node, a Spanish grove on the language grove, & so on. That inheritance structure is
live in production now: `groves/spanish` → `parents/language` → `parents/deck`, each its own repo
under `github.com/diotima-garden`, chained by git submodules and resolved automatically by
[`plugins/dafne`](../../../../../plugins/dafne/README.md) (`DAFNE.md` is each node's manifest).
`groves/spanish/DAFNE.md` is a worked example if you want to see it end to end.

## The one goal

**Make a grove trivially installable — & prove it generalizes by doing it for two distinct ones.**
The vertical slice: a stranger, on their own machine, not mine, brings up a working learning app
with **one command** & reaches a first real success in minutes — no manual environment surgery.

This is deliberately *one* slice, not "package all of Diotima." I'll be honest: I don't yet know
how the final shippable Diotima is packaged — plugin, container, something else. That's an open
question, & I'd rather it get *answered by a few concrete working instances* than debated in the
abstract. Build one thing that actually installs & runs end-to-end, & the general packaging
story falls out of it. That's the leverage a fresh team has.

There's one lever here I'd nudge you toward. Package a *single* grove & you can quietly hardcode
the install to that grove's machinery — a one-off that proves nothing about sharing. Package
**two distinct groves that lean on different machinery** — take the existing `spanish` grove
(Anki-heavy) as-is, & build a second grove of your own that plugs in *different* systems — & you
*can't* hardcode: the install has to stay generic across whatever a grove brings with it. That
generic "install any grove" operation is exactly what Diotima is really about — trivially sharing
& reusing groves — so two unlike groves don't just tick the box, they demonstrate the whole point.
Genericity proven by two real, different cases, not by abstraction.

- **The target** — get **two distinct groves** installable through one generic mechanism, the two
  deliberately using *different* machinery so the install can't be hardwired to one. Take `spanish`
  as-is for one; build the other yourself.

Either way the **grove is the vehicle & the motivation; the installable bundle is the
engineering core** — that's the part with the weight, & the part worth grading.

Two unlike groves force the install to stay generic — but only so far. The default install
may wire *each* grove's machinery explicitly (Anki here, something else there); it does **not**
have to solve fully-generic capability resolution — a grove declaring `requires: anki` &
the system auto-installing & activating that plugin with no per-grove wiring. That deeper
problem is a **bonus, architectural stretch** ([#17](https://github.com/diotima-garden/diotima/issues/17)),
not the floor & not the target. Reach for it only once two groves actually install.

## The honest asterisk on "installable"

"Trivially installable" does **not** mean "no account needed." Today the runtime is driven
through an LLM harness (Claude Code), so the app you ship still expects a user to bring their own
harness or an API key. That's a fine limit for a first slice — just don't promise it away. Removing
that dependency (running under a vendor-neutral harness) is what would unlock true one-click, no-
account install someday; it's noted below as a *future* thing, deliberately **out of scope** for
this project.

## Deployment is yours to decide

I'm not handing you the answer, because I don't have it. Worth looking into — as options, not
instructions — a plain Docker Compose bring-up, a dockerized Anki, [pi.dev](https://pi.dev),
turning the whole thing into a generic plugin. Weigh them, pick one, & be able to defend the
choice. That "which approach & why" is the requirements-analysis muscle the course is there to
build, so I deliberately don't pre-solve it.

## What "done" looks like

- **`/onboard` runs clean on a machine that isn't mine.** `/onboard` audits a fresh machine &
  says plainly what works & what doesn't — so it *is* the acceptance harness here. The bar for
  "done" is the day `/onboard` finds nothing to complain about on a clean install. Use it as the
  gate, not a vibe check.
- **Each grove reaches a pinned, concrete first success** — not a fuzzy "it works." Pin one real
  milestone per grove up front & demonstrate it: for `spanish`, *adds & reviews a real Spanish
  card*; for the grove you build, its own equivalent concrete first success. A stranger, on their
  own machine, hits that milestone in minutes with no hand-editing of paths or environments
  (bring-your-own-harness allowed).
- Reproducible on a machine that isn't mine — verified by driving the real thing end-to-end, not
  only by "tests pass."

## Optional focus areas — fold in what fits

Once the slice stands, or alongside it, the team can pull from these. They're *suggestions*, not
requirements — pick what suits your interests & the time you have:

| Focus area | What |
|---|---|
| [Learning analytics](brief-2-learning-analytics.md) | A dashboard over data the system already collects — is the learner actually progressing, & where are they stuck? |
| [Guardrails](brief-4-guardrails.md) | Keep a non-technical user from wrecking their own setup with a well-meaning but unsafe request. Has a genuine research half — also stands as a BP/DP topic. |
| [Determinism / optimization](brief-5-determinism.md) | Move work off the LLM & onto deterministic code where a model isn't actually needed — measured wins in cost, speed, reliability. |
| **World adoption** *(non-technical)* | For a student who leans product over code: find a real first user or use-case for the slice — a faculty, an institution, a company — & follow the thread. A way in that doesn't need heavy engineering. |

## Not this semester (named, not forgotten)

**Making the core vendor-neutral** — un-welding it from one LLM harness so it runs under two. It
matters (it's what unlocks the no-account install above), but it's a heavy refactor on its own &
it isn't the MVP. Leaving it out on purpose; flagging it so nobody mistakes the silence for
having missed it.

## What the team gets from me

- **A repo built to be read by a machine cold.** `CLAUDE.md` is the map; the skills, pipelines &
  MCP tools are self-describing. The fastest way to orient is to point an LLM at the repo & ask it
  where a thing lives — that's the intended onboarding path, & it means nobody inherits a black box.
- **`/onboard`** — a command that audits a machine, says plainly what works & what doesn't, & walks
  to a first success. It's also a natural acceptance harness: the goal is the day `/onboard` finds
  nothing to complain about on a fresh machine.
- **My honest analysis as customer input** — [`packaging-strategy.md`](../../../../meta/architect/packaging-strategy.md)
  & [`CONTRIBUTING.md`](../../../../../CONTRIBUTING.md). Handed over as customer input, not as the
  design you're stuck with.
- **Me, as customer** — reachable for direction against clear milestones. Being upfront about my
  time: I steer toward the outcome & unblock decisions; I can't do daily hand-holding, so the
  project is milestone-shaped on purpose.

## Helpful background (not gatekeeping)

Comfort with git, Python & the command line; curiosity about LLMs, platform architecture & how OS differences bite real
software; & an appetite for the "make it work anywhere" kind of engineering. Nothing here is a
prerequisite — interest carries further than a checklist.

---

*Implementation backlog: issue [#27](https://github.com/diotima-garden/diotima/issues/27) — the
build backlog for this slice (PRs, good-first-issues). This brief owns the problem; the issue
tracks how it gets made.*
