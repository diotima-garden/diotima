# Build Plan — `social-dynamics` grove

**Status:** design approved in architect mode; ready to implement.
**Execute in builder mode** (creating a grove modifies files under `groves/` and the
mem-bank registry — `interaction-mode-enforcement.md` requires builder mode first).

This plan is turnkey: every path, file body, and command is spelled out. A builder
session can run it top to bottom without re-deciding anything.

---

## 1. What this grove is

A training enclave for holding a strong, unbothered, playful **frame** under social
pressure — maintaining boundaries without over-explaining, justifying, or acting needy.

The grove's core is **data, not a skill**: a conversational **simulator** (throws a
scenario → you respond → it grades you) plus the **principles** that define a good
response. The drill runs as an ordinary LLM conversation. It is **text-only** — no Anki,
no external tooling — at MVP.

Decisions already locked (do not re-litigate):

| Decision | Choice | Why |
|---|---|---|
| Scope | Broad ("social dynamics") | Room for a family of drills; the dating frame-control drill ships now, siblings later. |
| Structure | **`drills/<name>/` from day one** | User's explicit choice. Each drill is self-contained (own index, rubric, versioned artifacts); the shared stance/failure-modes are hoisted to grove-root `principles.md`. |
| Anki | **No**, text-only | Skill is procedural/performance, not declarative recall. Adding a deck later needs only context files. |
| Grove inheritance (DAFNE) | **None** now | No parent groves. The reusable seam is the *drill archetype*, which becomes a real cross-grove parent only when a 2nd grove needs it — not built up front. |
| Memory privacy | Obfuscate at capture **+ `graduate:false`** | Sanitization is a soft LLM guarantee; keeping the bank local-only until trusted is the hard lever. |
| Simulator versioning | Kept as **artifacts** inside the drill; live version named in the drill's `context.md` | Non-duplication: don't copy a draft into a canonical `simulator.md`; point at the live artifact. |

---

## 2. Final directory tree

```
groves/social-dynamics/
├── context.md                                        # grove index
├── principles.md                                     # cross-cutting stance + failure modes (shared by all drills)
├── drills/
│   └── dating-frame/
│       ├── context.md                                # drill index: live artifact + rubric
│       ├── rubric.md                                 # Subtext / Leverage / Thermodynamics (this drill's grading)
│       └── artifacts/
│           └── soc-dynamic-gemini-first-attempt.md   # v1 simulator, MOVED from repo-root soc_dynamic.md — the live drill
├── research/
│   └── .gitkeep                                      # efficacy "artifact proofs", collected in later sessions
└── memory/                                           # obfuscated session bank
    ├── context.md
    ├── this-bank-prompt.md                           # the camouflage TRANSFORM
    └── big-bank/
        └── .gitkeep
```

`small-bank.md` is **not** created by hand — the mem-bank SessionEnd hook creates it on
first capture, and it is gitignored (`**/small-bank.md` already covered in `.gitignore`).

---

## 3. Steps

### 3.1 Create directories

```bash
mkdir -p groves/social-dynamics/drills/dating-frame/artifacts
```
```bash
mkdir -p groves/social-dynamics/research
```
```bash
mkdir -p groves/social-dynamics/memory/big-bank
```

### 3.2 Move the first-attempt simulator into the drill

`soc_dynamic.md` is **untracked**, so this is a plain `mv` (not `git mv`).

```bash
mv soc_dynamic.md groves/social-dynamics/drills/dating-frame/artifacts/soc-dynamic-gemini-first-attempt.md
```

### 3.3 Write `groves/social-dynamics/context.md`

```markdown
# Social Dynamics Grove

Training enclave for holding a strong, unbothered, playful frame under social pressure —
maintaining boundaries without over-explaining, justifying, or acting needy.

The grove's core is a conversational **simulator** (it throws a scenario, you respond, it
grades you) plus the **principles** that define a good response. It is text-only; drills
run as LLM conversations. Optional later tools (Anki leak-log, web-research evidence,
context-compiler) are noted as seams in the repo-root build plan, not built.

## Files in this area

| Path | What |
|---|---|
| `./principles.md` | Cross-cutting theory shared by every drill: the stance (frame vs neediness) and the failure modes to catch. |
| `./drills/` | One subfolder per training drill. Each drill is self-contained: its own index, grading rubric, and versioned artifacts. |
| `./drills/dating-frame/` | Frame-control under dating pressure (probing questions, shit-tests, late cancellations, vulnerability checks). **The only drill so far.** |
| `./research/` | Collected efficacy evidence ("artifact proofs") on whether such simulations work. Empty until gathered. |
| `./memory/context.md` | Memory bank — obfuscated session history. Captures the abstract training signal only; strips names and identifying detail. |
```

