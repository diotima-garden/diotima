# Bank Discovery Wiring — DAFNE Phase 3, bullet 1

*Created 2026-08-29. Architect-owned design record for the first bullet of
`dafne_plan.md` Phase 3: decommissioning `subscriptions.json` as the registry for
grove-owned memory banks. Every decision below is closed; every code claim is
verified against the tree at `file:line`. Written so a builder agent can execute
without re-deriving anything.*

**Scope:** how grove-declared banks reach mneme. Does **not** cover Phase 3's other
three bullets (`requires:` refusal, `SessionStart` manifest injection, assisted
parent update).

---

## The decision in one line

**The orchestrator asks DAFNE for the banks it oversees, unions them with its own,
and hands the merged list to mneme in-process.** Neither engine learns the other's
vocabulary.

### The three roles

| Component | Knows | Must never know |
|---|---|---|
| **dafne** (`plugins/dafne`) | how to walk a recursive node tree; how to resolve a node's `./`-relative paths | what a bank is *for*; that mneme exists |
| **mneme** (`plugins/mneme`) | banks, patterns, graduation | groves, submodules, DAFNE, that a bank list came from a tree walk |
| **orchestrator** (`system/diotima/`) | that both exist; which banks are purely its own | — it is the only place the two names meet |

mneme is a standalone product (its own repo, `diotima-garden/mneme`). It gains a
**library entry point** — a normal thing for a standalone product to have — not any
grove awareness.

`system/README.md` already defines `system/` as "host-level subsystems shared across
hooks and skills." That is the orchestrator layer; the integration belongs there and
nowhere else (constitution: one home per contract).

### Who owns *where* the groves are

**The orchestrator owns *where* (passes a base path); dafne owns *how* (tree walk).**

`interaction_north_star.md` already settled *where* on the runtime side — the grove
list is "readdir of a default dir ∪ MRU file ∪ later a store," all dumb runtime-side
data. Giving dafne its own notion of grove roots would put configuration inside the
engine and contradict that ruling.

**Payoff:** this is Phase-4-ready for free. When the garden dir and recents file
arrive, the orchestrator passes different (or multiple) base paths and **dafne is
unchanged**.

---

## The manifest schema — already designed, already in production

No new format needed. Both grove manifests already carry the block, in identical
shape, written during Phase 2 as scaffolding for exactly this:

```yaml
# groves/spanish/DAFNE.md
---
format: 0
requires: []
banks:
  - name: spanish-reading
    bank: ./reading-log
    graduate: false
    patterns:
      - "reading-log/context\\.md"
---
```

```yaml
# groves/social-dynamics/DAFNE.md
---
format: 0
requires: []
banks:
  - name: social-dynamics
    bank: ./memory
    graduate: false
    patterns:
      - ".*"
---
```

Field names mirror `plugins/mneme/registry.py`'s dict shape 1:1 (`name`, `bank`,
`graduate`, `patterns`/`pattern`) — whoever wrote the scaffolds designed for this
merge. `bank:` is `./`-relative to the node's own root, consistent with D3's include
discipline.

**Dafne's read of this block is deliberately shallow: it understands `bank:` only.**
That key is a path it must resolve; every other key is **opaque payload copied
through verbatim**. This is the "engine reads manifests and structure, never
content" contract, and it means a future grove declaring bank keys for some other
consumer needs no dafne change.

`recurse-mem-enable` (the D6 opt-in-diamond field) is **absent from both scaffolds
and read by no code today**. Its absence already means `false`, which is the correct
default. Do not add it speculatively — the unknown-fields rule reserves it for free.

---

## Migration table — all four current banks

Source: `groves/mem-bank-subscriptions.json`.

