# `requires:` Refusal — DAFNE Phase 3, bullet 2

*Created 2026-08-29. Architect-owned design record for the second bullet of
`dafne_plan.md` Phase 3: making a grove's declared capabilities something the runtime
**refuses or satisfies**, not merely reads. Every decision below is closed; every code
claim is verified against the tree at `file:line`. Written so a builder agent can
execute without re-deriving anything.*

**Scope:** how a declared-but-unavailable capability produces a plain, early message.
Does **not** cover installing or activating a plugin (that is issue #17's remaining
half), `SessionStart` manifest injection (bullet 3), or assisted parent update
(bullet 4).

---

## The decision in one line

**dafne answers *what does this node need, and who said so*; the orchestrator answers
*is it here*; the pipeline asks before it spends anything.** No component learns
another's vocabulary.

### The three roles

| Component | Knows | Must never know |
|---|---|---|
| **dafne** (`plugins/dafne`) | how to union `requires:` up the parent tree; which node declared each name | what `anki` *means*; that anki-mcp exists; how anything is installed |
| **orchestrator** (`system/diotima/`) | the capability→probe map: the token `anki` ⇒ is the machinery materialized on this machine | groves, parent trees, manifests |
| **call site** (the two pipelines today) | ask, read a semantic token, stop or proceed | either of the above |

This is the same split `bank_discovery_wiring.md` established for bullet 1, and
`system/diotima/bank_union.py` is its existing instance. `capabilities.py` is its
sibling: the one place where the DAFNE vocabulary (`anki` the token) meets the
runtime's reality (`plugins/anki-mcp` the machinery).

---

## The load-bearing ruling: freeze the consumer side, keep the supplier side soft

This bullet's real job is not the message — it is deciding **which half of this
mechanism can never be changed again**, so that a future package manager, plugin path,
or marketplace is an *addition* rather than a migration.

| | Consumer side (`requires:` in `DAFNE.md`) | Supplier side (how the runtime knows what it has) |
|---|---|---|
| Lives in | published, forked, vendored grove repos | the ambient runtime |
| Can be migrated later? | **No** — you cannot edit other people's repos | **Yes** — D0: the ambient runtime improves for free on every machine |
| Therefore | semantics must be right **now** | needs no design today beyond **one function to hide behind** |

The entire forward-compatibility budget goes into one seam:

```
dafne:        effective_requires(node_root)              # frozen — published groves depend on this
              requirements_with_provenance(node_root)    # frozen — same recursion, richer answer
orchestrator: installed_capabilities()                   # soft — body replaceable at will
```

**The acceptance test for this whole design:** when machinery delivery moves from
`plugins/` to `uvx --from git+…` (`packaging-strategy.md` Strategy B), to
`$XDG_DATA_HOME/diotima/plugins/`, to a distro package, to a marketplace-installed
store — **only `installed_capabilities()`'s body changes.** Zero groves edited, zero
manifests migrated, zero call sites touched.

The anticipated future body is a readdir over plugin directories, each installed plugin
declaring what it provides — structurally the mirror of `discover_grove_banks`.
**Build none of it.** Freezing a supplier-side file format with one capability in
existence is the zero-instance rule verbatim, and the seam means nothing is lost by
waiting.

### The three layers, and which one is allowed into the refusal

| Layer | Question | Owner | Today | Grows into |
|---|---|---|---|---|
| **Declaration** | what does this node need? | the grove, `DAFNE.md` | `requires:` | unchanged, forever |
| **Resolution** | is it here? | runtime probe | 1 entry, path-exists | plugin-path scan, package-manager query |
| **Provision** | where do I get it? | catalog | one sentence in the message string | fetched marketplace index |

**Only Resolution feeds the refusal decision.** Provision decorates the message and
nothing else — a runtime with no catalog at all still refuses correctly, it just says
less. That separation is what keeps a marketplace additive.

A `name → repo` catalog (`anki: diotima-garden/anki-mcp`) is the right eventual shape
and the wrong thing to build today: with one capability it is a line of text. It
becomes a file when there are three. An absent catalog entry must degrade to a plain
*"unknown capability `X`"* — never an error, or a 2028 grove cannot be opened by a
2026 runtime.

