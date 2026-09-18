# Grove Orientation — closing the loop on session-start injection

*Created 2026-09-18. Architect-owned design record, prompted by two live reports in the
same session: (1) a grove session responded to "let's continue our work" by checking
master's git status instead of the grove; (2) opening a grove from a multi-grove
session requires the model to notice and follow a prose pointer (`DAFNE.md` → "Read
`./memory/context.md`" → that file's "read small-bank.md now") rather than getting the
content handed to it. Companion to `bank_discovery_wiring.md`, whose machinery this
reuses read-side instead of write-side, and to `grove_sync.md`, whose Path-in/data-out
module shape this copies.*

*This is not a new question. `diotima-garden/diotima#25` asked exactly this — "should
small-bank context be read semantically, or injected via hook + session_crawler?" —
against the same reasoning ("the same risk applies symmetrically on the read side [as
the write side]") and named the same two blockers this document resolves: it is gated
on `diotima-garden/diotima#24` (context.md is copy-pasted per bank, drifting) and on
`diotima-garden/mneme#8` (the trigger layer is regex-over-raw-text, which is why the
banks are empty). This document is the resolution of #25, arrived at independently and
converging on the same mechanism; the citations below connect it back rather than
re-deriving what was already filed.*

---

## What actually happened (not what it looked like)

The report was "it drifted into builder-mode behavior uninvited." That's not what the
evidence shows. `social-dynamics/memory/small-bank.md` is 0 bytes — verified this
session. `spanish/reading-log/small-bank.md` does not exist at all — also verified.
Both grove banks that exist in production have never captured anything. When the user
said "let's continue our work," there was nothing grove-level in the injected context
to continue with; master's dirty git status (visible in every session regardless of
subject, since `bin/diotima` never changes `cwd`) was the only concrete "our work" on
offer, and the model took it. **This is a context vacuum, not a mode failure** — the
model went to the only referent it had.

That reframing matters for the fix. The answer is not a rule telling the model to
prefer the grove ("stay in user mode unless asked"). `structural-lessons.md`'s own
rule cuts against that instinct — one sentence competing against master's `CLAUDE.md`,
its mode-navigation table, and every session's ambient git-status block is exactly the
decay pattern this project has already burned itself on. The fix is to put something
real and grove-level into context so there is something to continue.

## Why the vacuum exists — the capture side is silently dead

Both grove banks default their capture pattern (`bank_effective_patterns` in
`plugins/mneme/registry.py:15-20`) to `<bank>/context\.md` — a static, hand-authored
index file whose own text says "read small-bank.md now if present." A normal drill or
reading session never touches that index file. `session_crawler/crawler.py`'s pattern
match runs only against tool paths and Bash command text appearing in the transcript
(`_candidate_strings`, `crawler.py:41-62`); nothing about running a social-dynamics
drill or a Spanish reading session touches `memory/context.md` /
`reading-log/context.md`, so `matched_any()` is false every time, `small-bank.py` never
queues a job for either bank, and nothing has ever been captured. No error, no log line
pointing at it — exactly `structural-lessons.md`'s "silent failure is this system's
default failure mode."

This default most likely made sense for the bank it was designed against first
(`modes/meta/memory` — architect/builder sessions edit `context.md` files constantly)
and was carried over to grove banks without re-deriving what "capturable activity"
looks like in a grove's own domain.

**Not fixed here — and not a per-grove regex-tuning problem either.**
`diotima-garden/mneme#8` already diagnosed this exact failure mode (regex-over-raw-text
trips on a path merely being *printed*, and misses real edits that don't happen to name
`context.md`) and designed the structural fix: typed `triggers_on` kinds
(`owns`-subtree membership, write-vs-read, mode/command signals) with regex kept only
as the permissive catch-all. Retuning social-dynamics' or spanish's `patterns:` string
would just relocate today's bug to a slightly different string; #8's fix is what
actually closes it. Recorded as a finding pointing at existing prior art, not changed
here.

## The fix that's actually available: read-side reuse of Phase 3's own machinery