| bank | destination | fields that must travel | status |
|---|---|---|---|
| `spanish-reading` | `groves/spanish/DAFNE.md` | `graduate: false`, `patterns` | **already present** — verify byte-match, then delete from JSON |
| `social-dynamics` | `groves/social-dynamics/DAFNE.md` | `graduate: false`, `patterns` | **already present** — verify byte-match, then delete from JSON |
| `meta` | **stays** in the orchestrator's own list | — | not a grove |
| `world-adoption` | **stays** in the orchestrator's own list | — | not a grove |

The two grove entries are already duplicated into their manifests. The real work is
wiring, not data movement.

### Why architect/world-adoption modes do NOT become groves

`product-vision.md` defines groves as content designed to be "published, inherited,
and re-aimed" — forked and pointed at someone else's domain. `modes/meta/` and
`modes/world-adoption/` are the system observing its own operational history:
runtime self-reflection, no parents, never cloned by a stranger and re-aimed.
Forcing them into the grove shape to unify discovery would bend the abstraction to
fit an implementation convenience.

**Therefore `subscriptions.json` narrows, it does not die.** `dafne_plan.md` Phase 3
says "retains only runtime-side preferences, **or dies**" — the evidence answers
which branch. It becomes the orchestrator's registry for banks that have no grove to
live in.

**It also moves.** `groves/mem-bank-subscriptions.json` is orchestrator config
sitting in the groves directory. Move it to `system/` alongside its only consumer.

---

## Verified findings (do not re-derive)

Each of these was checked against the tree on 2026-08-29.

### mneme

| Fact | Evidence | Consequence |
|---|---|---|
| Pattern matching is **unanchored** `.search()` | `session_crawler/crawler.py:138` — `if pat.search(s)` | Node-relative patterns in a manifest stay correct regardless of the mount point name. This is what makes grove-declared `patterns` portable. |
| File parsing **is** separated from logic — at the registry layer | `registry.py:6-12` `load_banks()` is the sole file read; `bank_effective_patterns`/`bank_small_bank_path`/`bank_archive_dir`/`bank_capture_prompt` all take a plain dict | Everything below the entry point already accepts in-memory banks. |
| File parsing is **not** separated at the entry point | `small-bank.py:186` hardcodes `load_banks(args.subscriptions, cwd)`; `big-bank.py:247` the same | **A small mneme change is required.** See the spec below. |
| Absolute `bank:` paths pass through untouched | `registry.py:23-27` — `if cwd and not p.is_absolute(): p = Path(cwd) / p`; same shape at `registry.py:30-34` | Dafne emitting absolute paths makes grove banks immune to whatever `cwd` the hook reports. **Load-bearing.** |
| `graduate` defaults to **True** | `big-bank.py:253` — `bank.get("graduate", True)` | Both grove banks set `graduate: false` explicitly; if that field fails to travel, graduation behavior silently changes for a real bank. |
| Double-graduation degrades gracefully | `big-bank.py:158` — `"not found, nothing to graduate"` | The duplicate hazard below is small-bank-specific, not big-bank. |
| `small-jobs.json` is read-modify-written with no locking | `small-bank.py:229-240` | Two concurrent `small-bank.py` invocations = lost-update race. **The new hook must replace the old one, not run alongside it.** |
| `run_hook` reads `sys.stdin` itself | `small-bank.py:158` | stdin can be read only once — see "why one parameter" below. |
| `HOOK_RECURSION_GUARD` is checked inside `run_hook` | `small-bank.py:164` | Calling `run_hook` (not something finer-grained) inherits the guard for free. Bypass it and the `claude -p` worker re-triggers the hook. |
| Importing `small-bank.py` has module-level side effects | `small-bank.py:15` `sys.path.insert(...)`, `:20` logger creation | Be deliberate about import order in the orchestrator. |
| Module filenames are hyphenated | `small-bank.py`, `big-bank.py` | Not importable via plain `import`. Use `importlib.util.spec_from_file_location`, or rename to underscores inside mneme. Either is acceptable. |

### dafne