### `installed` is a question, not a list

The sharpest reason a maintained inventory loses: `.venv/` is gitignored in both
plugins (`plugins/anki-mcp/.gitignore:6`, `plugins/dafne/.gitignore:1`), so **every
fresh clone — `--recursive` included — has `plugins/anki-mcp/server.py` but no
`plugins/anki-mcp/.venv/bin/python3`**, which is the interpreter `.mcp.json` actually
invokes. A hand-kept installed-list would report `anki: yes` on a machine where the
pipeline cannot work. The probe is evaluated at query time, always.

---

## The instance this bullet fixes (it is not hypothetical)

Two reachable states leave `anki` genuinely unavailable:

1. `git clone` without `--recursive` → `plugins/anki-mcp/` is an empty directory, no
   `server.py`.
2. **Any** fresh clone, `--recursive` included → no `.venv/`, so the interpreter named
   in `.mcp.json` does not exist.

State 2 is the default state of every new adopter's checkout. In both, the pipeline
today does **not** stop at the gate: it reads `context.md`, **spawns the background
compile fork**, and only then dies on `mcp__anki__sync`
(`.claude/commands/pipe/add-cards-to-grove.md:11-17`). That is the "deep pipeline
failure" the bullet names, verbatim.

---

## Manifest change: silence means "adds nothing"

`requires:` absent already yields the empty set — `manifest.py:58` reads
`set(manifest.get("requires") or [])`, and `parse_manifest` returns `{}` for a missing
file or missing frontmatter (`manifest.py:22-34`). **No code change needed to support
an absent clause.**

But the four leaf manifests currently carry an explicit `requires: []`, which teaches
the wrong convention by example — a grove author copying `spanish` learns "declare an
empty list," when the truth is *silence means: I inherit everything and add nothing*.

**Delete the `requires: []` line from:**

- `groves/spanish/DAFNE.md`
- `groves/english/DAFNE.md`
- `groves/instruments/DAFNE.md`
- `groves/social-dynamics/DAFNE.md`

Leave `deck`'s `requires: [anki]` alone — it is the only node in the tree that
introduces a requirement. After this edit, **every `requires:` line in the tree is a
real claim.**

