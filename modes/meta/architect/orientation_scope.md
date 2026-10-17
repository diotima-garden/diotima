# Orientation Scope — what a session's subject means, and what a node is called

*Created 2026-10-17. Architect-owned design record, prompted by one live report: a
session launched deliberately from inside `social-dynamics/parents/behavior-rewiring`
was asked "what groves are you aware of?" and answered by enumerating the whole garden
— `ls $DIOTIMA_GARDEN/..`, a recursive `find` for every `DAFNE.md`, frontmatter of all
ten manifests, `.gitmodules` of every consumer. The expected answer was one sentence:
"behavior-rewiring, because that is where diotima was launched from."*

*Direct successor to `grove_orientation.md`, which gave the hook its content (manifest +
populated banks + grove git state). This document is about its **framing**: what the
injected package claims about the rest of the world, and what it calls the thing it is
describing. Does not reopen that design — every mechanism below is an addition to its
output, not a change to it.*

---

## What actually happened (not what it looked like)

The first-instinct diagnosis was that `DIOTIMA_GARDEN` misled the session: a variable
named *garden* pointing at `…/parents/behavior-rewiring` invites "the real garden must
be elsewhere, let me go find it." **That is not what fired.** In the transcript,
`echo $DIOTIMA_GARDEN` and `ls -1 /home/papa/Documents/diotima-garden/` were issued in
the *same parallel tool block* — the garden root had already been derived by truncating
the path printed in the orientation text, and the decision to enumerate was already
made, before the variable's value was ever read. The name is a latent hazard (§6); it
is not this incident's cause.

Three things are:

**1. The orientation states position, never scope.** `format_orientation()` emits "You
are in grove `X` (path)", the manifest, bank content, git state. Nothing anywhere in the
injected package says *this node is the session's subject, and the garden is not in
play*. A question of the form "what do you know about?" therefore has no stated bound,
and the model supplies the widest one that the filesystem permits.

**2. `CLAUDE.md` promises the opposite, in the always-loaded layer.** Its Navigation row
reads: "launch via `bin/diotima` and the `SessionStart` hook lists what's in the garden
with full paths." In a node-subject session that is simply false — the hook took the
grove branch and listed nothing. A model reconciling a doc/observation mismatch goes and
looks. This is the more serious of the two: it is not a missing statement but a wrong
one, loaded every session, in the file that is supposed to be the orientation of record.

**3. The vocabulary contradicts itself inside one injection.** The hook's own first line
says "You are in grove `behavior-rewiring`". The manifest it prints immediately below
says "This node declares no `banks:`, so it is a bare node and not a grove." The user
felt the same seam in the question itself — *"what groves are you aware of? or not
groves but nodes."* Two definitions are live in the tree with no canonical home:

| Definition | Where it lives | Says |
|---|---|---|
| Manifest presence | `system/diotima/garden.py:is_grove()` | `DAFNE.md` exists → grove |
| Bank declaration | every production `DAFNE.md`'s own prose | declares `banks:` → grove; otherwise a *bare node* |

Current tree under that second definition: **groves** = `spanish`, `social-dynamics`;
**bare nodes** = `english`, `instruments` (top-level, launchable, bank-less),
`language` ×2, `deck` ×2, `behavior-rewiring`. Non-duplication's diagnosis applies —
a concept with two definitions has not found its canonical home.

---

## The fix — three changes

### 1. Scope framing, emitted by the hook, in both branches

Home is **`system/diotima/session-start.py`**, *not* `format_orientation()`. The
non-duplication instinct points at the shared formatter, and it is wrong here:
`format_orientation()` has a second caller, `orient.py --grove X`, which exists
precisely so a session can deliberately look at a *different* node mid-flight. Emitting
"other nodes are out of scope" from that CLI would be a lie. `orient.py`'s own docstring
already rules the split — *"a caller decides scope exactly once… the hook passes its
already-resolved subject."* **Scope is a session fact, not a grove fact.** The formatter
renders the package; the hook frames it.

