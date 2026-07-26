# Packaging: making Diotima trivially runnable

*Architect analysis + implementation-ready menu. What it would take to close the gap
between "has Claude Code + Anki" and "the system works," and enough detail under each
strategy to pick one up and build it. Analysis, not yet a committed execution plan.*

**Decisions already taken** (see *Decisions recorded* at the end):
- **No Claude Code plugin.** Considered and rejected — kept below only as a recorded no.
- **Container trial/CI image is in scope** as an opt-in addition, toggled so it never
  disturbs a running desktop Anki.

---

## Scoping the problem honestly

The situation fixes two constraints that bound everything:

- The user drives the system **through Claude Code** (the front end is the chat).
- **Anki desktop is running**, logged in, with the **AnkiConnect** localhost server up.

So the two heavy external pieces — the harness and the Anki bridge — are *given*.
"Trivially runnable" therefore has a small, bounded meaning: close the gap between
*has-Claude-Code-and-Anki* and *system-works*. That gap is exactly the README's
"moving parts" list **minus the externals**:

1. **Two git submodules** — `plugins/anki-mcp`, `.claude/utils` (HTTPS, anonymous-clonable).
2. **Python venvs** — currently three (`anki-mcp`, `context-compiler`, `gemini`).
3. **Undocumented dependencies** — deps live in prose in READMEs, no manifest anywhere.
4. **`.mcp.json` path wiring** — hardcodes `plugins/anki-mcp/.venv/bin/python3`, a POSIX
   venv path that breaks on Windows (`Scripts\python.exe`) and on any relocation.

That is the entire surface. It is small and well-bounded — the honest answer is *not*
"rebuild for distribution."

## The finding that collapses the problem

Grepping every Python component's top-level imports, the **only third-party dependencies
in the whole codebase** are:

| Dependency | Component | Status |
|---|---|---|
| `mcp` | `plugins/anki-mcp` | **mandatory** (the Anki bridge) |
| `google-genai` | `.claude/gemini` | **optional** (YouTube extraction only) |

`context-compiler`, `mem-bank`, `.claude/utils`, and `system/` scripts are **stdlib-only**
— `argparse`, `json`, `pathlib`, `re`, `subprocess`, `urllib`, etc. Their venvs install
*nothing*. Two of the three venvs are pure ceremony; `context-compiler` and any stdlib
script can run on the system `python3`.

**Consequence:** the real install has *one* mandatory third-party package. Every strategy
below simplifies once this is internalized — the "several virtualenvs" framing overstates
the actual work.

## Primer: what `uv` / `uvx` are (load-bearing below)

`uv` is a single-binary Python package + environment manager (Rust, by Astral — the `ruff`
authors). It installs as one static executable and needs no pre-existing Python:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh          # macOS / Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

`uvx` (bundled with `uv`) is its **tool runner** — the equivalent of `pipx`. It runs a
Python CLI inside an **ephemeral, cached, auto-managed environment**, with no manual venv
and no `pip install` step. Crucially it can run a tool **straight from a git repo**:

```bash
uvx --from git+https://github.com/diotima-garden/anki-mcp anki-mcp --help
```

