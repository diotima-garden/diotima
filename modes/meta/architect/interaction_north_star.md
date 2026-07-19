# Interaction North Star — how a user meets Diotima

*Status: settled 2026-07-18 (user ruling). Companion to
`major_architectural_decision_to_be_made.md` — D0 fixes the primitive (grove-rooted,
runtime ambient); this record fixes the front door built on top of it.*

The main Diotima repository carries no groves. Groves are separate repositories living in
user space. The question settled here: **what does launching feel like, and where do
grove working-copies live on disk?**

All scenarios below preserve D0's primitive — `cd` into a grove and launch always works;
discovery flows runtime → grove; a grove never registers itself. They differ only in the
sugar layer.

---

## The three candidate scenarios

### A — The Garden Directory

*Precedent: old Go's `~/go/src`, Obsidian vaults.*

Installation creates `~/diotima-garden/` — a visible, user-facing dir (groves are
authored content, closer to `~/Documents` than to cache) — and drops a `diotima` command
on PATH. Discovery is pure `readdir`: every subdirectory carrying `DAFNE.md` is a grove,
which is exactly the identity-marker job the manifest already holds. Session start:
*"Your garden has spanish and english. Enter one, or plant a new one?"* Entering reroots
the session into the grove (grove = cwd, D0 preserved). Adopting a stranger's grove =
`git clone` into the garden.

- **Strength:** the "you have X and Y" moment is trivial and robust; zero state beyond
  the filesystem; one place the user's stuff lives; backup = copy one folder.
- **Weakness:** dictates where repos live. Go *abandoned* the forced workspace layout
  under exactly this pressure — real precedent against, not aesthetics.
- **Discriminating test:** clone a stranger's grove into `~/projects/spanish` — invisible
  to the launcher until moved. That is A's whole cost.

### B — The Git Model

*Precedent: git itself; VS Code recent workspaces; `zoxide`.*

No blessed directory. A grove is a repo anywhere. `cd` in, run `diotima` — the runtime
sees `DAFNE.md` in cwd and plays the grove. The picker moment comes from a
**runtime-side MRU history**: each launch appends the grove's path to a user-level
recents file (`~/.local/state/diotima/recent`). Running `diotima` outside any grove
shows: *"Recently tended: spanish (yesterday), english (last week). Enter one, or create
a new grove here?"*

This is not `subscriptions.json` reborn: the grove never registers itself; the runtime
records only paths it has already been launched from; losing the file loses convenience,
nothing else. **History, not configuration** — the distinction that keeps it on the
right side of D1's Test 1.

- **Strength:** maximally consistent with D0; a stranger's grove works the instant it is
  cloned, anywhere; zero installer opinions.
- **Weakness:** first run is empty — no garden to show, so onboarding must lead with
  "create," and a grove never opened never appears. The invariant this strains is *user
  mode is the product*.

### C — The Managed Library

*Precedent: `pipx` / `brew` / Steam library.*

The runtime owns a store (`~/.local/share/diotima/groves/`) and the front door is verbs:
`diotima install <url>`, `diotima list`, `diotima open <name>`, `diotima create <name>`.
Bare `diotima` becomes a **conversational garden session** — an AI session above any
grove that lists groves, answers cross-grove queries, and drives the create /
fork-and-refocus wizard before rerooting into a grove.

- **Strength:** the only scenario where **distribution (D5) and launch UX are the same
  surface** — `install` is the marketplace verb, and fork-and-refocus gets a guided
  conversation instead of manual git surgery. Best story for the non-developer user the
  vision ultimately serves.
- **Weakness:** heaviest machinery; closest to orchestrator-rooted, the shape D0 warned
  inverts "open content, not tool"; and it front-runs D5, which is deferred until one
  grove has actually been published. Building C today designs the marketplace from zero
  published instances.

---

## How they differ on the tests that matter

| | A: Garden dir | B: Git model | C: Managed library |
|---|---|---|---|
| Stranger's grove cloned to `~/projects` | invisible until moved | works immediately | must be `install`ed |
| "You have spanish & english" moment | readdir, always right | MRU, right after first open | store list, always right |
| State beyond filesystem | none | recents file (disposable) | store + metadata |
| First-run (empty) experience | "plant your first grove" | blank recents | guided install/create |
| D5 marketplace fit | neutral | neutral | *is* the marketplace surface |
| Risk | dictates repo location (Go's mistake) | weak discoverability | front-runs D5, orchestrator pull |

---

## Ruling: these are stages, not alternatives

**B now, A's default-dir as sugar, C deferred with the door open.**

- **B is the primitive** and costs nearly nothing — it is D0 plus a recents file.
- **A becomes a default, not a requirement:** `diotima create` places new groves in
  `~/diotima-garden` unless told otherwise, and the launcher shows *garden-dir groves ∪
  recents*. A's discoverability without Go's mistake.
- **C waits for its first published grove**, exactly as the record's zero-instance rule
  demands. Nothing in A/B forecloses it: the store would be just another directory the
  launcher unions into its list, and the verbs layer on top of the same primitive.

The launcher's grove list is therefore a **union of dumb, disposable sources** — readdir
of a default dir, an MRU file, later a store. No daemon, no registry, no grove-side
registration, ever.

---

## The GUI note — same primitives, thinner shell

The staged design above is GUI-ready for free, because every discovery mechanism is
inert data a GUI can read without any new protocol:

- **The grove list is enumerable by anything.** Garden-dir readdir + recents file +
  (later) store are plain filesystem and a flat text file. A GUI grove picker is a file
  browser filtered on `DAFNE.md` presence — the manifest's identity-marker job pays off
  a second time. No daemon to talk to, no IPC to design.
- **"Enter a grove" is already a clean seam.** The launcher's only real action is *reroot
  a session into a directory*. A GUI does the identical thing: pick grove → spawn the
  runtime with cwd set. The GUI never needs to understand groves internally — it stays
  on the runtime side of the sovereignty line, reading manifests only.
- **C's conversational garden session is a chat surface.** When C arrives, the garden
  session is what a GUI wraps: the simplest viable GUI is a grove list in a sidebar plus
  a chat pane, which is precisely the shape of existing agent GUIs. The
  fork-and-refocus wizard is conversation, not forms — no bespoke UI logic.
- **Read-only observability comes free from the same discipline.** Because grove state is
  human-readable text (mem-bank, manifests), a GUI dashboard ("what did I tend this
  week?") is a renderer over files, not a query API. The runtime's efficiency contract —
  engine reads structure, never content — holds for the GUI too.

The constraint this imposes on today's work is only this: **keep every discovery source
a dumb file or directory.** The moment discovery hides behind a process or a socket, the
simple-GUI option is gone.