`bank_discovery_wiring.md` already wired the write side: `discover_banks()` (dafne)
resolves a grove's declared `bank:` path to absolute, `bank_union.py` (orchestrator)
hands the merged list to mneme's `run_hook(banks=...)` at session end. The read side
never got the equivalent treatment — `session-start.py` injects the raw `DAFNE.md` text
and stops, leaving "also check whether a bank exists and read its live content" as a
**prose instruction inside the manifest body** for the model to notice and act on.

The reuse is exact and requires no new engine work, verified this session:

- `plugins/dafne/manifest.py:106-131` `discover_banks(node_root)` — already returns
  each bank's `bank:` key as an absolute path.
- `plugins/mneme/registry.py:46-52` `populated_banks(banks, cwd=None)` — already
  returns `(bank_cfg, small_bank_path)` for every bank whose `small-bank.md` exists
  **and is non-empty**. Exactly the predicate this needs; zero new path-convention code.

So: the orchestrator asks dafne for the grove's banks, asks mneme which of them are
populated, reads those files, and injects their content next to the manifest — the same
"orchestrator is the only place the two vocabularies meet" shape `bank_discovery_wiring.md`
already established, run in the opposite direction.

Because both grove banks are empty today, this fix's visible effect is subtler than
"less git-status drift": the hook can say plainly *"no grove-side memory captured yet,
no uncommitted grove changes"* — a true, boring fact — instead of the model substituting
master's unrelated dirty tree because nothing else was offered. It becomes fully
load-bearing the moment the capture-pattern finding above is fixed in a grove repo and
banks start actually filling.

## A consequence found during the build: it further narrows the already-dead capture trigger

*Raised by the user during `orient.py`'s implementation, 2026-09-18; verified against
the code before writing this down.* `plugins/mneme/session_crawler/crawler.py`'s
`_candidate_strings()` yields text from exactly two places: a `user`-type transcript
event's message text, and an `assistant`-type event's `tool_use` inputs (`file_path`/
`path`/`pattern`, plus `Bash` command text). A `SessionStart` hook's `additionalContext`
is neither — it is never scanned. So the bank content `orient.py` now injects directly
leaves no candidate string for `bank_effective_patterns`' regex
(`social-dynamics/memory/context\.md`) to match against.

This does not regress capture for actual grove usage: per the section above, a normal
drill session never called `Read` on `context.md` either, so `matched_any()` was already
false for every real drilling session before this fix — that is the documented reason
both grove banks are empty today. What it does narrow is a second, unplanned path that
existed only by accident: an *investigative* session (architect/builder work inspecting
a grove, e.g. this one) that manually walked `DAFNE.md` → `context.md` → `small-bank.md`
via real `Read` calls left a matching tool-use path each time, incidentally. `orient.py`
now performs that navigation for the model, so that accidental trigger disappears too.

Not fixed here, same reasoning as the section above: this is another instance of
`diotima-garden/mneme#8`'s actual defect (regex-over-raw-text requires a tool-use event
that happens to carry the literal string; it was never a reliable signal for "this
session engaged with the grove's memory," accidentally-working or not). `#8`'s typed
`triggers_on` design (`owns`-subtree membership, write-vs-read, mode/command signals)
is what would let a session that received orientation via the hook still count as
"engaged with this grove" — closing this gap is the same un-defer trigger as the
original one, not a new one.

## Fresh and empty banks must read as boring, not broken

Both grove banks being empty today is the normal state of a fresh or rarely-triggered
bank, not a failure — and neither the mechanical path nor the fallback prose path may
present it as alarming.

**Mechanical path:** already handled, by construction. `populated_banks()` (mneme)
filters to non-empty banks only, so `orientation_for()` simply has nothing to append
for an empty or missing `small-bank.md` — no branch that could mis-render a missing
file as an error. Its exit criterion above already commits to stating the empty case
as a plain fact ("no grove-side memory captured yet").

**Prose fallback path — not a mneme concern.** Until the mid-session CLI ships (and for
any human reading a bank directory directly), the per-bank `context.md` is still the
thing a reader hits, and every copy today unconditionally says "Read it now" with no
acknowledgment that the file can be absent or empty. This is presentation, not capture
mechanics — mneme's registry already exposes the fact (`populated_banks`); it should
not also own explaining it to a reader. The right layer is the same one that owns the
file: `context.md` itself gets one added sentence, in each existing copy, saying that
empty/missing means nothing has been captured yet and that's expected, not a bug.