Why this matters here: `uvx` erases moving-parts #2 (venvs) and #4 (the OS-specific
`.venv/bin` vs `Scripts\` path) in one move — the launch command becomes just `uvx`, which
resolves identically on every OS. This is the mechanism behind Strategies A and B.

## Two axes that rank any strategy

1. **Does it fix the cross-platform `.mcp.json` path?** (the README's own
   "highest-value fix", contributor-backlog #1)
2. **Does it respect the thin-`.claude` / opencode direction?** (`product-vision.md`:
   `.claude/` holds only Claude-specific glue; the portable core — MCP server, bare
   `SKILL.md` files — lives outside a vendor wrapper. See `cross-tool-portability.md`.)

## The packaging unit: runtime, not groves

Per `product-vision.md`, the **runtime is the MP3 player, groves are the music** — and
DAFNE is actively extracting groves into their *own repositories*. So packaging targets
the **runtime**: harness glue + the `anki-mcp` server + skills. **Grove adoption stays a
separate, already-trivial step** (clone / fork-and-refocus, soon a DAFNE submodule pin).
Do not bake today's `groves/` into any installable, or the package fights the extraction
already underway.

---

## Strategies

Each carries: *what the user installs & the felt experience* · *what we build (impl
surface)* · *effort / risk* · *axes*.

### Step 0 — pin the dependency set *(prerequisite for A and B)*

Make deps declarative instead of prose.

- **User UX:** none — internal.
- **Impl surface:**
  - `plugins/anki-mcp/pyproject.toml` declaring `mcp` **and a console entry point**
    (`[project.scripts] anki-mcp = "server:main"`). This requires wrapping `server.py`'s
    top-level run code in a `main()` function — the same entry point B and console use.
  - `.claude/gemini/requirements.txt` → `google-genai`, documented as an optional extra.
  - Retire the phantom `context-compiler` venv: repoint its invocations at system
    `python3`. Touch points to update — `.mcp.json` is unaffected (context-compiler isn't
    an MCP server), but the `.venv/bin/python3` references in `.claude/settings.json`
    allow-rules (lines ~64–66) and the `compile*` skills must change to bare `python3`,
    and `/onboard` + `python-venvs.md` docs drop the context-compiler venv step.
- **Effort:** low. **Risk:** low. Floor under everything.

### Strategy A — `uv` bootstrap script *(immediate, honest step)*

**User installs:** git + `uv`. The script does the rest.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/diotima-garden/diotima
cd diotima
./setup.sh
```
```
✓ submodules initialized
✓ anki-mcp env ready (mcp)
✓ .mcp.json written for linux
✓ AnkiConnect responding on :8765
→ Restart Claude Code, then say "add a card to spanish"
```
Felt experience: **clone + one command + restart**, ~2 min.

- **Impl surface:** `setup.sh` + `setup.ps1` that (1) `git submodule update --init
  --recursive`, (2) ensures `uv` (or bootstraps it), (3) `uv venv` + `uv pip install mcp`
  for anki-mcp, (4) generates `.mcp.json` from a template with the interpreter path
  resolved for the host OS, (5) probes AnkiConnect and prints a verdict. This automates
  the **repair half** that `/onboard` deliberately refuses to do (`/onboard` stays the
  audit/diagnosis half; keep them complementary).
- **Effort:** low. **Axis 1:** partial — generator emits the right per-OS path, but a
  checked-in `.mcp.json` is still POSIX-shaped. **Axis 2:** neutral.

### Strategy B — `uvx`-package `anki-mcp` *(the leverage move; recommended core)*

