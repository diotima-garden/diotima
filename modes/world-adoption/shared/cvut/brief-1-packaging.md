# Customer brief — "Make Diotima trivially runnable"

> **Draft scaffold, not a final send.** AI-assisted, written to your voice (`voice.md`) —
> run the read-aloud test and rework by hand before this reaches Mlejnek or any student.
> Language: English, matching `cvut_mail.txt`. Whether the version students see should be
> Czech is an open decision (Mlejnek formalizes the official `zadání` either way).
>
> This is a **customer brief**: it states the problem I want solved and what "done" feels
> like. The requirements analysis and the design are the team's to make — that is the part
> the course is there to teach, so I deliberately don't pre-solve it here.

> **Source of truth.** This brief is the customer problem statement — the canonical scope &
> "what done looks like" that Mlejnek formally lists as the BI-SP1 `zadání`, and it stays
> stable for the semester. The *build backlog* (how it gets made, PRs, good-first-issues)
> lives in GitHub issue [#27](https://github.com/diotima-garden/diotima/issues/27); that
> issue tracks implementation, this brief owns the problem. The issue is written at
> contributor altitude & names approaches I've weighed — read it as *customer input*, not as
> the design you're handed.

> **One of two related zadání.** This project — "make it trivially runnable" — is the
> packaging half. Its sibling, "make the core provider-agnostic" (`brief-3`), is a separate
> team project. The two touch the same repo but are scoped to stand alone.

---

## Who's asking, & why

I'm a FIT graduate (Teoretická informatika, uid: baturvit). In my spare time — my bank job
started to bore me — I built an open-source project called **Diotima**: a context-engineering
system around a structured directory architecture, with deep integration of a spaced-repetition
database (Anki) to help a person actually learn. I use it every day. It works, & I think the
architecture is genuinely good.

The honest part: it works *on my machine*. What exists today is closer to a bare OS kernel with
a few example apps bolted on than to something a normal person installs & uses — a handful of
apps & APIs talking to each other on my PC, a power-user setup, not a product. The job, put
bluntly, is turning that kernel into something like Ubuntu. That gap between "works for me" &
"works for anyone" is the single thing standing between the project & real adoption, & I don't
have the time to close it alone. Quite a shame, considering the potential — which is exactly
why it's a good thing for a team to take on.

## The problem

**Setup friction, & it's OS-lopsided.** A newcomer today has to hand-assemble git submodules,
Python environments, & configuration paths before anything runs — & some of those paths are
OS-specific. Everything was built & tested on **Linux**; a handful of people have working
**macOS** instances; **Windows** is, honestly, completely unaddressed. Installing it is a small
adventure, not a command. Every hour a curious person spends fighting the install is an hour
they're not spending learning — & most won't spend it at all; they'll just leave.

## What I want (the outcome, not the how)

- **Clone & one command.** Someone with the honest prerequisites already in place goes from
  nothing to a first real success in minutes, on **Windows, macOS & Linux** alike — no manual
  environment surgery, no per-OS path editing.

## Rough shape (to size it — not to design it)

Big enough for a team over a semester:

- **Packaging & bootstrap** — turn the hand-assembled dance into a reproducible install &,
  ultimately, a single artifact. The problem surface here is bounded & I've already done an
  *honest customer-side analysis* of it — see [`packaging-strategy.md`](../../../meta/architect/packaging-strategy.md).
  **I hand that over as customer input, not as the answer.** The team owns validating it,
  choosing an approach, & defending the choice.
- **Cross-OS honesty** — the interesting engineering here is where OS differences bite real
  software: paths, environments, line endings, the things that quietly work on one machine &
  break on another. Making one install behave the same on three OSes is the meat of the work.

## What "done" looks like

- A person on any of the three OSes runs the documented command(s) & reaches a first success,
  with no hand-editing of paths or environments.
- The install is reproducible on a machine that isn't mine — verified by driving the real thing
  end-to-end, not only by "tests pass."

## Explicitly out of scope

- **Don't package the content.** Diotima separates the *runtime* (the player) from *groves*
  (the content/knowledge areas). This work packages the **runtime only** — grove adoption stays
  a separate, already-simple step. Baking today's groves into the installable would fight an
  extraction that's already underway.
- **No rebuild-for-distribution.** The surface is smaller than it looks; this is not a from-scratch
  redistributable.
- **Not the provider-agnostic refactor.** Un-welding the core from one LLM harness is the sibling
  `zadání` (`brief-3`), not this one. This project can assume the current harness & still succeed.

## What the team gets from me

- **A repo built to be read by a machine cold.** `CLAUDE.md` is the map; the skills, pipelines &
  MCP tools are self-describing. The fastest way to orient is to point an LLM at the repo & ask it
  where a thing lives — that's the intended onboarding path, & it means nobody inherits a black box.
- **`/onboard`** — a command that audits a machine, says plainly what works & what doesn't, & walks
  to a first success. It's also the acceptance harness: the goal is the day `/onboard` finds nothing
  to complain about.
- **My honest analysis** (`packaging-strategy.md`, `CONTRIBUTING.md`) as customer input.
- **Me, as customer** — reachable for direction against clear milestones. Being upfront about my
  time: I steer toward the outcome & unblock decisions; I can't do daily hand-holding, so the brief
  is milestone-shaped on purpose.

## Helpful background (not gatekeeping)

Comfort with git, Python & the command line; curiosity about how OS differences bite real software;
& an appetite for the "make it work anywhere" kind of engineering.
