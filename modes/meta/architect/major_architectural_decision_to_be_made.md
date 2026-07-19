# Grove Inheritance & Distribution — Decision Record

*Status: open. Raw dictation preserved at `modes/meta/memory/big-bank/grove-inheritance-raw-dictation.md`.*

The question: how are groves inherited, composed, and distributed?

**Method this record enforces:**
1. Questions the repo has already answered are fixed points, not discussion topics.
2. Every open question carries a *discriminating test* — a concrete scenario whose
   outcome differs by option. No test that differs ⇒ not a real question ⇒ pick either.
3. Deliberation is spent in proportion to **irreversibility**, not to interestingness.
4. Zero-instance problems are not designed. The deliverable for those is a proof that
   the option stays open. Abstraction needs two real instances.

---

## Governing principle: implementations are disposable; components and contracts are the design

*User ruling, 2026-07-16. This outranks every "already answered" entry below.*

The project to date has been a search for **which primitives and components the system
needs** — a period of learning hooks and context-engineering primitives by building. The
components that surfaced (context-compiler, mem-bank, anki-mcp) are **findings about what
must exist**, not implementations to be preserved. They are not perfect; they are what was
discovered to be necessary.

**A good forward-compatible architecture outranks preserving the mechanics of any existing
component.** Rewriting `resolve_include_path`, reshaping the compiler, re-cutting any
subsystem — all acceptable, and none of it is a cost to weigh against the architecture.

**Read every "already answered" section below accordingly.** They are evidence about
*which components exist and what contracts they need to honour* — never arguments that
current code should survive. Where a section reads as "this is solved, don't touch it," it
means "this contract is understood," not "this implementation is fixed."

**What is known about the components** (from the same ruling):

| Component | Present in | Status |
|---|---|---|
| **mem-bank** | **every grove** — it records the author's history and process automatically | runtime baseline; the universal primitive |
| **context-compiler** | groves with layered text to resolve; implied wherever anki-mcp is | inheritance engine — needed wherever a grove has parents |
| **anki-mcp** | *some* groves (languages, card-bearing) — **explicitly not all** | optional capability; must be declarable and refusable |

This table is the substance of D2, given directly rather than derived. A grove with no
Anki must be a first-class citizen, not a degraded one.

---

## Premise (fixed — not re-litigated)

- A grove is a repository. Groves distribute separately from the orchestrator.
- Inheritance between groves is the core mechanic.
- Groves trend toward pure human-readable text; code is squeezed into the orchestrator.
  Rationale: the orchestrator layer thins as models improve; text outlives its interpreter.

---

## Already answered — by the repo, with evidence

### Text inheritance is built and daily-driven — *within a single repo*

```
rioplatense-anki.md ──> languages/language-defaults.md ──> deck-defaults.md
                    └─> ./focus_area.md                └─> cloze-deletion.md
english.md          ──> languages/language-defaults.md
instruments.md      ──> deck-defaults.md
```

`plugins/context-compiler/` resolves this: `#include` splicing, general→specific order,
**each file included at most once (keyed by canonical resolved path)**, cycles are errors.
Dedup-by-identity is the same answer Python's MRO and C++ virtual inheritance converge
on, it is implemented, and it is unit-tested (`tests/test_preprocess.py`).

**Verdict:** the merge *contract* is understood — splice general→specific, dedup, error on
cycles. **Cross-repo resolution is also now settled: relative-only addressing, verified
2026-07-17 — see D3.**

**The limit that forced it:** `README.md:23` — a path not starting with `.` resolves
*relative to the project root*. So `#include groves/languages/language-defaults.md` works
only while `languages` and `spanish` sit in one tree; in a standalone `spanish` repo it
resolves to nothing. **Root-relative addressing carries the same defect as D1: a
grove-external path hardcoded at authoring time.**

`.`-relative addressing has no such defect, and D3 verifies it end-to-end against the real
compiler. The resolution rule is therefore *not* a deliverable D1 must produce — it is
independent of the manifest entirely, which is a welcome decoupling: **includes resolve by
position; the manifest declares identity and configuration. Neither needs the other.**