Each is a separate grove-repo commit plus a submodule pointer bump in master. Note
`groves/spanish/parents/language/DAFNE.md` carries an explanatory paragraph about why
its own `requires: []` is correct despite `deck` requiring anki; if that line is
dropped too, rewrite the paragraph to explain the union rather than the empty list.
(`language` and `deck` are their own repos, reached through the groves' `parents/`
mounts — a change there is a third repo plus nested pointer bumps. Dropping
`language`'s line is optional; the four leaves are the ones grove authors copy.)

---

## Verified findings (do not re-derive)

Each checked against the tree on 2026-08-29.

### dafne

| Fact | Evidence | Consequence |
|---|---|---|
| The union walk already exists, with a cycle guard | `manifest.py:46-63` `effective_requires` | Provenance is the same recursion retaining more; not a new traversal. |
| Missing `requires:` is already empty, not an error | `manifest.py:58` | The manifest cleanup above needs no engine change. |
| Parent enumeration is readdir, sorted | `manifest.py:37-43` `parent_dirs` | Provenance ordering is deterministic for free. |
| dafne imports `yaml` | `manifest.py:16` | Anything that reads a manifest must run under `plugins/dafne/.venv/bin/python3`. |
| Semantic-token convention is established here | `compiled-is-fresh.py:1-9` — *"Exit 0 and print FRESH or STALE to stdout — the caller branches on that token, not the exit code. Exit non-zero only for a genuine error"* | The refusal CLI must follow this exactly, including the imperative tail ("Stop and report this."). |
| dafne is whitelisted per-script with its venv interpreter | `.claude/settings.json:60-62` | A new Bash-invoked script needs its own allow rule; `:*` does not match mid-path prefixes (`settings.json:78`). |

### The tree's actual requirements

| Fact | Evidence |
|---|---|
| `deck` is the only declarer | `groves/spanish/parents/language/parents/deck/DAFNE.md` → `requires: [anki]` |
| spanish / english / instruments inherit `{anki}` through the union | `deck` ← `language` ← spanish, english; `deck` ← instruments |
| social-dynamics is a root node requiring nothing | `groves/social-dynamics/DAFNE.md`, no `parents/` |
| spanish's provenance path | `parents/language/parents/deck` |
| instruments' provenance path | `parents/deck` |

### Runtime / harness

| Fact | Evidence | Consequence |
|---|---|---|
| The anki capability is delivered as an MCP server with a venv interpreter | `.mcp.json` — `plugins/anki-mcp/.venv/bin/python3 plugins/anki-mcp/server.py` | Both path components are probe candidates; the interpreter is the discriminating one. |
| `.venv/` is gitignored in both plugins | `plugins/anki-mcp/.gitignore:6`, `plugins/dafne/.gitignore:1` | See "installed is a question." |
| Both pipelines spawn the compile fork **before** the first anki call | `add-cards-to-grove.md:11-17`, `tackle-feedback-on-grove.md:11-17` | The ordering constraint below is real, not theoretical. |
| The orchestrator layer exists and has this exact role | `system/diotima/bank_union.py:1-8` | `capabilities.py` is a sibling, not a new layer. |
| Orchestrator scripts are whitelisted with dafne's interpreter | `.claude/settings.json:44` — `Bash(plugins/dafne/.venv/bin/python3 system/diotima/graduate-banks.py:*)` | Copy this shape for the new script. |

---

## Implementation spec

### 1. `plugins/dafne/manifest.py` — provenance

```python
@dataclass(frozen=True)
class Requirement:
    name: str
    declared_by: tuple[PurePosixPath, ...]   # relative to the queried node; "." = the node itself


def requirements_with_provenance(node_root: Path) -> list[Requirement]:
    """Same recursion as effective_requires, retaining where each name came from.
    Paths are relative to the queried node, POSIX-normalized. All declaring nodes
    are listed, not just the first found. Sorted by name; declared_by sorted by
    path — determinism, same as parent_dirs."""
```

**Why paths and not node names.** Because parents are vendored physically under
`parents/`, the relative path *is* the inheritance chain spelled out —
`parents/language/parents/deck` reads as "via language, via deck" and is
copy-pasteable into a `cat`. A basename gives a leaf with no route to it, and two
nodes in one tree can share a basename (a fork of `deck` is legitimately distinct —
the record rules identity is *content* or *URL*, never assigned, so there is no node
name field, only the directory name the child chose when mounting). Under names, a
diamond renders as `declared by deck, deck`. Position is already DAFNE's identity
mechanism everywhere else (readdir for parents, position for `.private/`, no `id`
field); provenance stays consistent with that.

`effective_requires` stays as-is — it is the cheap answer for the decision, and may be
reimplemented as a projection of the richer one if the builder prefers one traversal.

**Test fixtures to add**, matching the existing suite's style (`plugins/dafne/tests/`):
a node declaring its own requirement (`declared_by == (".",)`); a two-level chain where
only the grandparent declares (the production spanish shape); a diamond where two
distinct paths declare the same name (assert **both** paths present); a node with no
`requires:` key at all (empty list, no exception); an unknown capability name passing
through untouched.

### 2. `system/diotima/capabilities.py` — the probe

```python
CAPABILITIES = {
    "anki": _anki_installed,   # today: does the .mcp.json interpreter + server.py exist
}


def installed_capabilities(project_dir: Path) -> set[str]:
    """Probed at query time, never a maintained list. The single seam that a future
    plugin manager replaces without touching dafne, groves, or call sites."""
```

**Where the probed path comes from: read it out of `.mcp.json`, do not hardcode it.**
The `anki` probe resolves the `command` of the `anki` server entry
(`.mcp.json` → `mcpServers.anki.command`) and checks that it exists, plus the first
`args` entry (`server.py`). Hardcoding `plugins/anki-mcp/.venv/bin/python3` drifts
silently the day `.mcp.json` changes — which the uvx migration in the adjacent findings
will do. Reading it keeps the probe tracking reality, and downgrades that migration
note from a silent-failure bug to a maintenance task. `.mcp.json` is project-root, not
`.claude/`, so this does not tie the orchestrator to a vendor path.

Rules for this file:

- **Probe structurally, never behaviorally.** Check that the machinery exists on disk.
  **Never** call AnkiConnect — that would make pipeline start depend on a running
  desktop app. "Anki installed but not launched" is a different failure class that
  anki-mcp surfaces on its own, and is explicitly out of scope here.
- **A capability with no entry in `CAPABILITIES` is *unknown*, not *missing*.** It
  yields a distinct message and **blocks nothing**. See the ruling section below.
- **Defensiveness is inherited.** Like `invoke-mneme-on-groves.py`, a failure inside
  the probe must not become the user's error; degrade to a readable message.

### 3. `system/diotima/check-requires.py` — the CLI

```
plugins/dafne/.venv/bin/python3 system/diotima/check-requires.py <node-dir>
```

**Why a CLI here, when bullet 1 deliberately avoided one:** bullet 1's caller was a
hook — Python calling Python, so a script wrapper was ceremony. This caller is an
**LLM reading a pipeline step**, which can only invoke things through the Bash tool. A
CLI is the interface, not a wrapper around one.

Output follows `compiled-is-fresh.py`'s convention exactly — **exit 0 with a token on
stdout; non-zero only for genuine errors** (bad usage, node directory missing):

```
REQUIRES_SATISFIED: anki — proceed.
```

```
REQUIRES_UNSATISFIED: groves/spanish requires 'anki', which is not available here.
  declared by parents/language/parents/deck
  missing: plugins/anki-mcp/.venv/bin/python3
  fix: set up the anki-mcp plugin (see /onboard), or use a grove that requires nothing.
Stop and report this to the user — do not continue the pipeline.
```

```
REQUIRES_SATISFIED: no requirements declared — proceed.
```

```
REQUIRES_UNKNOWN: groves/xyz requires 'video-transcode', which this runtime has never
  heard of. declared by parents/media
  This is not a failure — an unknown capability blocks nothing. Continue, and expect
  any step that needed it to be unavailable.
```

**Token precedence when a node has both kinds.** Reachable as soon as a second
capability exists: any unsatisfied name wins — print `REQUIRES_UNSATISFIED` with every
unsatisfied name, and list unknown names underneath it as a notice. Exactly one token
leads the output, always.

Add the allow rule in `.claude/settings.json`, copying line 44's shape:

```
"Bash(plugins/dafne/.venv/bin/python3 system/diotima/check-requires.py:*)"
```

### 4. The call sites — preflight in both pipelines

Insert as **step 0** — before the `read <grove-dir>/context.md` step — in both
`.claude/commands/pipe/add-cards-to-grove.md` and
`.claude/commands/pipe/tackle-feedback-on-grove.md`:

```
- bash: plugins/dafne/.venv/bin/python3 system/diotima/check-requires.py <grove-dir> [mandatory]
  Why: this pipeline needs anki. Refuse here — before the background compile fork is
  spawned — rather than dying deep at the first mcp__anki__ call.
  REQUIRES_UNSATISFIED → stop and report. REQUIRES_UNKNOWN or REQUIRES_SATISFIED → proceed.
```

**Why the pipeline and not `SessionStart`.** In master, cwd is the monorepo with four
mounted groves carrying two different effective-requires sets; there is no single
subject for a session-start refusal. The real "open a grove" moment in today's runtime
is a pipeline receiving `<grove-dir>`. This is a deliberate refinement of the bullet's
"opening a grove" wording — the same kind of refinement bullet 1 made to "or dies."

**Phase 4 costs nothing extra.** When the `diotima` launcher lands and cwd genuinely
*is* a grove, the launcher becomes a second call site of the same two functions.
Neither dafne nor the probe changes.

---

## Ordering constraint — a real bug if ignored

Both pipelines spawn the compile fork at step 2, before the first anki call at step 3.
Compilation is pure text and needs no capability, which is exactly why it is tempting
to put the check after it. **A check placed after step 2 leaves an orphaned background
fork on every refusal.** The preflight is step 0 or it is wrong.

---

## Rulings made here that the record left open

The decision record parks "the exact vocabulary of `requires:`" as still-open
(`grove_inheritance_decisions.md`, D2). This session rules the two questions the
refusal path forces:

**1. Refusal attaches to operations, never to opening.** Reading, compiling, or editing
a grove's text with no Anki installed is legitimate and must stay unblocked. Only the
pipeline that actually needs the capability refuses.

**2. A capability the runtime cannot name blocks nothing.** It produces a notice
(`REQUIRES_UNKNOWN`), not a refusal. Blocking it would resurrect exactly the
forward-incompatibility the unknown-fields rule was built to avoid, and would demote
"a grove requiring nothing is first-class" to "a grove requiring nothing *I know* is
first-class." The two rulings are one rule: **refuse what you can name and cannot
satisfy; notice what you cannot name.**

---

## Doors held open, nothing built

| Door | Trigger to build | What is pre-paid |
|---|---|---|
| Supplier-side `provides:` declaration | a second capability, or plugins arriving from outside `plugins/` | `installed_capabilities()` is the seam; its body is free to become a scan |
| `name → repo` provision catalog | a third capability (with one, it is a sentence) | Provision is already separated from Resolution; absent entries degrade to a notice |
| Capability version constraints (`requires:` items as mappings, not strings) | first real version-skew incident | the unknown-fields rule already tolerates the richer form; **no tolerance code today** |
| Soft/optional requirements (grove degrades instead of refusing) | first grove that genuinely has a degraded mode | operation-scoped refusal already means a capability only blocks what needs it |
| Local mask (child suppresses an inherited requirement) | first grove that must suppress one | union does not foreclose it (already deferred in the record) |
| Transitive plugin→plugin dependencies | first plugin with a dependency | the probe answers per-name; nothing assumes a flat world |

---

## Exit criteria

- `requirements_with_provenance(groves/spanish)` returns exactly
  `[Requirement("anki", (PurePosixPath("parents/language/parents/deck"),))]`.
- `requirements_with_provenance(groves/social-dynamics)` returns `[]`, and the
  preflight prints `REQUIRES_SATISFIED: no requirements declared`.
- With `plugins/anki-mcp/.venv` temporarily renamed, `/pipe:add-cards-to-grove
  groves/spanish` stops at step 0 with the provenance path in the message and **no
  background compile fork spawned**. Restore the venv afterward.
- No `requires: []` line remains in any of the four leaf grove manifests, and
  `effective_requires` still returns `{anki}` for spanish, english, and instruments.
- A fabricated node declaring an unnamed capability yields `REQUIRES_UNKNOWN` and the
  pipeline proceeds.
- Nothing in `plugins/dafne` mentions anki, anki-mcp, `.mcp.json`, or installation.

---

## Adjacent findings surfaced during this design (not in scope)

- **The preflight cannot diagnose its own absence.** It runs under
  `plugins/dafne/.venv/bin/python3`, which is gitignored and therefore missing on the
  same fresh clone this bullet exists to serve. A missing dafne venv is an onboarding
  failure, not a capability refusal, and belongs to `/onboard` and issue #27 — but it
  means the very first run on a new machine still fails in a bare way. Worth naming in
  whatever bootstrap work follows.
- **`packaging-strategy.md` Strategy B (uvx delivery) will change the probe.** When
  `.mcp.json` becomes `uvx --from git+…@v1.0 anki-mcp`, "does this path exist" stops
  being the right probe. That is exactly the change `installed_capabilities()` exists
  to absorb — but whoever does the uvx migration must update the probe in the same
  change, or it silently reports `anki` missing forever.
- **dafne still has no logging utils submodule** (raised 2026-08-29, prior session).
  The observability contract says every hook and worker writes a trigger log; the new
  script is a worker with no log surface. Track separately.