- *Node branch* — the subject is this node; the garden was **not** enumerated and is not
  in scope; "what do you know" is answered from this manifest; bringing another node in
  means relaunching `bin/diotima` from it.
- *Garden branch* — the symmetric statement: the subject is the garden, and these are
  its nodes.

### 2. One definition of grove vs. node, emitted correctly

**Do not change discovery.** `english` and `instruments` are bank-less by the manifest
definition but are legitimate launchable subjects and must keep appearing in
`garden_listing()`. The predicate is really *"is a launchable subject"* — rename
`is_grove()` to say so, or document it as such in `garden.py`, and let the one word in
the orientation line be chosen from data `orientation_for()` already computes: banks
discovered → "grove", none → "node". The hook then stops calling a bare node a grove,
and the word gets one owner.

### 3. `CLAUDE.md`'s Navigation row becomes two-case

Rewrite it to cover both: launched from inside a node → that node's orientation is
injected and no garden listing is given; launched otherwise → the garden's nodes are
listed. It should *point at* the orientation contract, not restate what the hook emits —
the restatement is exactly what went stale and caused (2).

---

## Why this is text and not a `PreToolUse` gate

The standing rule in this project is *enforce invariants with hooks, not prose*, and it
still holds — this passes it rather than dodging it. The invariant is not absolute:
enumerating the garden is sometimes exactly the right action, so it fails the
mechanical-trigger half of the rules-vs-hooks test, and a gate on garden reads would
block legitimate work. What *is* mechanical here is the delivery: a `SessionStart` hook
emits this deterministically in every session, which is categorically different from a
`.claude/rules` one-liner competing for attention. `structural-lessons.md`'s "design
interfaces for their reader — LLMs follow text" is the governing lesson.

---

## Rejected and deferred

**Rejected: have the hook also inject the garden listing**, so the model never needs to
look. That is more always-loaded context in answer to a request for *less*, and it
inverts token economics for a question most sessions never ask.

**Deferred (§6): the `DIOTIMA_SUBJECT` rename.** `DIOTIMA_GARDEN` is overloaded — the
garden root in the config-default path, the resolved subject in the launch path — and
`dafne-plan-details/phase-3.md` records that reuse as *deliberate*, justified on process
hygiene (it never reaches the caller's shell). That justification is sound and
orthogonal to readability. Since the name demonstrably did not cause this incident,
reopening a recorded ruling to fix it would be designing from zero instances.
**Un-defer trigger:** the first consumer that genuinely needs the garden root *and* the
session subject in the same process — grove creation defaulting to `$DIOTIMA_GARDEN/<name>`
(Phase 4) is the nearest candidate.

**Optional, not proposed as part of this:** `orient.py --list`, so "what nodes exist" is
one cheap named action rather than an ad-hoc `find`. Only worth building if the scope
line proves to shift the question from *exploring* to *asking*.

---

## Exit criteria

1. A session launched from inside a bank-less node, asked "what do you know about?",
   answers from the injected manifest and runs **no** garden-wide `ls`/`find`.
2. That session's orientation calls `behavior-rewiring` a *node*, never a *grove*, and
   does not contradict the manifest text printed two lines below it.
3. A garden-subject session still gets its node list, now explicitly framed as the
   session's scope.
4. `CLAUDE.md`'s Navigation row describes what the hook actually does in both branches.
5. `orient.py --grove X` output is unchanged — no scope claim leaks into the CLI.

Verification technique is the one Phase 3 already used for this hook: a print-mode
`bin/diotima` run from inside a scratch node, asking the session to report what it was
told, with no other source for the answer.

---

## Carried forward

The harness memory `bare-nodes-not-at-garden-root` ("bare nodes live solely as
`parents/` submodules") is **wrong as written** — `english` and `instruments` are
top-level and bank-less. It needs correcting when change 2 lands, not before, so the
correction and the settled vocabulary land together.