The shift: **no venv, no server submodule for consumers, no OS-specific path.** `.mcp.json`
ships as:
```jsonc
{ "mcpServers": { "anki": {
    "command": "uvx",
    "args": ["--from", "git+https://github.com/diotima-garden/anki-mcp@v1.0",
             "anki-mcp", "--managed-config", "groves/managed-models.json"] } } }
```
**User installs:** git + `uv`. That's the whole list.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/diotima-garden/diotima
cd diotima
# restart Claude Code — uvx fetches & caches anki-mcp on first launch
```
Felt experience: **clone + restart.** No pip, no venv, no server submodule, cross-platform
for free (first launch a few seconds slower while `uvx` resolves once). The `git clone` of
the main repo remains — that is where **groves, skills, and hooks** live.

- **Impl surface:** the Step-0 `pyproject.toml` + `main()` entry point; pin a **tag/ref**
  in `--from …@v1.0` for reproducibility; switch `.mcp.json` to the `uvx` form. `anki-mcp`
  stays a submodule only for *local development* of the server itself. (Optionally publish
  to PyPI later so `--from` can drop the `git+` URL; `git+` works with no publish.)
- **Effort:** medium. **Axis 1:** **yes** — the highest-value fix, for free. **Axis 2:**
  **yes** — MCP-as-standalone is exactly what `cross-tool-portability.md` blesses; both
  Claude Code and opencode point their own config at the same `uvx` command.

### Strategy E — containerized Anki, as a trial / CI image *(opt-in addition)*

Headless desktop Anki + AnkiConnect in a container is **off-the-shelf**:
[`ankimcp/headless-anki`](https://github.com/ankimcp/headless-anki) publishes prebuilt
images running real Anki under `QT_QPA_PLATFORM=offscreen` / Xvfb+VNC, with **AnkiConnect
(add-on `2055492159`) preinstalled and auto-patched to bind `0.0.0.0`**, exposing `8765`
(AnkiConnect), `5900` (VNC), `3141` (their own MCP). It boots against a **local profile**
— no AnkiWeb login. Our `anki-mcp` talks to it **unchanged** (same AnkiConnect surface).

There is no true card-driving "Anki CLI" — Anki is the Qt GUI over a Rust backend,
AnkiConnect is a GUI add-on, so "headless" = that GUI under a virtual display. The one
genuine CLI subcommand is the built-in **sync server** (`SYNC_USER1=user:pass anki
--syncserver`).

**User installs:** Docker + git. **No Anki, no AnkiWeb account.**
```yaml
# docker-compose.yml  — opt-in via a compose profile so it NEVER runs by default
services:
  anki:
    profiles: ["trial"]                 # only starts with `--profile trial`
    image: ghcr.io/ankimcp/headless-anki:x11-vnc-addons-v1.4.0
    ports: ["8765:8765", "5900:5900"]   # AnkiConnect + VNC
    volumes: ["./anki-data:/data"]      # throwaway collection
```
```bash
docker compose --profile trial up -d    # explicit; nothing starts otherwise
# Claude Code on the host works normally — anki-mcp hits :8765 in the container
# watch cards render: point a VNC viewer at localhost:5900
```

**The toggle — and how it stays out of a real Anki's way.** Host port `8765` can be bound
by only one process, so the three modes are:
- **Default (daily driver):** container **not started** (it's behind the `trial` profile).
  Desktop Anki owns `8765`. Normal use untouched. ✅ This is the "doesn't break normal
  Anki" guarantee — it's opt-in by construction, not by luck.
- **Trial (no desktop Anki):** start the container; it owns `8765`; `anki-mcp` hits
  `localhost:8765` unchanged.
- **Coexist (both at once — e.g. CI while you also use desktop Anki):** remap the
  container to host `8766` and point *that* `anki-mcp` instance at it. **This needs one
  small change to `anki-mcp`:** `ANKI_CONNECT_URL` is currently **hardcoded** in
  `plugins/anki-mcp/core.py:16` and `launcher.py:19` — make it read an
  `ANKI_CONNECT_URL` env var (default `http://localhost:8765`). Also gate
  `launcher.ensure_anki_running` to a no-op when targeting a container (nothing to launch
  on the host).

**How the user sees / interacts with the containerized Anki.** Two surfaces:
- **The chat (primary, GUI-free).** Everything goes through AnkiConnect, so Claude
  reports and renders results in the chat — cards added, old→new edit diffs, deck synced.
  Identical to the host case. For *confirming* changes, no GUI is involved.
- **The Anki GUI over VNC / noVNC.** The container runs the **full real Anki desktop**;
  reach it via a VNC viewer (`localhost:5900`) or a **browser tab** (noVNC add-on,
  ~`localhost:6080`). Needed for the two activities that require the UI: **reviewing**
  cards (spaced repetition) and **writing feedback** onto a card (the reverse loop). It's
  a remote-desktop experience — fine to evaluate, clunky for daily, and with **no mobile
  story** unless the container syncs to the user's own AnkiWeb (the parked two-writer
  hazard). This is the structural reason E stays trial/CI, not daily driver. In CI nobody
  watches — assert via AnkiConnect, optionally capture a VNC screenshot as a build
  artifact.

- **Impl surface:** `docker-compose.yml` with the `trial` profile; the `ANKI_CONNECT_URL`
  env override in `anki-mcp` (also generally useful); optionally publish the noVNC port
  for browser access; a CI workflow that `compose --profile trial up`, seeds a throwaway
  grove, and runs the pipeline end-to-end.