| Fact | Evidence | Consequence |
|---|---|---|
| The manifest reader already exists | `manifest.py:19-34` `parse_manifest` (YAML frontmatter, `{}` when absent, unknown fields ignored) | Bank discovery reuses it as-is. |
| The recursive tree walk already exists, with a cycle guard | `manifest.py:37-43` `parent_dirs`, `:46-63` `effective_requires` | Bank discovery is the same recursion collecting a different key. |
| dafne has a **real** third-party dependency | `manifest.py:16` — `import yaml` | dafne's venv is not phantom. The hook must run under `plugins/dafne/.venv/bin/python3`. |
| dafne is whitelisted per-script with its venv interpreter | `.claude/settings.json:60-62` | A new script needs its own allow-rule in the same shape, if invoked via the Bash tool. |

### Harness wiring

| Fact | Evidence |
|---|---|
| Current session-end hook | `.claude/settings.json:147` — `python3 "$CLAUDE_PROJECT_DIR"/plugins/mneme/small-bank.py --subscriptions "$CLAUDE_PROJECT_DIR"/groves/mem-bank-subscriptions.json` |
| `big-bank.py` is invoked by Claude via the Bash tool, whitelisted by **prefix** | `.claude/settings.json:44` — `Bash(python3 plugins/mneme/big-bank.py:*)` |
| `$CLAUDE_PROJECT_DIR` is available in hook command strings | same line 147 | 

**Why `$CLAUDE_PROJECT_DIR` matters:** it gives the orchestrator its grove base path
**without reading stdin**, which is what collapses the mneme change to a single
parameter.

---

## Implementation spec

### 1. `plugins/dafne` — bank discovery

New script alongside the existing per-concern scripts (`preprocess.py`,
`include_graph.py`, `compiled-is-fresh.py`), plus functions in `manifest.py`:

```python
# manifest.py
def discover_banks(node_root: Path, seen: set[Path] | None = None) -> list[dict]:
    """Same recursion as effective_requires, collecting manifest['banks'].
    Resolves each entry's './'-relative `bank:` to an ABSOLUTE path against
    node_root. All other keys are copied through verbatim — opaque payload."""

def discover_grove_banks(base_dir: Path) -> list[dict]:
    """readdir(base_dir), keep children carrying DAFNE.md, discover_banks() each."""
```

```
plugins/dafne/discover_banks.py --base <dir>   →   {"banks": [...]} on stdout
```

The CLI form exists for standalone use and debuggability; the orchestrator may
import the functions directly instead. **Dafne never writes a file.** It answers a
query.

Test fixtures to add, matching the existing suite's style: a node with no `banks:`
key; a grove with one bank; a two-level parent chain where only the child declares
banks; verification that `bank:` comes back absolute; verification that an unknown
key inside a bank entry survives the round trip.

### 2. `plugins/mneme` — one optional parameter

```python
def run_hook(args, banks=None):
    ...
    if banks is None:
        banks = load_banks(args.subscriptions, cwd)
```

Same shape for `big-bank.py`'s main. **Standalone CLI behavior must be
byte-identical when `banks` is omitted** — that is the whole compatibility contract.
mneme still knows nothing about groves.

**Why not a second `hook_input=` parameter:** `run_hook` reads stdin at
`small-bank.py:158`, and stdin can be read only once. The tempting fix is to have
the orchestrator read stdin and pass the parsed dict through. It does not need to —
the orchestrator gets its base path from `$CLAUDE_PROJECT_DIR` and **never touches
stdin**, so `run_hook` keeps reading stdin exactly as it does today. One parameter,
not two.

This change belongs in the `diotima-garden/mneme` repo and needs its submodule
pointer bumped in master afterward.

### 3. `system/diotima/invoke-mneme-on-groves.py` — the orchestrator

Responsibilities, in order:

1. Read its own bank list (`system/mem-bank-subscriptions.json` — `meta`,
   `world-adoption`).