### 3.4 Write `groves/social-dynamics/principles.md`

```markdown
# Principles — Social Dynamics

The durable stance every drill in this grove trains toward. Drill-agnostic; each drill's
concrete grading rubric lives in its own folder (`drills/<name>/rubric.md`).

## The stance
Hold a strong, unbothered, playful frame under pressure. Security is signaled by *not*
needing a particular reaction from the other person. Neediness leaks through
over-explaining, justifying, and treating a test as if it were a threat.

## Failure modes to catch
- **Over-explaining** — supplying reasons no one asked for.
- **Justifying** — defending yourself against a test instead of holding frame.
- **Neediness** — handing your emotional state to the other person to manage.
- **Reactivity** — matching their energy instead of setting the temperature.
```

### 3.5 Write `groves/social-dynamics/drills/dating-frame/context.md`

```markdown
# Drill — Dating Frame-Control

Holding a strong, unbothered, playful frame under dating pressure: probing questions,
shit-tests, late cancellations, vulnerability checks. The simulator throws a scenario,
you respond, it grades you against `./rubric.md`, reports how the other party would likely
feel receiving your reply, then escalates.

| Path | What |
|---|---|
| `./rubric.md` | This drill's grading dimensions: Subtext / Leverage / Thermodynamics. |
| `./artifacts/soc-dynamic-gemini-first-attempt.md` | v1 simulator — first draft, produced with Gemini. **Currently the live drill.** |

Shared stance and failure modes live one level up in `../../principles.md`.
```

### 3.6 Write `groves/social-dynamics/drills/dating-frame/rubric.md`

```markdown
# Rubric — Dating Frame-Control

How a response in this drill is graded. Drill-specific: a different boundary drill
(e.g. saying-no-at-work) would define its own dimensions. If a second drill ends up
reusing these verbatim, promote them to `../../principles.md`.

- **Subtext** — does the response signal security or neediness? Any over-explaining?
- **Leverage** — was power handed over, or was the frame maintained?
- **Thermodynamics** — was the response clean and elegant, or bloated and reactive?

After grading, the simulator reports how the other party would likely feel receiving the
reply, then escalates to the next scenario.
```

### 3.7 Write `groves/social-dynamics/memory/context.md`

```markdown
This directory carries memories generated by the mem-bank subsystem for this grove.

| Where | What |
|---|---|
| `./this-bank-prompt.md` | Capture transform — what qualifies for capture and how it is de-identified. |
| `./small-bank.md` | Active context of recent training sessions (obfuscated, local-only). **Read it now** if present. |
| `./big-bank/` | Deep history. **Don't read unless deep area memory is needed.** Empty until graduation is enabled. |
```

### 3.8 Write `groves/social-dynamics/memory/this-bank-prompt.md`

This is a **transform**, not a filter — it deliberately inverts the Spanish reading-log
bank (which captures user input *verbatim*; that would defeat obfuscation here).

```markdown
This is the social-dynamics training bank. It records how boundary-setting drills went
and what patterns surfaced — the abstract training signal only, never personal specifics.

ALWAYS capture (never SKIP) sessions that ran a drill, reflected on a real social
situation, or changed the simulator/principles. For anything else (infrastructure,
unrelated work), respond with exactly SKIP.

When you capture, TRANSFORM the content — never record it verbatim:
- Remove all real names; use neutral roles (a colleague, a date, a friend, a family member).
- Strip identifying details: places, employers, locating dates, distinctive events.
- Keep only the ABSTRACT structure: the pressure/test applied, the response pattern used,
  where the frame held or leaked, and the lesson.
- Never quote either party verbatim; paraphrase into de-identified terms.

Structure each entry as:
SITUATION (abstracted):
<the test in de-identified terms>
RESPONSE PATTERN:
<the frame move; where it held or leaked>
LESSON:
<the training takeaway>
```

### 3.9 Placeholder files so empty dirs are tracked

```bash
touch groves/social-dynamics/research/.gitkeep
```
```bash
touch groves/social-dynamics/memory/big-bank/.gitkeep
```