This directly collides with `diotima-garden/diotima#24` — every `context.md` is already
a hand-copied near-duplicate with documented drift (that issue's own example: the
social-dynamics copy has an extra `this-bank-prompt.md` row the others lack). Adding a
fifth hand-edit site is exactly the pattern #24 wants to kill. The call made here:
**add the sentence now, identically worded across all four existing copies, as a
stopgap** — it is small enough that #24's eventual centralization absorbs it verbatim
with no rework, and leaving four copies actively misleading until #24 is picked up is
worse than four copies of one more identical line. Editing four files is not the same
scale of problem as the boilerplate table this issue is actually about.

## The second real signal: the grove's own git status

Groves are separate repos (Phase 2). `bin/diotima` deliberately keeps `cwd = master`
for the whole session (`bin/diotima:24-30`, the `.claude/settings.json`-load
requirement), which means the ambient git-status block every session already carries is
**always about master**, never about the grove — even in a session whose entire
subject is one grove. That's a second, independent source of the same vacuum: the one
git signal in view is structurally guaranteed to be irrelevant to "our work" in a grove
session.

Fix: `session-start.py`, when the subject is a single grove, also runs read-only git
commands **against the grove's own repo** (`cwd=grove`, never `git -C`, matching
`grove_sync.py`'s own convention) and injects that alongside the manifest and bank
content. This is a factual correction of a misleading ambient signal, not a directive —
closer to `grove_sync.md`'s "report the exception" posture than to a behavioral rule.
Check before writing a second git-status reader: `grove_sync.py`'s `status()` already
computes most of this for the sync decision (non-duplication).

## Layer placement and API shape

New module, orchestrator-owned (same layer as `bank_union.py`, `grove_sync.py`) —
and the same shape `grove_sync.md` already ruled on for exactly this reason: *"The
module returns data; it does not print. Formatting belongs to whoever calls it."*
The hook injects into `additionalContext`; the mid-session CLI prints for a model
reading stdout. Those are two different framing needs, and a string-returning
function would bake one caller's formatting choice into the data layer, foreclosing
the other. Split it the way `grove_sync.py` splits `GroveStatus`/`status()` from its
callers:

```python
# system/diotima/orient.py (name open)
@dataclass(frozen=True)
class GroveOrientation:
    manifest_text: str
    populated_banks: list[tuple[dict, str]]   # (bank_cfg, small_bank_content)
    git_status: str | None                    # None = clean, nothing to report

def orientation_for(grove: Path) -> GroveOrientation:
    """Gathers manifest + populated-bank content + this grove's own git status.
    Takes the resolved grove directly -- does not call resolve_subject() itself,
    so the hook and the mid-session CLI share one function with two different
    callers deciding scope."""
```

`session-start.py` calls `orientation_for()` with the already-resolved subject, in the
single-grove branch only (the garden-listing branch has no one grove to report on, per
the existing `context_for()` split), then formats the result into `additionalContext`
text. The mid-session CLI (below) calls the same function and formats for stdout. The
exit criterion's "byte-for-byte match" now means the two formatters produce identical
text for identical input, not that there is only one formatter — worth keeping as one
shared formatting function too, once a builder session finds out whether the hook and
CLI framing needs actually turn out to differ. No change to `garden.py`'s own
scope-resolution, per its docstring commitment to being the one place `$DIOTIMA_GARDEN`
is read.

## The other half: mid-session grove switching gets the same call, not a second path

Today, opening a grove from a multi-grove/garden session is pure LLM judgment end to
end: notice the user named a grove, find its `DAFNE.md`, read it, notice the "Read
`./memory/context.md`" line, follow it, notice *that* file's "read small-bank.md now"
line, follow that too. Three hops of prose-dependent navigation for something
`orientation_for()` above already does in one call.

