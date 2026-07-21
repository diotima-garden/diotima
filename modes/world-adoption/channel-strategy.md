# Channel Strategy — where feedback & developers actually come from

Provenance: Gemini 2.5-pro strategic consult, 2026-07-21 (driver:
`scratchpad/consult_gemini.py`, one-off). Bundled the whole picture — project
context, the CVUT per-subject outreach strategy, and the three tailored letters —
and asked: *is this an effective way to get **feedback** and **developers**?*
This file is the durable verdict + the resulting channel plan.

## The verdict in one line

> "A well-designed flyer in the wrong building." The letters are good; the *audience*
> is mismatched. Professors convert into *feedback* and *developers* poorly — at best
> into "maybe a student picks it as a thesis," which is slow (3–9 mo, semester-bound),
> high-maintenance for a time/health-constrained solo dev (you become the mentor), and
> high-dropout (worsened by the "works on my machine" state).

**Tempering (context Gemini lacked):** we're *already* running developer-community
outreach — live r/Anki, r/AnkiAi, r/AnkiLanguageLearning threads, Salitur as a real
lead. So "pivot to Reddit" isn't a pivot; it's already in motion and should be the
*primary* channel. The university push is a *parallel, second* bet — and its real
payoff isn't developer-recruitment (where the critique holds) but **institutional
backing + local relationships**, which HN/Reddit can't give. Different scorecard;
keep it, but don't over-invest scarce time there.

## Primary channel: Reddit + developer communities  ← focus here

Order roughly by contributor-value × fit. Every post goes through the outbound
contract / `prepare-human-facing-content` (venue rules first — several of these are
self-promo-strict).

| Community | Lead angle | Status / note |
|---|---|---|
| **r/LocalLLaMA** | "Directory structure as a context-engineering framework for LLMs" — the DAFNE / grove idea. Crowd that *builds*, most likely to yield contributors. | **NEW — highest contributor value.** Lead with the technical idea, not the Anki feature. |
| **r/opensource** | Explicit "looking for contributors" post pointing at the contributor backlog (cross-platform, packaging, provider-agnostic core). | **NEW.** Needs P0 done first (see below) or it bounces. |
| **Show HN (Hacker News)** | "Show HN: an AI learning conductor to automate my Anki workflow" — link the repo, ask for feedback directly. | **NEW — highest ceiling** per Gemini (thousands of views, real comments in a day). One shot; time it after P0. |
| **r/Anki** | Learning/workflow: batch card-gen + trust machinery + reverse feedback loop. | **ALREADY ACTIVE** — main post + comment replies; Salitur lead. Keep nurturing. |
| **r/AnkiAi** | AI×Anki intersection — direct fit. | **ALREADY ACTIVE.** Monitor for solution-shaped threads. |
| **r/AnkiLanguageLearning** | Language-learner angle (Spanish grove worked example). | Cross-post **stalled** (never approved). Decide: retry vs. drop. |
| **r/selfhosted** | "Self-hosted learning stack, runs on your machine." | **NEW** — moderate fit; **do not post until docker/onboarding exists** (audience will try to run it). |
| **r/programming** | A single high-quality technical *article* (architecture story), not a pitch. | **NEW** — strict self-promo rules; only viable with a real blog post as the artifact. |

**Sequencing rule:** the communities whose readers will *try to run it*
(r/opensource, r/selfhosted, r/programming, HN) must come **after** onboarding is
fixed. The Anki-flavored subs (already active) don't gate on that.

## P0 — the gate before the run-it-yourself channels

Highest-leverage use of scarce time, per the consult: **lower the barrier to entry
before recruiting.**
- `docker-compose up` (or equivalent single-command dev env) — "works on my machine"
  is a contributor death sentence.
- `CONTRIBUTING.md` with 3–5 tagged **good first issues** drawn from the existing
  contributor backlog (cross-platform paths, packaging, opencode/provider-agnostic).

## Secondary bet: CVUT professors (keep, right-size)

- Send **softwarovy tymovy projekt** — strongest, concrete, solves a problem he has. Best shot.
- **Algoritmy data miningu** — reworked so "only my own data" reads as a growing pipeline + working
  starting point, not a viability red flag.
- **Architektonické a návrhové vzory** — reworked so the ask is concrete (case-study OR thesis comparing ad-hoc
  solutions to standard patterns), not abstract self-praise.
- All three **reworked hook-first** (tailored ask + repo link lead; boilerplate after)
  — a scanning professor now hits the personalized reason in sentence one.
- Don't burn time drafting the other 18 yet; gate further sends on responses to these.

## Open decisions

- r/AnkiLanguageLearning cross-post: retry or abandon (stalled since ~7-13).
- Who owns P0 — is packaging itself a task to hand a student team (Mlejnek) *or* a
  prerequisite you do first so the Reddit dev-channels land? (Chicken-and-egg worth
  resolving.)