**Honest instance count** (this record's own rule, applied to itself):

| Capability | Implemented | Production instances |
|---|---|---|
| Multiple includes per file | yes | `rioplatense-anki.md` — but that's one base + one *local* file, not two independent bases |
| Diamond resolution (dedup) | yes, unit-tested | **0** — no file reaches `deck-defaults.md` by two paths |

The mechanism exists and is tested, so a future diamond will not find you blind. But it
has never fired in anger. Do not treat it as validated by use.

### Implicit inheritance was tried and rejected

Cascade `context.md` sourcing — walk up the directory tree, read every ancestor
root-first — was the original mechanism (`.claude/rules/context-inheritance.md`,
documented in `big-bank/cascade-context-sourcing.md`). It was **deleted in `a4cd371`**
(2026-04-19, "isolate generation context via fork agent") in favour of explicit
`#include` plus subprocess isolation.

**Verdict:** explicit declaration beat ambient discovery once already, in this codebase.

**Scope it honestly:** what was rejected was ambient inheritance *between context files*
— implicit directory-walking that made the resolved context unpredictable. It is direct
precedent for **D3's include syntax** (name parents explicitly; do not infer them from
tree position). It is *not* a general verdict against in-grove path conventions — see
D1's Test 2 and the `youtube-extract` evidence in D2, where a convention works fine.
Cited too broadly, this precedent would settle D1 by rhetoric instead of by test.

### State lives in the grove; machinery lives in the runtime

Two independent instances, neither planned as a principle — both simply true:

| Member | State (in grove) | Machinery (in runtime) |
|---|---|---|
| mem-bank | `groves/languages/spanish/reading-log/` | `.claude/mem-bank/` |
| Anki | `groves/languages/spanish/backups/` | `plugins/anki-mcp/` |

**Verdict:** this *is* the grove/runtime boundary. "Do we even need a runtime?" — it
already exists; it is precisely what remains when `groves/` is removed. The only live
question is how thin it gets, and that is D2.

### Fork is dead as the inheritance mechanism

**A fork cannot express multiple parents.** Multiple inheritance is a hard requirement
(it is the premise of the whole record). A fork has exactly one upstream. That alone
settles it — no other argument is needed.

*Not* resting the verdict on "forks can't forward-propagate": they can. `git merge
upstream/main` pulls upstream changes into a fork, conflicts and all — and a submodule
whose child overrides parent content carries the same semantic-conflict exposure. The
propagation difference between fork and reference is one of degree; the multi-parent
difference is categorical. Use the categorical one.

**Verdict:** composition-by-reference, not fork. Multi-parent decides it.

### The three member kinds — the distinction the rest depends on

A grove is not one thing that inherits. It has three member kinds with **different**
inheritance semantics:

| Kind | Examples | Composition | Status |
|---|---|---|---|
| **Text** | specs, rules, focus areas | splice; dedup resolves diamonds | merge semantics **solved in-repo**; cross-repo resolution open (D3) |
| **State** | mem-bank contents, decks, backups, feedback logs | cannot splice — merging is semantic, not textual | **the only place diamonds bite**; 0 instances |
| **Machinery** | mem-bank scripts, anki-mcp, context-compiler | does not inherit; runtime provides | boundary is **D2** |

---

## Open decisions — dependency-ordered

### D0. The connection protocol — where does the user launch, and how do grove and runtime find each other?

**Recommendation: the grove is the project root; the runtime is ambient. The grove never
finds the runtime — the runtime is already loaded, and the grove is simply the directory
that was opened.**

This dissolves the question rather than answering it. `DIOTIMA_GARDEN=/a/b/c`, a registry
of grove paths, a discovery daemon — all of them exist to solve "how does X find Y by
path." Nothing needs to find anything by path if the runtime is installed once and the
grove is just `cwd`. Discovery flows **runtime → grove**, never the reverse, which is
exactly the direction `product-vision.md` mandates: *"the runtime reads from groves;
groves never need to know about the runtime's internals."*

Mechanically, `include_graph.py:49` already does `project_root = Path.cwd()`. Open a
grove, and the grove *is* the project root. The primitive is already there.

**Why not the orchestrator as a submodule inside the grove** (asked directly):

1. **It destroys the backdoor you asked for.** A vendored runtime is a *pinned* runtime.
   Every improvement would then require touching every grove — the precise opposite of
   "propagate future changes to existing groves." An ambient runtime propagates to all
   groves for free. **This is the argument; the rest are footnotes.**
2. It inverts the dependency — the grove would know about the runtime, violating the
   sovereignty invariant.
3. N groves = N copies on disk.
4. Songs don't embed the player.

**Why not orchestrator-rooted** (open Diotima, browse to a grove): the runtime would need
to be told where each grove lives — which is `subscriptions.json` again, i.e. option (a),
already killed by D1's Test 1. It also inverts "user mode is the product": you'd open a
tool and hunt for content, rather than opening content.

**Why MCP is not the answer** (asked directly): MCP is a transport for *tools*. The
orchestrator is mostly not tools — it is skills, hooks, context compilation, mem-bank
machinery. Hooks in particular cannot be expressed as MCP. MCP carries specific
integrations (anki-mcp already does, correctly) but cannot be the grove↔runtime binding.

