# Phase 3.5 details — Manual edit audit (context.md → DAFNE.md sweep)

*Moved out of `dafne_plan.md` unedited, per the 2026-09-07 plan split — see that
file's Phase 3.5 for the condensed checklist and exit criteria. This file carries
the full account behind each checklist item.*

*Not a scripted execution phase like the others — a checkpoint. Between designing/
executing Phase 3's bullets, edits (the `context.md` → `DAFNE.md` rename among them)
were made by hand across master and several submodules, outside any checklist step.
This quasi-phase closes the loop before Phase 4 starts: confirm the manual work is
complete and consistent, then commit it everywhere. Added 2026-09-07; dirty state at
the time this was written:* `.claude/commands/pipe/add-cards-to-grove.md`,
`.claude/commands/pipe/tackle-feedback-on-grove.md`, `.claude/skills/onboard/SKILL.md`,
`CLAUDE.md`, `README.md`, `modes/world-adoption/shared/cvut/SP1/project.md`, this plan
file, and modified content in submodules `groves/english`, `groves/social-dynamics`,
`groves/spanish`, `plugins/anki-mcp`.

- **Recursive status check:** confirmed the dirty set was exactly as recorded above;
  `groves/instruments`, `plugins/dafne`, `plugins/mneme`, `.claude/utils` were all
  clean — nothing missed the top-level `m` marker.
- **Rename completeness:** repo-wide grep for `context.md` returned only legit
  survivors — mode-level `context.md` (`modes/meta/builder/context.md`,
  `architect/context.md`, `world-adoption/context.md`), mem-bank entry-point files
  (`reading-log/context.md`, `memory/context.md`), a pre-DAFNE debug hook
  (`.claude/hooks/debug/notify-context-read.py`, predates groves entirely — 2026-04-28),
  and historical mentions of the deleted `dafne_simulation/context.md`. No missed
  renames found.
- **Diff review per dirty repo:** all four submodule diffs were read in full.
  `groves/spanish` and `groves/social-dynamics`: each grove's old top-level
  `context.md` body was moved verbatim into `DAFNE.md` (content byte-matched against
  `git show HEAD:context.md`), then the redundant file deleted — a clean
  context.md→DAFNE.md *merge*, not just a rename. `plugins/anki-mcp/README.md`: the
  feedback-pipeline caption was de-named from `context.md` to generic "context
  file" rather than renamed to `DAFNE.md` — confirmed deliberate and correct, since
  the screenshot it captions (`assets/feedback-01-invoke.png`) shows a stale
  pre-Phase-1/2 state (`groves/languages/spanish/context.md`, the old
  `context-compiler` skill) that predates this migration; naming `DAFNE.md` there
  would trade one stale claim for another, and the screenshot's own staleness is a
  separate, out-of-scope issue. `groves/english/english.md`: a real anomaly —
  content unrelated to the rename (the Input Format code block and the Cloze Logic
  MULTI-CLOZE bullet) had been deleted by hand, left as a dangling empty heading.
  Surfaced to the user rather than assumed: confirmed intentional (the rigid
  `Text | Book Title | Chapter/Location` format was tedious for day-to-day pasting)
  and kept as-authored, committed separately (`4767dd8`) from the rename work.
- **Cross-check against this plan's own text:** grepped this file itself — the only
  `context.md` mentions left are historical (`dafne_simulation/context.md`,
  pre-deletion) and this phase's own text; nothing stale.
- **Commit sweep:** four submodules committed and pushed —
  `groves/english` (`4767dd8`, the Input Format/Cloze Logic edit, unrelated to the
  rename), `groves/spanish` (`90902d9`), `groves/social-dynamics` (`441b92e`,
  also fixes a stale `context.md` mention in `improvement-plan.md`), `plugins/anki-mcp`
  (`d905d87`). Master committed with the resulting pointer bumps plus its own direct
  edits.