Fix: a thin CLI wrapper (`python3 system/diotima/orient.py --grove <path>`, whitelisted
read-only per `security.md`'s repeatable-command contract) that calls the same
function. Deciding *which* grove the user means is genuinely judgment — that stays with
the model, unavoidably. Executing "gather that grove's full orientation package" once
the decision is made should not be. This is exactly the rules-vs-hooks test in
`architect/context.md`: judgment triggers a deterministic call, never a second
hand-written prose chain.

Follow-up, out of scope for master: once this ships, each grove's `DAFNE.md` "Read
`./memory/context.md`" line is redundant for the model (still fine as human-facing
documentation) and can be trimmed — a separate-repo change, one per grove, same shape as
Phase 3.5's cleanup sweep.

## A related building block, found but not proposed for use

`plugins/mneme/session_crawler/crawler.py:21-22,65-72` already defines "did this session
enter architect/builder mode" **mechanically** — `_detect_mode_from_events` scans
transcript tool-use paths for `meta/architect/context\.md` / `meta/builder/context\.md`
and returns the first match, first-indicator-wins. This is currently consumed only
post-hoc, for capture routing at session end. It is the exact primitive a live
PreToolUse gate would need if this project ever wants to *enforce* "no orchestrator-level
action before mode is entered" mechanically rather than by prose — reusing the same
regex, not a new mode-definition.

**Not proposed here.** Blocking bare git commands on a grove session outright risks a
real false positive (a user legitimately checking master), and there is exactly one
reported instance so far — the vacuum fix above may well remove the incentive on its
own. Recorded as a door, not a bullet.

## Exit criteria

- A fresh single-grove session's injected context includes the grove's manifest, the
  content of every populated bank (verified against an intentionally-seeded
  `small-bank.md`, since both real banks are empty today), and the grove's own
  `git status`/last commits — with nothing about master's tree.
- A garden/multi-grove session, told to work with grove X, produces the identical
  three-part block via one CLI call, byte-for-byte matching what the hook would have
  injected had the session launched inside that grove directly.
- Neither `orient.py` nor `session-start.py` calls `resolve_subject()` more than once
  per session; the CLI path takes its grove as an argument.
- `system/diotima/tests/` gains coverage for: a grove with no banks, a grove with one
  empty bank, a grove with one populated bank, a grove with a dirty tracked file (git
  status appears), a grove that's clean (git status block says so plainly).

## Doors held open, nothing built

| Door | Trigger | Pre-paid by |
|---|---|---|
| Live PreToolUse mode gate | a second real instance of orchestrator-level drift after the vacuum fix ships | `crawler.py`'s existing mode regexes |
| Trigger-layer rework (fixes the actual capture-pattern defect) | `diotima-garden/mneme#8` gets picked up | that issue's `owns`/`triggers_on` design, already complete |
| Centralize `context.md` as one template instead of N copies | `diotima-garden/diotima#24` gets picked up | this document's stopgap sentence is written to be absorbed verbatim, not reworked |
| Trim `DAFNE.md`'s prose memory-pointer | `orient.py` ships and is verified end-to-end | this document |
| Give hook-injected orientation its own capture signal (`orient.py` reading a bank leaves no tool-use trace for the regex to match — narrower than before this fix, not just still-broken) | `diotima-garden/mneme#8` gets picked up | the "consequence found during the build" section above |

**Correction while reviewing prior art:** the trigger-layer issue (#8) lives in
`diotima-garden/mneme`, but the context.md-duplication issue (#24) and its sister
read-strategy issue (#25) both live in `diotima-garden/diotima` (the parent org repo,
not mneme) — worth knowing before searching the wrong repo a second time.

## Open decision for the user

Where this lands in `dafne_plan.md`: Phase 3 bullet 3 ("manifest injection at session
start") is checked off and executed as scoped — it never promised bank content or a
mid-session equivalent, so reopening it would make the plan lie about what it verified.
Proposing this as a **new Phase 3 bullet 5** (bullet 4 is the deferred assisted-update
item) rather than folding into bullet 3. Not editing `dafne_plan.md` yet — that edit,
and the builder-mode session to execute this, wait on the user's sign-off.