### 3.10 Register the memory bank

Add one entry to `.claude/mem-bank/subscriptions.json` (in the `"banks"` array):

```json
{
  "name": "social-dynamics",
  "bank": "groves/social-dynamics/memory",
  "graduate": false,
  "patterns": ["social-dynamics/.*"]
}
```

Two things here are load-bearing — do **not** drop them:

- **`graduate: false`** — mirrors the Spanish reading-log bank; keeps the bank local-only
  until the obfuscation is trusted (the hard privacy lever).
- **`patterns` override is required** — do NOT rely on the default. The capture hook
  (`small-bank.py`) matches each pattern against the session transcript via
  `transcript.matched_any(...)`, which matches the **file paths a session reads**
  (verified: the `meta` bank's `meta/.*/context\.md` fires because a session reads
  `modes/meta/architect/context.md`). The default pattern resolves to
  `groves/social-dynamics/memory/context\.md` (see `registry.py::bank_effective_patterns`),
  but a **drill session reads the grove index, the drill files, and the simulator artifact —
  never `memory/context.md`**. So the default would make capture **silently never fire**.
  The override `social-dynamics/.*` fires on any grove file a drill touches (index,
  `principles.md`, the drill's `context.md`/`rubric.md`, or the artifact); the
  `this-bank-prompt.md` SKIP rule is the relevance backstop for non-drill sessions that
  merely mention the path.

`.gitignore` already ignores `**/small-bank.md`, so no gitignore change is required.

---

## 4. Verification

1. `git status` shows: `soc_dynamic.md` gone from root; new files under
   `groves/social-dynamics/`; modified `.claude/mem-bank/subscriptions.json`.
2. `python3 -c "import json; json.load(open('.claude/mem-bank/subscriptions.json'))"`
   parses clean (valid JSON, no trailing-comma error).
3. The `social-dynamics` bank appears in the registry — grep the file for
   `"social-dynamics"` and confirm the `patterns` override is present (not the default).
4. Optional smoke test of capture: run any session that mentions a drill, end it, and
   confirm the SessionEnd hook creates `groves/social-dynamics/memory/small-bank.md`
   with an obfuscated (SITUATION/RESPONSE/LESSON) entry — **not** verbatim text.

---

## 5. Deferred — seams, not work

Do **not** build these now. They cost nothing to add later because the grove format is
domain-agnostic (adding capability = adding context files, zero orchestrator changes).

- **A second drill:** create `drills/<name>/` with its own `context.md`, `rubric.md`, and
  `artifacts/`. The moment a second drill reuses the frame-control rubric verbatim, promote
  those dimensions up to `principles.md` (extract-the-shared-thing-when-a-2nd-consumer-appears).
- **Anki leak-log (maturity-2):** once real drills accumulate, your own graded *failure
  patterns* become spaced-repetition cards. Analogous to the Spanish feedback loop. Not
  the theory — the personal leaks.
- **`research/` evidence:** later sessions use WebSearch/WebFetch to gather proof of
  whether such simulations are effective; drop the findings here as artifact proofs.
- **`context-compiler`:** only if a drill's prompt becomes *layered* (persona + rubric +
  principles compiled into one deployable prompt). Today it's one self-contained artifact —
  no compile step.
- **Simulator versioning:** as a drill matures, add new files under its `artifacts/`
  (e.g. `soc-dynamic-v2.md`) and update the "live drill" pointer in that drill's
  `context.md`; note the lineage in the memory bank.
- **Cross-grove inheritance (DAFNE):** the drill archetype (scenario → response →
  graded-rubric → reflect) becomes a real parent node only when a *second grove* wants it.
  Handle during the DAFNE migration, not now.

---

## 6. One-line summary for the builder

> Create `groves/social-dynamics/` with `context.md`, `principles.md`, a
> `drills/dating-frame/` folder (`context.md` + `rubric.md` + `artifacts/` holding the moved
> `soc-dynamic-gemini-first-attempt.md`), an empty `research/`, and a `memory/` bank
> (`context.md` + obfuscating `this-bank-prompt.md` + empty `big-bank/`); register the bank
> in `subscriptions.json` with `graduate:false` **and a `["social-dynamics/.*"]` patterns
> override** (the default never fires for drill sessions). Text-only, no grove inheritance,
> everything else deferred.
