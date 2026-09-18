# Assisted Parent-Update Flow ("tend parents") — DAFNE Phase 3, bullet 4

> **STATUS: DESIGNED, DEFERRED — do not build (user ruling, 2026-09-16, same day as
> this document's own creation).** This designs the **author** flow: re-pinning a
> parent submodule inside a grove you own, with a compiled-output diff before you
> accept. Hours after it was written, the scope question that had not been asked got
> asked: *who actually needs this?* The answer split one bullet into two flows, and
> only the other one ships. See **"The two flows"** immediately below before reading
> any further — everything after it is the deferred branch.
>
> **Un-defer trigger:** the first time a parent you do **not** own publishes an
> improvement you want. That is the instance this design is disciplined by and
> currently lacks. Until then, re-pinning your own parents is two git commands in a
> session, not a subsystem.

---

## The two flows — why this document is the deferred one

D4 was written in 2026-07 from the seat of a grove **author**, before the grove
**consumer** existed as a concept in this record. That framing hid a split:

| | **Flow A — sync** (ships) | **Flow B — tend parents** (this document) |
|---|---|---|
| Who | anyone who cloned a grove | the grove's owner |
| What moves | the grove fast-forwards to its author's published state | one parent's pin is re-pointed, committed in the child |
| Git | `git pull --ff-only` + `git submodule update --init --recursive` | fetch in parent, checkout tip, `git add`, `git commit` in child |
| Decisions | one: pull or not | per-parent: accept this new pin? |
| Commits authored | none, ever | one per accepted bump |
| Recursion | free — the author's pins arrive with the pull | the hard question this document spends itself on |
| Real instances | the user asking for it, plus every future adopter | **zero** — no cross-owner parent/child pair exists |

**Flow B's hard parts — the ownership ruling, the compiled-diff-before-accept, the
scratch-worktree substrate — are all machinery for deciding whether to accept someone
else's change to a parent you depend on. No such someone else exists yet.** By this
record's own doctrine (*"Zero-instance problems are not designed... Abstraction needs
two real instances"*), building it now is designing from zero instances. The analysis
below is kept in full as the reasoning trail — the same treatment D4's own
range-vs-pin analysis got — so that when the trigger fires, none of it is re-derived.

Flow A is specified in `dafne_plan.md` Phase 4 (consumer sync nudge). It needs none of
what follows: no ownership ruling (the consumer authors no commits), no compiled diff
(they are not making an authorship decision), no scratch worktree (nothing is swapped
in place).

---

*Created 2026-09-16. Architect-owned design record for the last bullet of
`dafne_plan.md` Phase 3. Every code claim is verified against the tree at `file:line`.
Written so a builder agent can execute without re-deriving anything — whenever the
un-defer trigger above fires.*

**Scope:** how a pinned parent's upstream improvement reaches a child grove, and what
the runtime shows before it commits a new pin. Does **not** cover: installing
capabilities, `SessionStart` injection (bullets 2–3, done), the consumer sync flow
(Flow A, Phase 4), or the rest of Phase 4 (picker, MRU, grove creation).

---

## Recap — what this bullet is, in plain terms

D4 (`grove_inheritance_decisions.md`) chose **pins over version ranges**: a child grove
freezes each parent at an exact submodule commit, so its compiled output never changes
under you. The cost of that choice is that an improvement to a parent — a better
`deck-defaults.md`, a fixed `language-defaults.md` — never reaches a child on its own.
Someone has to notice, look at what changed, and choose to re-pin.

D4 explicitly moved that someone's job into runtime UX rather than the format: *"an
assisted-update flow ('tend parents') fetches submodule upstreams, nudges on new
commits, shows the compiled-output diff, and commits the new pin."* This document
designs that flow. It is pure propagation UX — no grove's manifest changes because
this bullet exists, per D0's ambient-improvement guarantee.

---

## The decision in one line

**dafne reports drift in the `parents/` tree it already understands; the CLI shows the
compiled-output consequence of accepting one hop of it; nothing here ever touches a
capability probe or an orchestrator concept.** This bullet has only one role, unlike
bullet 2's three — there is no "is it installed" question, because git pins are not a
capability.

---

## The load-bearing ruling — flag this to the user before building

**A child may only commit a pin bump in its own `parents/` — never inside a vendored
parent's own `parents/`.**

`spanish/parents/language/parents/deck` is a real, physically-checked-out nested
submodule (verified: `parents/language/.gitmodules` at
`diotima-garden/spanish/parents/language`, nested `parents/deck` present). It is
tempting to let the flow walk all the way down and re-pin `deck` from inside `spanish`'s
checkout, since today one person (you) owns every repo in this chain. That would be
designing from the accident of the current instance, against the sovereignty invariant
`product-vision.md` states as a protected constraint: *"groves are sovereign... publishing
a grove must never require touching the orchestrator"* — and by the same logic, never
require touching a grove you don't own. In the published-grove model this whole record
protects, `spanish`'s owner does not in general own `language`'s repo. A commit inside
`parents/language/parents/deck`, made from within `spanish`'s working tree, only means
anything once pushed to `language`'s own remote — a repo `spanish`'s owner has no right
to push to as a stranger.

**Resolution:** fetch and report recursively (read-only, cheap, harmless at any depth);
commit only at depth 1 (the node's own direct `parents/<name>` entries). Deeper drift
renders as **information**, not an action: *"`parents/language` is 3 commits behind its
own upstream; note `parents/language` also carries its own outdated `deck` pin — that's
language's maintainer's call, not yours."* This satisfies the plan's literal wording
("fetch upstreams of everything under `parents/`, recursively") without inventing a
write path the record's ownership model forbids.

*(Put this to the user as a ruling before implementation starts, the same way Phase 3's
manifest-injection bullet put the per-grove-vs-whole-garden bank scoping to them rather
than assuming — see `dafne-plan-details/phase-3.md`.)*

---

## Layer placement

| Component | Lives in | Knows | Must never know |
|---|---|---|---|
| **Report** (`tend_parents.py` — fetch, drift, diff) | `plugins/dafne/` | how to walk `parents/`, git plumbing over that tree, how to compile a node's entry files | anki, capabilities, `system/diotima/` |
| **Apply** (checkout + commit one pin) | `plugins/dafne/` — same module, a distinct, never-whitelisted entry point | one child node, one direct parent, one target SHA | nothing about siblings or grandparents |
| **Skill** (`plugins/dafne/skills/tend-parents/`) | `plugins/dafne/skills/` | how to call Report, present its output, ask the user, call Apply on a yes | — |

**Nothing lives in `system/diotima/`.** That layer's entire job, established by bullet
2, is *"is it materialized on this machine"* — a capability probe
(`system/diotima/capabilities.py:1-8`). A submodule pin is not a capability; there is no
probe question here. A builder reaching for `system/diotima/` by analogy to bullet 2 is
the mistake this section exists to head off.

This mirrors bullet 2's own frozen/soft split, but the axis is different: bullet 2 froze
the *consumer* side (`requires:`, published and unchangeable) and kept the *supplier*
side soft. Here there is no consumer/supplier split — both halves are runtime-side and
equally revisable, so both live in the one place that already owns `parents/`: dafne.

---

## "Diff of what?" — entry-file discovery, no new manifest field

The plan says "shows the compiled-output diff." A node's manifest carries no `entry:`
field naming which `.md` file(s) are its compiled products — adding one would be a
`DAFNE.md` format change, and D1's ruling on the record is explicit that the format's
reversibility is **LOW** once a stranger authors one.

No new field is needed. `include_graph.collect_inputs(entry, seen)`
(`plugins/dafne/include_graph.py:68-83`) already returns every file transitively
`#include`d from an entry point. The rule: **an entry file is any top-level `.md` in the
node (not under `parents/` or `.private/`) whose `collect_inputs` output contains a path
inside the parent being bumped.** Concretely, for `spanish/rioplatense-anki.md`
compiling to `rioplatense-anki.compiled.md`
verified on disk at `diotima-garden/spanish/rioplatense-anki.md`, 2026-09-16), bumping
`parents/language` means: does `rioplatense-anki.md`'s transitive input set intersect
`parents/language/`? It does (via `language-defaults.md`), so it is the entry file to
recompile before/after. A node with no entry file touching the bumped parent at all
still gets a correct, empty diff — nothing to show, nothing wrong.

This reuses code that already exists and is already unit-tested
(`plugins/dafne/tests/`), and rules the manifest-field question out rather than leaving
it open.

---

## Preconditions — dirty tree refuses before anything is touched

Per this project's own structural lesson (*"silent failure is this system's default
failure mode"*, `structural-lessons.md:19-24`) and the top-level rule to run `git status`
before any command that could discard uncommitted work: **before fetching or checking
out anything, walk every node in the tree (the subject node and every `parents/`
descendant reachable from it) and require a clean `git status --short` in each.** A
dirty submodule anywhere in the walked tree — the subject's own uncommitted edits, or a
parent someone hand-modified in place — aborts with a report of which path is dirty and
why, before a single `git fetch` runs. This is a **refuse-early** contract, the same
shape as bullet 2's `REQUIRES_UNSATISFIED` preflight: cheap to check, expensive to
recover from if skipped, since the apply step's revert-on-decline path assumes the tree
was clean before it started.

---

## Divergence is not behindness

Submodules are checked out at a detached HEAD — there is no tracking branch, so `git
rev-parse @{u}` resolves to nothing (verified: `spanish/parents/language` is at commit
`7ba8124` with no local branch, per `git status --short` showing empty / clean detached
state). The remote's default branch must be resolved explicitly:

```
git ls-remote --symref <remote-url> HEAD
```

gives the remote's default branch name without a local checkout of it, then `git fetch`
that branch and read its tip SHA. Compare against the pinned SHA with:

```
git merge-base --is-ancestor <pinned-sha> <tip-sha>
```

Three distinct outcomes, not two:

- **ancestor, and different** → genuinely behind — a real update is available.
- **identical** → current, nothing to report.
- **not an ancestor** (exit code 1, but not because of an error) → **diverged**, not
  behind. This happens when the parent's history was rewritten upstream (force-push,
  rebase) — real in a fork-heavy ecosystem, and it must never render as "update
  available," since fast-forwarding to a non-descendant SHA is not what "assisted
  update" promised.

