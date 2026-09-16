# Phase 2 details — Production groves surgery

*Moved out of `dafne_plan.md` unedited, per the 2026-09-07 plan split — see that
file's Phase 2 for the checklist and target topology. This file carries only the
Exit narrative.*

**Exit:** every grove clones standalone and compiles byte-identical to golden with zero
edits; master's `groves/` holds only submodule mounts; context-compiler is gone.
**Phase 2 complete (2026-08-15).** Six repos pushed and mounted, not three — the plan's
target topology didn't cover `groves/social-dynamics/`; extracted anyway as a bare root
grove per an explicit scope decision when this phase began (see `grove_inheritance_decisions.md`).
Two smaller deviations from the plan's literal text, both decided the same way:
`queue-policy.md` (not in the plan's file table at all) landed in `language` alongside
`language-defaults.md`; `groves/managed-models.json` stayed in `groves/` rather than
moving to the anki-mcp side — deferred, not forgotten, since it touches a second repo
(`plugins/anki-mcp`) this session left alone. `spanish`/`english`/`instruments` verified
byte-identical to `golden/*.golden.md` three ways: from the master-mounted submodules,
from a genuinely standalone `git clone --recursive`, and (for spanish) from the sandbox
before it was deleted. `groves/mem-bank-subscriptions.json`'s `spanish-reading` bank path
was updated to the new mount point as a courtesy — the live subscription source of truth
stays this file, not any grove's `DAFNE.md`, until Phase 3 runs.