**Launch, layered:** grove-rooted is the primitive. An optional "garden" launcher that
lists known groves and drops you into one is pure sugar on top — it scans a directory or
a user-level list, and crucially it never requires a grove to *register itself*. That
answers the either/or without reintroducing the runtime→grove-internals coupling.
*The sugar layer is now settled — see `interaction_north_star.md` (2026-07-18): git-model
primitive now, garden default-dir as sugar, managed-library verbs deferred to D5.*

**How the manifest gets loaded — VERIFY, do not treat as settled.** The runtime injects
the grove's manifest at session start via the harness's context mechanism. `.claude/`
hooks are the Claude-specific port of this; opencode gets its own. **The exact hook event
is unverified** — `settings.json` today uses `UserPromptSubmit`, `InstructionsLoaded`,
`PreToolUse`, `PostToolUse`, `SessionEnd`; whether a session-start injection point exists
and whether a *plugin* can ship it needs checking before anything depends on it. The
architecture does not rest on the answer — this is a port detail, and it belongs behind
the `.claude/`-is-vendor-specific line.

**The payoff:** the grove contains **zero** vendor-specific files. No `.claude/`, no
`CLAUDE.md`, no env var. Pure text, memory, and parents.

### Proposed grove layout

```
New_Grove/
  GROVE.md          # identity, manifest, semantic navigation
  memory/           # mem-bank node (standard structure)
  parents/          # base groves as submodules — NOT at top level
    languages/
    <base_b>/
  <content>.md
```

**One correction to the sketch:** parents go under a dedicated `parents/` (or `.groves/`)
directory, not at the grove's top level as `base_grove_a/`. At top level, the parent
namespace collides with the content namespace — a parent named `memory` or `files` is
ambiguous — and resolution stops being mechanical. Under `parents/`, the runtime
enumerates parents without parsing `.gitmodules`, and includes become
`parents/languages/language-defaults.md`.

**What GROVE.md must carry for forward compatibility:** *(superseded 2026-07-18 — the
manifest is now `DAFNE.md`, and `parents` was dropped from it entirely; see the DAFNE
amendments section below. Kept for the reasoning trail.)*

| Field | Why |
|---|---|
| `grove_format` | Version, so a runtime can migrate or warn instead of misreading |
| `parents` | Declared by **repo URL** → source + pin/range (see D4). URL-as-identity is the decentralized-by-hosting model (Go modules): no central registry, forks get new URLs naturally, ownership = hosting control. |
| `requires` | Capabilities (mem-bank, anki, …) — lets a runtime refuse or satisfy, instead of failing obscurely |
| bank config | The `patterns` / `graduate` data that D1's Test 2 shows a convention cannot express |

