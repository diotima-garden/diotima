# Customer brief — "Un-weld the Diotima core from one LLM vendor"

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
> belongs in a GitHub issue that owns this thread — **to be filed** (today the closest is
> [#22](https://github.com/diotima-garden/diotima/issues/22), which only relocates one
> vendor-specific module & is not the full refactor). The issue tracks implementation, this
> brief owns the problem.

> **One of two related zadání.** This project — "un-weld the core" — is the portability half.
> Its sibling, "make it trivially runnable" (`brief-1`), handles packaging & install. The two
> touch the same repo but are scoped to stand alone. This is the thread with the heavier design
> weight of the pair.

---

## Who's asking, & why

I'm a FIT graduate (Teoretická informatika, uid: baturvit). In my spare time — my bank job
started to bore me — I built an open-source project called **Diotima**: a context-engineering
system around a structured directory architecture, with deep integration of a spaced-repetition
database (Anki) to help a person actually learn. I use it every day. It works, & I think the
architecture is genuinely good.

The honest part: the whole thing is driven through one specific LLM harness (Claude Code). The
portable core — the tools & specifications, the part that carries the actual value — is welded to
that one vendor's wrapper, when it doesn't need to be. If a project is going to belong to the
world, it can't belong to one vendor. I don't have the time to draw that boundary cleanly alone —
which is exactly the kind of proper refactor a team can own & argue about.

## The problem

**Vendor lock.** The portable core & the vendor-specific glue are tangled together. There's no
clean seam between "the part that is genuinely Diotima" & "the part that is one company's harness."
So switching harnesses, or running under a second one, is a rewrite instead of a config change —
& that single fact quietly caps who can adopt the project & how durable it is.

## What I want (the outcome, not the how)

- **Not welded to one harness.** The portable core runs under **at least two** LLM front-ends —
  moving the project toward [opencode](https://opencode.ai) as a portable base — so switching or
  adding a harness is a config change, not a rewrite.

## Rough shape (to size it — not to design it)

Big enough for a team over a semester, & real design weight throughout:

- **Find the seam.** Separate what is genuinely vendor-specific glue from the portable core. This
  is the analysis the course exists to teach: nobody has drawn this boundary yet, & drawing it well
  *is* the project.
- **Prove it under a second harness.** Make the core actually run under a second front-end (toward
  opencode) from a single source of truth — no forked copy that rots. Two harnesses, one core.

## What "done" looks like

- The same core runs under two harnesses from the same source of truth, no forked copy.
- Adding or switching a harness is a config/boundary change a maintainer can point to — not a
  scattered rewrite.
- Verified by driving the real thing end-to-end under both harnesses, not only by "tests pass."

## Explicitly out of scope

- **Not the packaging work.** Making the install one command across three OSes is the sibling
  `zadání` (`brief-1`). This project can assume the current install path & still succeed.
- **Don't boil the ocean on providers.** "At least two harnesses, cleanly" beats "every harness,
  half-wired." The goal is a defensible seam, proven twice — not universal support.

## What the team gets from me

- **A repo built to be read by a machine cold.** `CLAUDE.md` is the map; the skills, pipelines &
  MCP tools are self-describing. The fastest way to orient is to point an LLM at the repo & ask it
  where a thing lives — that's the intended onboarding path, & it means nobody inherits a black box.
- **Prior thinking on the seam** — I've already started separating vendor glue from core (e.g. the
  `.claude/utils` extraction, the MCP-servers-as-portable-boundary pattern in
  `cross-tool-portability.md`). Handed over as customer input, not as the answer.
- **Me, as customer** — reachable for direction against clear milestones. Being upfront about my
  time: I steer toward the outcome & unblock decisions; I can't do daily hand-holding, so the brief
  is milestone-shaped on purpose.

## Helpful background (not gatekeeping)

An appetite for clean boundaries — the person who enjoys asking "what actually belongs to us vs. to
the tool we happen to run on?" Comfort with git, Python & the command line; curiosity about LLM
tooling (Claude Code, opencode) helps but isn't required — the architecture is the point, not any
one vendor.
