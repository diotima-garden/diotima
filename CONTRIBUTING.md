# Contributing to Diotima

First: thank you for even reading this. This is a spare-time project with a stable
vision and an honestly rough install — which is a strange and *good* place for a
contributor to arrive. The architecture is decided and documented; a lot of what's left
is the engineering that turns "works on my machine" into "works anywhere." If that kind
of work is your idea of fun, you've found a clean on-ramp.

## The unusual part: you don't work this repo by hand either

The same property that runs the product runs the development of it. The whole repo is
built to be *legible to a model reading it cold* — `CLAUDE.md` is the map, and the skills,
pipelines, and MCP tools are all self-describing. So the fastest way to orient yourself is
not to read every file; it's to **point an LLM (today, Claude Code) at the repo and ask it
where the thing you care about lives.** It will orient itself the same way it orients an
end user. Treat that as the primary onboarding tool, not a gimmick.

Read `CLAUDE.md` first — it's the navigation table for everything below.

## Getting it running

The setup is documented, honestly, in the README:

- [The moving parts](README.md#the-moving-parts-what-a-fresh-install-currently-touches) — what a fresh install touches.
- [Rough install path](README.md#rough-install-path-until-this-is-packaged) — the current hand-assembled steps.
- Then open the repo in Claude Code and type **`/onboard`** — it audits your machine
  against all of it, tells you plainly what works and what doesn't, and walks you to a
  first success. If `/onboard` fails for you, that's not you doing it wrong — that's a
  bug report, and a genuinely useful one. Open an issue with what it told you.

Fair warning, straight from the README: **this is a power-user setup, not a product yet.**
Expect some turbulence. The whole point of the backlog below is to end that.

## Where to start

The highest-value work is the seam between "works for me" and "works for anyone." The
three headline items live in the README —
[Where help is wanted](README.md#where-help-is-wanted-the-contributor-backlog):

1. **Cross-platform support** — the plugin/config directory layout is non-standard and has
   already bitten a Windows setup. Making paths OS-agnostic is the highest-value fix.
2. **Automated setup → one deliverable** — replace the manual venv-and-key dance with a
   reproducible bootstrap, and ultimately a single installable artifact.
3. **LLM-provider-agnostic core** — migrate the Claude-Code-shaped runtime toward
   [opencode](https://opencode.ai) as a portable base.

Those are big and shape the project — if one calls to you, **open an issue to say hi
before you dig in** so we can carve off a first slice together rather than you
disappearing into a three-week refactor.

Browse [all open issues](https://github.com/diotima-garden/diotima/issues) for the rest.
There's no formal "good first issue" label yet — ask in an issue and I'll point you at
something that fits your appetite.

## How work lands here

- **Fork, branch, PR.** Branch off `master`; keep each PR to one self-contained change.
  Small and focused beats big and sweeping — it's easier to review and easier for you to
  finish.
- **Respect the repo's own conventions.** A few project rules exist because the harness's
  permission system matches command strings literally — they're in `.claude/rules/`
  (e.g. project-root-relative paths, one command per bash block, pipelines preferred over
  raw skills). Skim them if your change touches skills, pipelines, or tooling.
- **Invariants belong in hooks or schemas, not prose.** If your change introduces an
  "always/never" rule about how a tool is used, encode it as a `PreToolUse` gate or a
  schema constraint rather than a sentence someone has to remember.
- **Verify by driving the real thing.** This system's whole thesis is a human-in-the-loop
  trust loop (backup → generate → diff → approve → log). If you change behavior, exercise
  the actual flow and say what you observed in the PR — not just that tests pass.
- **Commit messages:** describe the *why*, present tense, one logical change per commit.

## Licensing

The runtime is [Apache-2.0](LICENSE); contributions to it are accepted under that license,
no CLA. **Groves are different** — a grove is your content, not covered by the runtime's
license, and you choose how (or whether) to share it. See the README's
[licensing note](README.md#licensing-open-runtime-sovereign-groves).

## Say hi

Genuinely: if any of this looks interesting, open an issue just to introduce yourself and
what you're drawn to. The architecture is documented and I'm happy to orient you — the
scarce thing here is my time, not my willingness. Welcome aboard.