A remote that cannot be reached at all (network failure, repo moved) is **skip with a
notice**, not a hard error for the whole run — one bad parent must not block reporting
on the rest of the tree.

---

## Semantic tokens

Following the convention this engine already established
(`compiled-is-fresh.py:1-9` — *"Exit 0 and print FRESH or STALE to stdout — the caller
branches on that token, not the exit code. Exit non-zero only for a genuine error"*):

**Report** (`tend_parents.py report <node-dir>`, exit 0 unless usage/IO error):

```
PARENTS_CURRENT: every direct and nested parent is at its upstream tip.
```

```
PARENTS_BEHIND:
  parents/language — 2 commits behind (7ba8124..3f9c1a0)
  parents/language/parents/deck — 1 commit behind, nested — language's own call, not yours
Run `tend_parents.py diff <node-dir> parents/language` to preview, or `apply` to accept.
```

```
PARENTS_DIVERGED:
  parents/language — pinned commit 7ba8124 is not an ancestor of upstream's tip 9e2b001
  (history was rewritten upstream). Not auto-resolvable — investigate manually.
```

```
PARENTS_UNREACHABLE:
  parents/language — could not fetch (network error) — skipped, rest of tree reported below.
```

**Precedence when a tree has more than one state** (the same question bullet 2 had to
settle, `requires_refusal.md:293-296`): list every state found, but the token that leads
the output is the most actionable one — `PARENTS_DIVERGED` outranks `PARENTS_BEHIND`
outranks `PARENTS_UNREACHABLE` outranks `PARENTS_CURRENT`. A tree that is simultaneously
behind on one parent and diverged on another leads with `PARENTS_DIVERGED` so the
riskier state is never buried under routine news.

**Diff** (`tend_parents.py diff <node-dir> <direct-parent-path>`): computes the affected
entry file(s) per the rule above, compiles each at the current pin (before, straight
from `node-dir` as it sits) and at the fetched tip (after — see the scratch-tree
mechanism below), and prints a unified diff per entry file. No entry files affected →
prints that explicitly, does not print an empty diff silently.

**Why "after" cannot be a checkout-then-revert, and what it is instead.** An earlier
draft of this design had `diff` check out the fetched tip in the real submodule and
revert it afterward "unconditionally." That is not a guarantee a process can make — a
killed session (or a crash inside the compile step) leaves the submodule at the wrong
SHA with no automatic recovery, and the dirty-tree precondition then blocks every
subsequent `report`/`diff`/`apply` on that node with no stated way out. `diff` must
never touch the real checkout at all.

Because includes are `.`-relative to the including file (`include_graph.py:27-34`), the
compiler needs the swapped parent to physically sit at `parents/<name>` in whatever tree
it reads — it cannot be pointed at a parent living elsewhere.

**The scratch tree must be real directories, not symlinks.** A symlink farm was the
first draft of this mechanism and is wrong: `resolve_include_path` computes `own_root =
find_node_root(from_file)` from the *real*, symlink-resolved path
(`include_graph.py:16-24, 43-49`). Once `preprocess.py` follows a symlink at
`<scratch>/parents/language` into the real `diotima-garden/spanish/parents/language`,
that file's own includes (`./parents/deck/...`) resolve against the *real* tree, not the
scratch one — and the swapped parent (an actual directory, not a symlink) would sit
beside symlinked siblings, so the two halves of one compile resolve against different
roots. This is the exact fidelity gap `dafne_plan.md`'s Phase 1 exit note already
recorded for `dafne_simulation`'s symlinked `parents/` mounts. Known-bad substrate here,
not a neutral shortcut.

The mechanism instead uses nested worktrees, so every path in the scratch tree is
physically inside it:

1. `git worktree add --detach <scratch> <node-dir's current HEAD>`, run inside
   `node-dir`'s own repo — a full, real second working copy of the node at its present
   commit, empty `parents/` (worktrees don't check out submodules on their own).
2. `git submodule update --init --recursive` inside `<scratch>` — populates every
   parent, at their *currently pinned* SHAs, as real (non-worktree) submodule checkouts,
   physically nested exactly as they are in `node-dir`.
3. For the one parent being diffed, `git worktree add --detach
   <scratch>/parents/<name> <fetched-tip-sha>` run inside **that submodule's own `.git`**
   (not the outer node's) — replaces just that one directory's checkout with the tip
   commit, still a real, physically-nested directory.
4. Compile the entry file from `<scratch>` — this is the "after" output. Every include
   resolves inside `<scratch>`'s own tree, identically to how it would in `node-dir`,
   because the substrate is now structurally identical, not merely visually similar.
5. Tear down in reverse, always, including on error: `git worktree remove
   <scratch>/parents/<name>` (inside the parent's `.git`), then `git worktree remove
   <scratch>` (inside `node-dir`'s `.git`). Neither the outer `git worktree add` nor the
   inner one touches `node-dir` or its real `parents/<name>` checkout — both are
   additive registrations of a second working directory against the same repository,
   which is why this needs no exception to the "never checkout/reset/commit" rule.

**Faithfulness check, not just a convenience test:** compiling `<scratch>`'s entry file
at the node's *current* pin (before touching the diffed parent) must byte-match
compiling `node-dir`'s own entry file directly. A silent divergence there would mean the
scratch substrate is producing a *plausible but wrong* "before," which would make every
diff plausible but wrong too — this system's stated default failure mode
(`structural-lessons.md:19-24`), and worse than an outright error precisely because it
would not look wrong. This check belongs in the exit criteria, not only in a test file.

This is why `diff` can stay in the whitelist below while `apply` cannot: every git
operation `diff` performs (`fetch`, `worktree add` ×2, `worktree remove` ×2,
`submodule update` inside a scratch copy) is additive or read-only against the real
checkout, none of it is checkout/reset/commit/push against tracked state, and a crash
mid-`diff` leaves at worst a stray worktree registration and a scratchpad directory —
cheap to find (`git worktree list`) and remove by hand, never a corrupted pin that
blocks the next run.

---

## Read vs. mutate — why this is two entry points, and only one is ever whitelisted

`modes/meta/builder/security.md:32-40` is explicit and unconditional: *"Any git command
that stages, commits, or pushes changes"* and *"Destructive operations: `rm`, `git
reset`, `git checkout --`, `git clean`"* **must never be added to the allow list — they
should always surface for user confirmation.** Verified against the current
`.claude/settings.json`: no `git checkout`, `git commit`, or `git push` appears in the
whitelist anywhere today (grep run against the full file, 2026-09-16).

If `tend_parents.py apply ...` — the subcommand that checks out a new SHA and commits
the pin — were whitelisted the same way `check-requires.py` is
(`.claude/settings.json:45`), every future apply would run without the confirmation the
security policy exists to guarantee, merely because the mutation happens inside a
script's `subprocess` calls rather than as a literal `Bash` tool invocation. That would
be a structural end-run around a deliberate policy, not a design choice — the exact
"enforce invariants with hooks, not prose" logic in reverse: a hook (the permission
system) that *should* fire is bypassed by moving the mutation one layer down.

**Ruling:** `report` (fetch, rev-parse, merge-base — no writes at all) and `diff` (the
scratch-worktree mechanism above — additive-only against the real checkout) are both
genuinely read-only against tracked state and get a whitelist entry each, same shape as
line 45. `apply` performs the real checkout and commit and is **never whitelisted** —
every invocation surfaces the normal Bash confirmation prompt, once per accepted parent
bump, which is exactly the human decision point D4's "on acceptance" clause describes.
The skill's job is to run `report`, show the user `diff` for anything behind, and only
then invoke `apply` — the prompt the user sees at that point *is* the "on acceptance"
gate, not a redundant one.

**No push, anywhere, in any subcommand.** D4's own words are precise: *"commits the new
pin — the commit is the audit trail, `git revert` the rollback."* Nothing in that
sentence is push. `security.md:24-26`'s narrow push exception ("allowed when the user
explicitly asks for it in the moment") stays exactly that — this flow does not invoke
it, and a builder must not add a push step to `apply` on the assumption that a commit
implies one.

---

## `subprocess`, not `git -C`, not chained Bash

This flow is unavoidably cross-repo (a submodule's own git commands must run with the
submodule as the working directory), but two standing rules apply to how it is invoked
from the CLI surface:

- The global instruction bans `-C <path>` at the Bash-tool level ("the working directory
  is already the project root"). `tend_parents.py` sidesteps this entirely by never
  using `-C` itself — internally it calls `subprocess.run([...], cwd=parent_path)` for
  each git operation, so the process's own working directory changes, not an argument to
  git. The one and only Bash-tool-visible command is the single
  `plugins/dafne/.venv/bin/python3 plugins/dafne/tend_parents.py report <node-dir>`
  invocation.
- `.claude/rules/bash-commands.md` bans chaining with `&&`/`;`/`|` in one Bash block.
  Irrelevant to this script's *internals* (Python calling `subprocess` isn't a Bash
  block), but binding on the **skill markdown** that invokes it — each `report` /
  `diff` / `apply` call is its own bash block, never chained.

---

## Who resolves `<node-dir>`

`tend_parents.py` never resolves the subject itself — it takes `<node-dir>` as a plain,
already-concrete path argument, exactly as `preprocess.py <entry-file>` and
`include_graph.py <entry-file>` already do. **dafne must not import
`system/diotima/garden.py`** — `layers.md`'s dependency direction is upper-knows-lower,
and dafne is the lower-level engine here (parallel to how bullet 2 kept anki, `.mcp.json`,
and the orchestrator entirely out of `plugins/dafne`). If dafne resolved
`$DIOTIMA_GARDEN` itself, the dependency would point the wrong way.

Concretely, the grove is outside the project root once ruling (a) unmounted `groves/*`
(`dafne-plan-details/phase-3.md`), so `<node-dir>` is necessarily an absolute path or one
relative to `$DIOTIMA_GARDEN` — never a project-root-relative path, since no such grove
exists under the project root to be relative to. `.claude/rules/portability.md`'s
project-root-relative rule governs paths *inside this repo*; it does not and cannot
apply to a path naming a location in a separate garden repo. The resolution happens one
layer up, at the call site: the `tend-parents` skill is invoked with a concrete grove
path already in hand — from the current session's `SessionStart`-injected grove context
(if cwd is a grove) or from `system/diotima/garden.py`'s `resolve_subject()` if the skill
is invoked over the whole garden — and passes that resolved path straight through as
`<node-dir>`. This is the same division bullet 2 already established: the call site asks
using vocabulary dafne and the orchestrator both understand (a path), neither one
reaches into the other's resolution logic.

The plan's own carried-forward note applies directly here too: `$DIOTIMA_GARDEN` narrows
to a single grove when set by `bin/diotima`'s launch, so a skill that means "tend every
grove in the garden" must resolve via `garden.py`, not assume `$DIOTIMA_GARDEN` always
names the garden root (`dafne_plan.md`'s trailing note, 2026-09-07).

---

## Verified findings (do not re-derive)

| Fact | Evidence | Consequence |
|---|---|---|
| Parent enumeration is readdir, sorted, cycle-guarded recursion already exists | `manifest.py:38-64` `parent_dirs` / `effective_requires` | Depth-first walk for reporting reuses this shape; no new traversal primitive needed. |
| Entry-file → transitive input set is already computed, unit-tested | `include_graph.py:68-83` `collect_inputs` | Answers "diff of what" with existing code, no manifest field. |
| Semantic-token convention (`FRESH`/`STALE`, exit-0-with-token) is established | `compiled-is-fresh.py:1-9` | This bullet's tokens (`PARENTS_CURRENT` etc.) follow the same contract. |
| dafne is invoked per-script with its own venv interpreter, individually whitelisted | `.claude/settings.json:44-45, 61-63` | `report`/`diff` get their own new entries in the same shape; `apply` gets none. |
| No `git checkout`, `git commit`, or `git push` is whitelisted anywhere today | grep of full `.claude/settings.json`, 2026-09-16 | `apply` must not become the first exception; it stays prompted every time. |
| `git add`/`git diff`/`git log`/`git submodule status` are already whitelisted (read/stage-adjacent, not commit) | `.claude/settings.json:50-56` | Precedent for what "read-only enough to whitelist" has meant here so far; `apply`'s commit step is a different class from these and stays out. |
| Submodules sit at detached HEAD with no tracking branch | verified live: `diotima-garden/spanish/parents/language` at `7ba8124`, clean, no local branch | `@{u}` cannot be used; remote default branch must be resolved via `ls-remote --symref`. |
| Nested submodules are real, not hypothetical | `diotima-garden/spanish/parents/language/parents/deck` exists on disk with its own `.git`, `.gitmodules` | The ownership ruling above is disciplined by one real instance, not designed from zero. |
| `plugins/dafne` skills already exist as the pattern to extend | `plugins/dafne/skills/compile/`, `.../reverse-propagate/`, `.../compile-context/` | New skill is a sibling: `plugins/dafne/skills/tend-parents/SKILL.md`. |

---

## Implementation spec

### 1. `plugins/dafne/tend_parents.py`

```
plugins/dafne/.venv/bin/python3 plugins/dafne/tend_parents.py report <node-dir>
plugins/dafne/.venv/bin/python3 plugins/dafne/tend_parents.py diff <node-dir> <direct-parent-relpath>
plugins/dafne/.venv/bin/python3 plugins/dafne/tend_parents.py apply <node-dir> <direct-parent-relpath>
```

- `report`: dirty-tree check first (abort with a plain message naming every dirty path,
  no fetch attempted, if anything is dirty); then depth-first walk of `parents/` from
  `node-dir` via `manifest.parent_dirs`; for each node, `git fetch` + `ls-remote
  --symref` + `merge-base --is-ancestor`, classify per the three-outcome rule above;
  print the leading token plus every finding, direct and nested, nested ones annotated
  "not yours to bump here."
- `diff`: same dirty-tree check, scoped to `<direct-parent-relpath>` only (must be a
  direct child of `node-dir/parents/`, reject a nested path with a clear message
  pointing at the ownership ruling); fetch that one parent, compute affected entry
  files via the `collect_inputs`-intersection rule, compile each "before" straight from
  `node-dir`, build the scratch tree described above for "after," print unified diffs,
  and always tear down the scratch worktree and directory before exiting (success or
  error) — the real checkout in `node-dir` is never touched.
- `apply`: dirty-tree check; must operate on a direct parent only (same rejection as
  `diff`); checkout the fetched tip in that one submodule; `git add <parent-relpath>`;
  `git commit -m "tend: <parent-relpath> <old-short>..<new-short>"` in `node-dir`'s own
  repo. No push. On any failure after the checkout, revert the submodule to its
  original SHA before exiting non-zero — never leave a half-applied bump.

### 2. `plugins/dafne/skills/tend-parents/SKILL.md`

Modeled on `plugins/dafne/skills/compile/SKILL.md`'s shape: run `report`; if
`PARENTS_CURRENT`, say so and stop; if anything else, summarize the findings, and for
each direct parent behind, offer to run `diff` and show it, then ask the user
explicitly before running `apply`. One bash block per subcommand call, never chained,
per `bash-commands.md`.

### 3. `.claude/settings.json` additions

```
"Bash(plugins/dafne/.venv/bin/python3 plugins/dafne/tend_parents.py report:*)",
"Bash(plugins/dafne/.venv/bin/python3 plugins/dafne/tend_parents.py diff:*)",
```

No entry for `apply` — see the read-vs-mutate ruling above.

### 4. Tests (`plugins/dafne/tests/`)

Fixtures mirroring the existing suite's style: a two-level chain with the outer parent
genuinely behind (assert `PARENTS_BEHIND` names it); the same chain with the inner
(nested) parent also behind (assert it appears annotated, not offered for `apply`); a
diverged remote (rewritten history) classified as `PARENTS_DIVERGED`, not `PARENTS_BEHIND`;
a dirty submodule anywhere in the tree aborting `report` before any fetch; `diff` on a
node with no entry file touching the bumped parent, printing an explicit empty-diff
notice; `apply` rejecting a nested (non-direct) path.

---

## Exit criteria

Demonstrable against the one real instance in the tree — `$DIOTIMA_GARDEN/spanish` (on
disk today at `/home/papa/Documents/diotima-garden/spanish`) → `parents/language` →
`parents/deck`. Since production `language` is not guaranteed to be behind its upstream
at any given moment, "behind" and "diverged" states are manufactured for the
demonstration exactly as the Tests section fixtures do: point a scratch clone of
`spanish` at a local bare repo standing in for `language`'s remote, add one commit to
that bare repo (or force-push a rewritten history onto it for the diverged case), then
run the flow against the scratch clone. Nothing here depends on the real
`diotima-garden/language` actually having pending upstream work.

- With the scratch `spanish` clean and its `language` stand-in genuinely behind, `report`
  prints `PARENTS_BEHIND` naming `parents/language`, and separately notes if
  `parents/language/parents/deck` is also behind (nested, annotated, not actionable
  from here).
- `diff <spanish-path> parents/language` shows a real, correct before/after compiled
  diff for `rioplatense-anki.md` — verified on disk as spanish's entry file that
  transitively includes `language` via `language-defaults.md` — and leaves the real
  `parents/language` checkout completely untouched throughout (verify with `git status
  --short` immediately after `diff` returns: empty, not merely restored).
- **Faithfulness check:** before running any diff for real, compile the scratch tree's
  `rioplatense-anki.md` at the node's current (unswapped) pin and byte-compare it against
  compiling `node-dir`'s own `rioplatense-anki.md` directly. Identical bytes confirm the
  nested-worktree substrate is faithful; any difference means the scratch mechanism
  itself is wrong and every diff it produces afterward is untrustworthy.
- `apply <spanish-path> parents/language` — invoked directly, unwhitelisted, prompting
  for confirmation like any other Bash command — leaves `spanish`'s own repo with
  exactly one new commit bumping `parents/language`'s pointer, message naming old/new
  short SHAs, and nothing pushed.
- A dirty file planted anywhere in the scratch `spanish` or its `parents/language` makes
  `report` abort before issuing any `git fetch`.
- The force-pushed scratch remote yields `PARENTS_DIVERGED`, never `PARENTS_BEHIND`.
- Attempting `apply <spanish-path> parents/language/parents/deck` (a nested path) is
  rejected with a message pointing at the ownership ruling, not silently narrowed to the
  direct parent.

---

## Doors held open, nothing built

| Door | Trigger to build | What is pre-paid |
|---|---|---|
| A "bump everything behind" batch mode over `apply` | first grove with 3+ stale direct parents, when one-at-a-time gets tedious | `apply` already takes one parent per call; a loop over `report`'s findings costs nothing today |
| Auto-push after commit | user asks for it explicitly, in the moment | `security.md`'s existing narrow push exception already covers this; no new mechanism needed |
| Version-range resolution replacing pins | D4 is revisited (LOW reversibility — would need a real propagation-pain instance first) | out of scope by design; this flow is explicitly the runtime-UX alternative D4 chose instead |
| Cross-repo commit for nested (non-direct) drift, with real multi-owner instances | a second maintainer genuinely owns an intermediate parent and wants to delegate the bump | the ownership ruling above is deliberately conservative; nothing here forecloses a future "propose a PR against language" flow, it just isn't this one |

---

## Adjacent findings surfaced during this design (not in scope)

- **dafne still has no logging utils submodule** (raised in `requires_refusal.md`,
  carried forward here unchanged) — `tend_parents.py` is a worker with no log surface,
  same gap.
- **The stale `golden/` snapshot does not block this bullet.** `dafne_plan.md`'s
  dependency-graph note parks the golden refresh until integration tests start; this
  flow diffs live compiles against live upstream tips, never against `golden/`.