- **Where it wins:** zero-install *trial* (someone with no Anki tries Diotima) and
  *CI/integration testing* against a disposable collection. **Where it doesn't:** the
  daily driver — an empty collection has none of the real review history that feeds
  generation, and the user already runs desktop Anki.
- **Effort:** low to adopt for trial/CI. **Axis 1:** N/A (different concern). **Axis 2:**
  neutral-positive (a deployment target; both harnesses still point at `:8765`).
- **The AnkiDroid note (inspiration, not a task):** AnkiDroid never uses AnkiConnect — it
  speaks Anki's **HTTP sync protocol** to AnkiWeb or a self-hosted sync server. The
  reusable principle: *a collection is portable over sync, independent of the client
  driving it.* A future "no desktop Anki on host, drive the real collection" path would
  have the container `SYNC_USER` into the user's AnkiWeb, then expose AnkiConnect. ⚠️
  **Hazard:** two clients writing one collection concurrently forces one-way sync /
  conflict resolution — the silent-data-loss class this project is built to fear
  (`structural-lessons.md`). Single-writer discipline only; out of scope for now.

### Rejected — Claude Code plugin *(decision recorded)*

A Claude Code plugin (`/plugin install`) could ship skills + hooks + the `.mcp.json`
pointer as one in-harness install. **Rejected**, because: (1) `cross-tool-portability.md`
establishes that plugin-wrapping is exactly what **breaks opencode sharing** — opencode
can't see plugin-bundled skills or load Claude plugins at all, undoing a stated invariant;
(2) it would still not contain the **groves**, so it doesn't remove the separate
adoption step; (3) over `uvx` (B) it adds little for the daily driver. Kept here only so a
future reader sees it was weighed, not missed.

---

## Setup UX comparison (at a glance)

| Path | User installs | Manual venv? | Anki needed? | Cross-platform | Felt effort |
|---|---|---|---|---|---|
| **Baseline (today)** | git, python, mcp | 3 (by hand) | yes | ✗ (Windows breaks) | 10–15 min |
| **A** bootstrap | git, **uv** | script-managed | yes | ✓ (generated path) | clone + 1 cmd |
| **B** uvx | git, **uv** | **none** | yes | ✓ (free) | clone + restart |
| **E** container | **Docker**, git | none | **no** | ✓ | `compose --profile trial up` |

Through-line: **`uv` erases the venv/path pain** for the daily driver (A/B); **Docker
erases the Anki-install pain** for trials (E). Nothing else beyond the two givens.

## Recommended path

**Daily driver:** `0 → A → B`.
1. **Step 0 — pin deps** (`pyproject.toml` + `main()` entry; drop the phantom
   context-compiler venv). The floor under everything.
2. **Strategy A — `uv` bootstrap.** Immediate honest win: 7-step dance → one command,
   automating the repair half `/onboard` refuses.
3. **Strategy B — `uvx`-package `anki-mcp`.** The leverage move: kills the submodule, the
   venv, and the cross-platform path in one change; aligned with the opencode direction.

**Parallel track (opt-in):** **Strategy E** — adopt `ankimcp/headless-anki` behind a
compose `trial` profile plus the `ANKI_CONNECT_URL` env override, for zero-install trials
and end-to-end CI. Independent of 0→A→B; it changes the deployment target, not the
runtime's packaging.

## Decisions recorded

- **Claude plugin: no.** Breaks opencode sharing, omits groves, marginal over B.
- **Container trial/CI: yes, opt-in.** Behind a compose profile so it never disturbs a
  running desktop Anki; coexistence needs the `ANKI_CONNECT_URL` env override in anki-mcp.
- **uv/uvx: the chosen mechanism** for erasing the venv + cross-platform-path friction.

## Open (shapes sequencing, not direction)

- Publish `anki-mcp` to PyPI (drops the `git+` URL) — future-additive, not required for B.
- The sync-protocol "drive the real collection from a container" path — parked behind the
  single-writer hazard above until there's a reason to build it.