2. Ask dafne for grove banks under `$CLAUDE_PROJECT_DIR/groves`.
3. Union the two lists.
4. Call mneme's `run_hook(args, banks=merged)`, letting mneme read stdin itself.

**Defensiveness is an inherited obligation.** Today mneme's hook wraps every step in
try/except and returns 0, so nothing it does can disrupt session end
(`small-bank.py:187-189`, `:198-200` are the pattern). The orchestrator must do the
same — a dafne failure must not take the hook down with it. This is the one thing
given up by moving in-process, and it must be paid back explicitly.

### 4. `.claude/settings.json` — replace, do not add

The session-end hook entry at line 147 is **replaced** by:

```
plugins/dafne/.venv/bin/python3 "$CLAUDE_PROJECT_DIR"/system/diotima/invoke-mneme-on-groves.py
```

dafne's venv interpreter, because of the `yaml` dependency; mneme is stdlib-only and
imports fine alongside it.

**Not a second hook.** Two entries would mean two `small-bank.py` invocations racing
on `small-jobs.json` (`:229-240`) plus a redundant full transcript parse.

### 5. `system/mem-bank-subscriptions.json` — moved and trimmed

Moved from `groves/`, reduced to:

```json
{
  "banks": [
    { "name": "meta", "bank": "modes/meta/memory",
      "patterns": ["meta/.*/context\\.md", "mneme/README\\.md"] },
    { "name": "world-adoption", "bank": "modes/world-adoption/memory" }
  ]
}
```

### 6. Manifest cleanup

Delete the "This `banks:` config is a placeholder scaffold — the live subscription
source of truth remains `groves/mem-bank-subscriptions.json` …" paragraph from both
`groves/spanish/DAFNE.md` and `groves/social-dynamics/DAFNE.md`. Each is a separate
grove repo commit plus a submodule pointer bump in master.

---

## Ordering constraint — a real bug if ignored

`spanish-reading` and `social-dynamics` currently exist in **both** the JSON and
their grove manifests. If the union runs before the JSON is trimmed,
`small-bank.py:203` iterates both copies and queues two jobs for the same bank —
the same `small-bank.md` written twice.

**Trim the JSON in the same change as the union, or before it.** Never after.

Also note the repo ordering: mneme and the two grove repos are **separate
submodules**. Land the mneme `banks=` parameter and the grove manifest cleanups
first, bump pointers, then flip the hook in master — otherwise master's hook calls a
`run_hook` signature that isn't there yet.

---

## Duplicate-name behavior (accepted, not guarded)

Two `banks` entries sharing a `name` across sources are not deduped. Harmless for
`small-bank.py` (it queues twice, keyed by `session_id` + `target`), and
`big-bank.py` degrades gracefully at `:158`. Zero instances once the trim above is
done. Not worth guarding against.

---

## Exit criteria

- `system/mem-bank-subscriptions.json` contains no path into any grove's interior.
- Session end on a Spanish reading session queues a `spanish-reading` job, with the
  bank path resolved from `groves/spanish/DAFNE.md` and nothing else.
- `graduate: false` still suppresses graduation for both grove banks.
- `plugins/mneme` run standalone with `--subscriptions <file>` and no `banks=`
  behaves exactly as before the change.
- Deleting a grove's mount removes its banks with no runtime-side edit.

---

## Adjacent findings surfaced during this design (not in scope)

- **`packaging-strategy.md` Step 0 is stale.** It says to "retire the phantom
  context-compiler venv: repoint its invocations at system `python3`" on the grounds
  that it is stdlib-only. dafne absorbed context-compiler and now imports `yaml`
  (`manifest.py:16`), so its venv is real and that step would break it. Fix the
  strategy doc when that track is picked up.
- **`dafne_simulation/` still exists on disk** as an untracked, empty husk
  (`dafne_simulation/spanish/`), despite Phase 2's cleanup checkbox. `git ls-files`
  returns nothing for it. Safe to `rm -rf`.
