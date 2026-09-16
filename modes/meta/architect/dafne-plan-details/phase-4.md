# Phase 4 details — Launch UX

*Moved out of `dafne_plan.md` unedited, per the 2026-09-07 plan split — see that
file's Phase 4 for the checklist, bullet definitions, and exit criteria. This file
carries the execution narrative for the one bullet that's done.*

## Bullet 1 — `bin/diotima`, the minimum launcher

→ **Executed 2026-09-07.** Grew one requirement beyond the bullet's original text,
forced by the cwd-exact-match finding recorded under Phase 3's manifest-injection
bullet (`dafne-plan-details/phase-3.md`): `bin/diotima` *does* now resolve whether
the invocation `cwd` is a grove (`cwd/DAFNE.md` exists, checked *before* any `cd`, no
ancestor-walking — matching `is_a_grove`), but **it does not launch the runtime there.**
It always launches with `cwd = master` regardless, since that's the only `cwd` Claude
Code will load master's `.claude/settings.json` from. What the cwd-is-a-grove check
controls instead is which single directory (that grove, or the garden) gets
`--add-dir`-ed and handed to the session via `$DIOTIMA_GARDEN` for the `SessionStart`
hook to read — see that bullet for the full mechanism and the reasoning for reusing the
`DIOTIMA_GARDEN` name. Net effect: this slice already **absorbs the next bullet's
cwd-detection half** under a corrected mechanism; only the picker and MRU remain
open below. The garden default (`~/Documents/diotima-garden`) is not hardcoded in
the script — it lives in `system/diotima/config.json`'s `default_garden` key, read
by both `bin/diotima` and the hook's own fallback, so there is exactly one place to
change it. Verified: cwd-independence (`pwd` before and after differ, confirmed via
a fake `claude` binary substituted on `PATH`), correct `--plugin-dir` enumeration
(`anki-mcp`, `dafne`; `mneme` correctly excluded, no `.claude-plugin`), and all three
`dir`-resolution branches (grove cwd; `$DIOTIMA_GARDEN` set; config-default
fallback, which also exercises "if dir not exist → create").