**No assigned `id` field** (an earlier draft proposed one — dropped 2026-07-17 on the
user's challenge: *who assigns IDs when anyone can fork any grove?*). Nobody does. The one
job an `id` had — collapsing a shared grandparent vendored at two paths — is solved by
**content-addressing** (hash the file; git already does), which needs no authority and
treats a modified fork as legitimately distinct. Identity is either *content* (for file
dedup) or *URL* (for naming a parent). Neither is assigned. This is the zero-instance rule
catching a field invented for a deferred problem.

**Protocol rules that buy forward compatibility** — these are the actual "backdoor":

- **Unknown fields are ignored, never fatal.** A grove authored in 2028 opened by a 2026
  runtime must degrade, not crash. Be liberal in what you accept.
- **`grove_format` is the migration handle** — a new runtime can read an old grove.
- **The runtime never writes into `parents/`.**
- **New runtime capabilities propagate for free** (ambient install). "One day groves can
  host skills" is then a runtime change plus an opt-in `requires:` line — no existing
  grove is touched. *That* is the backdoor, and it is bought by D0, not by any field.

### D1. Does a grove declare itself, or does the runtime configure it?

**Root of the declaration *format*. D0 and D1 are one decision seen from two sides —
D0 is the topology (who is `cwd`, who is ambient), D1 is the format (what the grove
declares). D0's recommendation already presupposes D1 resolving to "manifest"; if D1
instead resolved to "registry," D0 would collapse back into orchestrator-rooted. They
stand or fall together — read D0 for the shape, D1 for the evidence that the shape is
earned.**

Concrete evidence of breakage today — `.claude/mem-bank/subscriptions.json`, which is
*runtime* config, contains:

```json
{ "name": "spanish-reading", "bank": "groves/languages/spanish/reading-log", ... }
```

The runtime hardcodes a path into the grove's interior. The moment a grove is a separate
repository, this breaks: the runtime cannot know the internal layout of a grove it has
never seen.

**Options**
- **(a) Runtime registry** — status quo; runtime config enumerates each grove's internals.
- **(b) Grove manifest** — the grove declares its banks, capabilities, and parents; the
  runtime discovers the declaration.
- **(c) Convention-only** — fixed magic paths inside the grove, nothing declared.
  Not hypothetical: `youtube-extract` already works this way (see D2).

**Test 1 — location.** Publish the Spanish grove standalone; a stranger clones it into
their orchestrator. Does the runtime find its mem-bank without anyone editing runtime
config?
- **(a) fails** — a runtime edit per adopted grove; publishing a grove would touch the
  orchestrator, violating a stated vision invariant.
- **(b) and (c) both pass.** This test kills (a) and no more. It does *not* discriminate
  the manifest from a convention — a fixed in-grove path is found just as well.

**Test 2 — configuration, the one that actually discriminates (b) from (c).** A
convention supplies a *location*. It cannot supply *data about* that location. Today's
`subscriptions.json` entry carries `name`, `patterns`, and `graduate: false` — the
Spanish reading-log is deliberately excluded from graduation. Now ask: can a grove
declare **two** banks with different filters and different graduation policy?
- **(c) fails** — a magic path yields one bank and no way to express patterns or
  `graduate: false`. To keep (c), that data must move back to runtime config, which is
  (a) again, which Test 1 killed.
- **(b) passes.**

So the case for the manifest rests on **per-member configuration**, not on location.
Note what this implies: if a member kind needs no configuration, a convention is
genuinely sufficient for it, and the manifest should not swallow it out of tidiness.
The manifest earns its keep exactly where there is data to declare.

*(The `a4cd371` precedent is narrower than it first looks — it rejected ambient
inheritance* between context files*, not in-grove path conventions. It informs D3's
include syntax more than it does this decision. Do not over-apply it.)*

**Reversibility: LOW.** Once third parties author manifests, the format is frozen.
**This deserves nearly all the deliberation.**

### D2. What does the runtime guarantee a grove may assume? — **largely answered**

Answered by the component ruling at the top of this record, so what remains is the shape,
not the substance:

| Layer | Component | Rule |
|---|---|---|
| **Baseline — always present** | mem-bank | Every grove has one. It records the author's history and process automatically. A grove without memory is not a grove. |
| **Baseline — always present** | include resolution | The inheritance engine. Any grove with parents needs it; a root grove simply never invokes it. Costs nothing to guarantee. |
| **Optional — declared** | anki-mcp | *Not* universal. Card-bearing groves want it; others must not pay for it. |
| **Optional — declared** | future (youtube-extract, skills, …) | Same treatment. This is the slot that keeps the contract extensible. |

**The load-bearing consequence:** `requires:` must be something a runtime can **refuse or
satisfy**, not merely read. A grove declaring `anki` opened by a runtime without it should
say so plainly, not fail obscurely deep in a pipeline. And a grove declaring nothing
beyond baseline must be **first-class, not degraded** — mem-bank plus text is a complete,
legitimate grove (the "personal blog" / Marcus Aurelius case from the dictation).

**Still open:** whether `#include` resolution counts as a runtime *guarantee* or is simply
inert when unused (it is a pure function over files — arguably not a capability at all),
and the exact vocabulary of `requires:`. Both are low-stakes next to D1's format.

**Note the zero-instance honesty here:** a non-Anki grove still has **0** instances. The
ruling above is a design intent, not an observation — the only entry in this record
resting on stated intent rather than evidence. It is accepted because it comes from the
person who will author the second grove.

**Live evidence for option (c), worth studying before D1 is settled:**
`.claude/skills/youtube-extract/extract.py:41` reads `context_file.parent /
"focus_area.md"`. That is grove-*relative*, so — unlike `subscriptions.json` — **it
survives repo separation intact**. It is a working convention-only contract: zero
declaration, zero runtime config, and it would keep working in a standalone grove.

Its actual cost is not breakage but **silence**: the requirement exists only in a
docstring (`extract.py:8`) and an error message. Nothing tells a grove author the file
is expected until the tool fails. That is the honest (c) trade — cheap and portable,
but undiscoverable and unversioned. D1 should beat it on discoverability, not on
portability, or (c) wins on simplicity.

**Asymmetry that decides the default:** adding a guarantee later is cheap; removing one
breaks every published grove. **Start minimal.**

**Reversibility: MEDIUM** (additive is easy, subtractive is not).

### D3. How is a parent delivered into a child, and how does `#include` resolve across repos?

Given fork is dead: submodule vs. registry dependency vs. vendored copy.

#### Root-relative includes do not compose across repos — traced in the source

This is the sharpest concrete finding in the record, and it is not a design opinion:

```python
# include_graph.py:11-14
def resolve_include_path(path_str, from_file, project_root):
    if path_str.startswith("."):
        return (from_file.parent / path_str).resolve()
    return (project_root / path_str).resolve()   # ← any non-dotted path

# include_graph.py:49
project_root = Path.cwd()
```

A parent grove authored standalone contains `#include groves/languages/deck-defaults.md`,
which resolves against **its own** root. Vendor that grove into a child at
`parents/languages/`, and `project_root` is now the **child's** cwd — the include
resolves to a path that does not exist, or worse, silently to the wrong file.

**Every current grove uses root-relative includes.** They work only because everything
shares one tree.

#### The fix: relative-only addressing. **Verified empirically, 2026-07-17.**

**Ban non-dotted include paths. That is the whole change.** No grove-root detection, no
manifest-mediated resolution, no `project_root` at all.

A `.`-relative include resolves against *the including file's own directory*
(`include_graph.py:12-13`), which is position-independent by construction. A grove's
internal includes therefore resolve identically whether the grove is standalone or
vendored ten levels deep inside a child.

**This was tested against the real compiler, not reasoned about.** A nested vendored
structure was built and compiled twice:

```
spanish/rioplatense.md            #include ./parents/languages/language-defaults.md
                                  #include ./focus_area.md
spanish/parents/languages/
    language-defaults.md          #include ./cloze-deletion.md
                                  #include ./parents/deck-base/deck-defaults.md
    cloze-deletion.md
    parents/deck-base/deck-defaults.md
```

- Compiled from `spanish/` → `CLOZE, DECK-DEFAULTS, LANGUAGE-DEFAULTS, FOCUS-AREA,
  RIOPLATENSE` — correct content, correct general→specific order.
- The **same parent files** compiled standalone from `parents/languages/` → `CLOZE,
  DECK-DEFAULTS, LANGUAGE-DEFAULTS`. Identical resolution, zero edits.

**The finding that collapses this decision: the current compiler already does this
correctly, unmodified.** Every include started with `.`, so the `project_root` branch
never executed. Relative-only is not a change to build — it is a **discipline to adopt**.

**Revised cost** (an earlier draft of this record overstated it as "a compiler change plus
a migration"):
- **Compiler:** no change required for correctness. Optionally delete the `project_root`
  branch and parameter — a *simplification*, removing a concept rather than adding one.
- **Migration: repo surgery, not a path rewrite.** The test above *built* the target
  topology; it did not exercise the transform from today's. **The current nesting is
  upside-down relative to the target.** Shared bases currently sit *above* their
  consumers — `spanish/` reaches `languages/language-defaults.md` by going up, which
  reaches `deck-defaults.md` up another level. The target vendors parents *downward*
  (`./parents/languages/...`). Converting naively produces precisely the `../`-escape
  anti-pattern this section bans. The real sequence is: **promote the loose shared files
  to groves → vendor them downward as submodules → then rewrite includes.** Only the third
  step is mechanical.
- **Enforcement:** a lint/hook rejecting (a) non-dotted paths and (b) `../` escaping the
  grove root — the one genuine hazard, since an escaping path resolves *differently*
  standalone vs. vendored and would fail silently. Per this project's own doctrine,
  invariants become hooks, not prose.

**The compiler's contract, stated component-first:** *given one entry file, resolve its
includes using only paths relative to each including file, and never consult anything
above the entry file's own tree.* That contract is what must survive. The current
implementation happens to satisfy it; any rewrite must too.

**Reversibility: LOW for the addressing discipline** — includes are authored inside
published groves and freeze the moment a stranger writes one. But the discipline is now
**verified rather than speculative**, which is what low-reversibility decisions deserve
before they freeze.

### D4. Submodule pin vs. resolved version range — reproducibility or auto-propagation?

***Resolved 2026-07-19 — pins + assisted update. See the ruling section at the end of
this record. Original analysis kept for the reasoning trail.***

**The unexamined fork in the proposed layout, and the real crux of the forward-compat
question.** It deserves a conscious decision because the sketch implicitly assumes one
answer while the stated goal wishes for the other.

The "backdoor to propagate future changes" is **already satisfied for runtime/machinery**
by D0's ambient install — free, no mechanism needed. It is **not satisfied for base-grove
content.** A git submodule pins an exact SHA. An improvement to `languages` reaches a
derived grove only via a manual `git submodule update --remote`, in every derived grove,
forever.

| | Submodule pin | Resolved version range (`languages: ^2`) |
|---|---|---|
| Base-content improvements | manual, per grove | flow automatically |
| Reproducibility | exact, forever | compile output can change under you |
| Resolution machinery | none (git does it) | runtime must resolve + fetch |
| Diamond with conflicting versions | two copies, both pinned | must pick — MVS, nesting, or error |

**You cannot have both.** Pinning *is* the absence of propagation; propagation *is* the
absence of pinning. The sketch says submodules (pin); the goal says propagate.

**This is your call, not a derivable one** — it is a values question about whether a
grove's compiled output must be stable over time. Note the asymmetry, though: a range can
be pinned (`=2.1.0`), but a pin cannot be un-pinned without changing the format. **The
range is the more forward-compatible primitive**; submodules can still be the *delivery*
mechanism underneath a declared range.

**Reversibility: LOW** — it is encoded in every published grove's `parents:` declaration.

### D5. Distribution / marketplace

Depends entirely on D1. Zero groves have ever been published. **Defer** until D1 ships
and one grove is actually distributed.

---

## Constraints the format must protect

Not today's work — but the format must not foreclose these.

**Opening a stranger's grove must not execute their code.** While a grove is pure text +
memory + submodules, cloning and opening one is safe: the runtime is yours, the content
is theirs. The moment groves can host skills or hooks — explicitly wanted "one day" — the
threat model inverts: *opening shared content executes a stranger's code*, with your
credentials, in your session. That is the npm/VSCode-extension problem, and it arrives the
day the marketplace does.

This is a **reason the text/state/machinery split is load-bearing rather than tidy**: the
first two are inert, the third is not. If groves ever carry machinery, distribution needs
a trust boundary (declared capabilities, review, signing, sandboxing — undecided). Note it
now so D1's `requires:` field is designed as something a runtime can *refuse*, not merely
read.

---

## Decided — mem-bank diamond (user ruling, 2026-07-16)

**Resolution: explicit opt-in, not automatic merge.** A derived bank declares
`recurse-mem-enable` (**default `false`**, for token economy) to say whether base groves'
banks are subscribed to the hook at all. Per-bank filtering already exists via
`this-bank-prompt.md` — each bank states what to capture and what to exclude (the Spanish
reading-log's prompt excludes card creation, vocabulary, and deck maintenance, keeping
only reading selections and verdicts).

**Does inherited memory travel when a grove is forked? — resolved, it's a git decision
(user ruling, 2026-07-17).** Not a format concern at all. The author *commits* the bank
(the grove ships as a *record* — the blog / Marcus-Aurelius case, where the filtered
history is the shared artifact) or *gitignores* it (the grove ships as a *method* to
re-aim — fork-and-refocus, empty bank). Both products fall out of ordinary git with no
mechanism to design. This is a clean instance of the governing principle: the primitive
(git) already carries it; the runtime adds nothing.

**Why this holds up architecturally, not just pragmatically:**
- **Default `false` means the diamond does not form.** There is no merge to resolve
  because there is no automatic recursion. The hard case is opt-in, and opting in is a
  deliberate act by someone who wants it.
- It is **explicit declaration over ambient behaviour** — consistent with the `a4cd371`
  precedent and with D1's direction.
- Two bases filtering the same sessions through different `this-bank-prompt.md` lenses is
  a **feature, not a collision**: the banks are answering different questions. That is
  precisely why state resists textual merging — and why not merging is right.

The toggle belongs in the bank's own config, which makes it manifest data — another entry
in D1's Test 2 column (data a path convention cannot express).

---

## Deferred — zero instances today; keep the option open, do not build

| Thing | Instances | Obligation |
|---|---|---|
| Diamond on **text** via vendored parents | 0 | see note below — content-addressing preserves the option for free |
| Conflicting parent *versions* (base_a wants `languages@1`, base_b wants `languages@2`) | 0 | D4's choice determines whether this can even arise |
| Marketplace / registry | 0 | — |
| Jupyter / deterministic grove interaction | 0 | — |

**Note on text diamonds under vendoring** — a consequence of D0+D3 worth recording so it
isn't rediscovered painfully: `collect_inputs` dedups via `seen.add(resolved)`, keyed on
the **canonical filesystem path**. Once parents are vendored, a shared grandparent exists
at `parents/base_a/parents/common/` *and* `parents/base_b/parents/common/` — two distinct
real paths. Path-dedup will not collapse them, and the content splices twice.

The eventual fix is **content-addressed dedup** — key `seen` on a hash of file content
rather than filesystem path, so two identical vendored copies collapse regardless of
location. This needs **no manifest field and no assigned identity** (git already
content-addresses; a modified fork hashes differently and is correctly kept distinct).
Zero instances today, so **do not build it** — but note the door is already open for free.
The option costs nothing to preserve because content is intrinsic; nothing to carry, no
field to freeze.

Building any deferred item now is designing from zero examples. Revisit when a second real
instance appears — and note it here when it does.

---

## Next step — the cheapest thing that de-risks what remains

**Executed 2026-07-18 — see `dafne_simulation/` and the DAFNE amendments below.** The
boundary answer: `deck` (deck-defaults + cloze-deletion) and `language` are bare DAFNE
nodes, not groves; `spanish` is a grove. Compiled output byte-identical to production;
parents compile standalone unmodified. Original text kept for the reasoning trail.

D3's addressing rule is now verified, so the open risk has moved. **The remaining
armchair-proof question is where the grove boundaries fall.**

Today `deck-defaults.md` (at `groves/`) and `cloze-deletion.md` (at `groves/languages/`)
are **loose shared files, not groves** — yet `language-defaults.md` includes both. So:
*which of today's includes are cross-grove relationships (become `parents/` submodule
entries) and which are within-grove file includes (stay plain `./`-relative)?* Relative
addressing works for both, which is exactly why the syntax no longer forces the answer —
**the boundary question is now independent, and it is the one that matters.**

Work that out for the Spanish chain specifically:

```
rioplatense-anki.md ──> language-defaults.md ──> deck-defaults.md
                    └─> ./focus_area.md      └─> cloze-deletion.md
```

- Is `languages` a grove, with `deck-defaults` a grove above it? Or is `deck-defaults` a
  loose file the runtime provides?
- Does `spanish` become a grove with `parents/languages/`, and do `english` + `instruments`
  then share it?
- What does each `#include` line look like afterward?

This either **validates** the nearest-GROVE.md rule plus the `parents/` layout, or exposes
a gap — for the cost of an afternoon and zero code. It is the record's own doctrine
applied to itself: abstraction needs the real case to discipline it, and this is the only
real case in existence. **Do this before D3's syntax freezes, because after publication it
cannot be taken back.**

---

## Decided — DAFNE and the node/grove split (user rulings, 2026-07-18; enacted in `dafne_simulation/`)

The boundary exercise prescribed above ran in a symlink sandbox: each top-level dir in
`dafne_simulation/` simulates a standalone repository, `parents/<name>` symlinks simulate
submodules. Verified: compiled output byte-identical to the production `groves/` chain;
parent nodes compile standalone with zero edits. Findings graduated into rulings:

### DAFNE — the engine has a name and a home

**DAFNE** (*Directory As a Fractal Node Engine*): the deterministic interpreter of the
node tree. Its own repository, mounted under `plugins/` like context-compiler and
anki-mcp — runtime, ambient (D0), independently versioned. **It absorbs context-compiler
rather than sitting beside it**: `include_graph.py` is the proto-DAFNE, and two
graph-walkers in `plugins/` would be the exact duplication smell the constitution warns
about. Efficiency contract: the engine reads *manifests and structure*, never content —
the LLM reads content, the engine walks trees.

### Node vs grove — the memoryless-node question, answered by first instance

A **DAFNE node** is protocol conformance: manifest, text, optional `parents/`, optional
`.private/`. A **grove** is a node carrying memory. `deck` and `language` are bare nodes;
`spanish` is a grove. Grove-ness is inferred **structurally** (bank declaration /
`memory/`) — there is no `type:` field, consistent with identity-by-content everywhere
else in this record. D2's "a grove without memory is not a grove" survives by becoming
definitional rather than normative. Bases are libraries; groves are the lived-in things
people share as content.

### The manifest is `DAFNE.md`

Its **presence marks a directory as a node** — the identity-marker job is why `AGENTS.md`
lost (any repo may carry one for unrelated reasons, so presence can't discriminate).
Naming follows the Cargo.toml/Dockerfile precedent: manifests are named after the
ecosystem, not the package kind — which is precisely how `GROVE.md` broke (it misnames
every bare node). Field `grove_format` simplifies to `format`. `AGENTS.md` stays
available as an *optional* navigation companion — graceful degradation when a node is
opened by a foreign agent runtime with no DAFNE installed. The manifest now carries only
`format`, `requires`, and bank config: each round of deliberation has earned it *down*.

### `parents` is not manifest data

D1's own Test 2 criterion, applied against this record's own sketch: enumeration =
`readdir(parents/)` (position expresses it fully); URLs = `.gitmodules` (git's canonical
home — duplicating them into the manifest would be two sources of truth, guaranteed to
drift). Termination = **absence of `parents/`** — no `parents: []` field, and **no
sentinel root repository**. A "small DAFNE" terminal node was considered and rejected: a
pinned submodule is the *least* capable propagation vehicle in the design (the real
channels — ambient engine, `format` migration handle, D4 ranges — all already exist), a
repo is the most expensive sentinel imaginable purchased to avoid an `if not parents:`
check, and *"I don't know what to put there yet"* is the zero-instance rule verbatim —
the `id` field again. The empty `grove/` root-base dir built to test this stayed empty
and was deleted.

**D4 consequence, kept conscious:** convention-only parents is fully compatible with
submodule pins; a version *range* would resurrect a manifest field, since `.gitmodules`
can express only pins. Dropping the field must not decide D4 silently.

### `.private/` — name reserved now, mechanism built later

Visibility by position — a convention, exactly where Test 2 says conventions suffice
(location-only fact, no per-file data). The honest justification is not script-hiding
(scripts in nodes: zero instances) but **API-surface control for text**, which has a
near-instance already: `language` includes two `deck` files by bare path, so every parent
file is API — the fragile-base-class problem; a published node whose entire tree is
includable can never refactor again. Interpreter rule: *an include target must lie within
the including node's own tree (own `.private` accessible to self) or within a
transitively vendored parent tree **outside** any `.private/`; non-dotted paths and `../`
escapes rejected.* Reserved now because it freezes with D1 — retrofitting privacy onto a
published all-public format is impossible. **Visibility ≠ trust** — see next.

### Trust amendment for node-carried skills

When nodes one day carry skills, the connector contract is **harvest → declare →
consent**, never auto-load. *Public ≠ safe*: public skills are precisely the ones that
execute, with the user's credentials. The three-member-kinds rule softens accordingly:
*runtime machinery never inherits; node-carried skills inherit like text but execute only
across a trust boundary.*

### Polymorphism — door open, nothing built

Override-by-name-collision would be ambient behaviour — the shape `a4cd371` already
killed once. If polymorphism ever comes, it comes as explicit declaration. Zero
instances; nothing in the current design forecloses it.

### New open questions (also parked in `dafne_simulation/context.md`)

- ~~Does `requires:` union up the parent tree, or is it re-declared per node?~~
  **Resolved 2026-07-19: union — see the ruling section below.**
- The production `groves/` tree still needs the D3 repo surgery (promote → vendor
  downward → rewrite includes). The sandbox validated the target topology, not the
  transform. **Execution plan: `dafne_plan.md`.**

---

## Decided — D4 and `requires:` scope (user rulings, 2026-07-19)

**D4: pins + assisted update.** Version truth = the submodule SHA; git is the entire
format-side mechanism, and no version field returns to `DAFNE.md`. Propagation becomes
runtime UX: an assisted-update flow ("tend parents") fetches submodule upstreams, nudges
on new commits, shows the **compiled-output diff** (possible only because groves are
text), and commits the new pin — the commit is the audit trail, `git revert` the
rollback.

The deciding analysis: ranges fork into (B1) no-lockfile — true auto-propagation, but
compiled output changes under you, which breaks the grove-as-*record* product outright —
and (B2) with-lockfile, whose update UX (nudge → accept → recompile → verify → commit)
is *identical* to pins-plus-assist while additionally costing a resolver, a lockfile
format, a diamond-version policy, a resurrected manifest field duplicating
`.gitmodules`, and a semver-discipline obligation on authors who are teachers, not
library maintainers. No shipping ecosystem lives in B1; B2 buys nothing pins don't.
Pins also place each concern on its naturally-propagating side of the boundary: version
*truth* in the grove (frozen, reproducible), version *intelligence* in the ambient
runtime (improves for free per D0).

**The door stays open:** a future `versions:` range field is purely additive — the
unknown-fields rule means an old runtime opening a ranged grove degrades gracefully to
its submodule pins. Deferred until a real propagation instance exists to discipline the
design (zero-instance rule).

**`requires:` unions up the parent tree.** The engine computes effective requirements by
walking `parents/` manifests — structure and manifests only, per the efficiency
contract. Encapsulation holds: `language` never re-declares that `deck` needs anki, and
a parent adding a capability never forces descendant edits. A local *mask* (child
suppresses an inherited requirement) has zero instances and is deferred; union does not
foreclose it.

---

## Not an architecture question

**"Will this be replaced by a feature drop from Gemini / NotebookLM?"**

Strategy, not structure. It belongs in `modes/world-adoption/`, and mixing it in here
poisons the design reasoning.

For the record, the vision already implies the answer: a feature drop from a giant eats
*runtimes*, not *content*. You explicitly want the orchestrator to thin over time.
Keeping groves as near-pure text is not naïveté about that risk — it *is* the hedge.
Text outlives its interpreter.
