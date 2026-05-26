# Leak 1 — Inefficient Cloze: Resolution

**Date:** 2026-05-26

## Decision

The user's original design intent was valid: cloze as a scaffolded stepping stone toward full production. The flaw is in Anki's SRS mechanics — paired cards schedule independently, so cloze drifts to long intervals (2650 factor, 335d) while production stays hard (1300 factor, 25d). The scaffold isn't there when needed.

**Adopted approach:** two changes working together as one design shift.

---

## Option 1 — Cloze justified only when it tests distinct knowledge

Cloze is kept only when it isolates something the production card does not force:
- Irregular conjugations, pronoun placement/attachment
- Prepositions (*por/para*, *a/en*), tense contrasts
- Dialect-sensitive forms (*vos* inflection, Argentine vocabulary)
- Contractions (*al*, *del*), superlatives, stem changes

Redundant production+cloze pairs (same word, same recall) are eliminated going forward. Retroactive cleanup of existing ~100 pairs is a separate pass (not done here).

---

## Option 2 — Hint field as scaffold alternative

A `Hint` field was added to the Anki `Basic` note type (index 2). The front template was updated to show it as a collapsible `<details>` element — renders nothing when empty, so all existing cards are unaffected.

Template change:
```
{{Front}}
{{#Hint}}<details><summary>hint</summary>{{Hint}}</details>{{/Hint}}
```

Usage: populate Hint with the key word or irregular form on production cards where cold recall is genuinely hard. Leave blank otherwise.

---

## `Production` Note Type Migration

Decision: move the `Hint` field off `Basic` (shared system type, pollutes English/Instruments editors) and onto a dedicated `Production` note type.

**`Production` note type created** with fields `[Front, Back, Hint]` and front template:
```
{{Front}}
{{#Hint}}<details><summary>hint</summary>{{Hint}}</details>{{/Hint}}
```

**230 Spanish production notes identified** for migration (`deck:Español tag:cardtype::production note:Basic`).

**AnkiConnect `changeNoteType` action not available** in the installed version. Discovered instead that `updateNoteModel` exists in the add-on and changes note type in-place, preserving card IDs and scheduling data. Dummy note test confirmed it works correctly.

**Migration ready** — sandbox testing complete (see below). Next step: bulk migration of 230 notes from `Basic` → `Production` via `update_note_model`, then remove `Hint` field and revert template on `Basic`.

---

## Sandbox Test Log & Unit Test Spec

Validates that `add_model_field`, `remove_model_field`, and `update_note_model` are safe to run on notes with existing data.

### Setup

- Created note type `TestSandbox` with fields `[Front, Back]`
- Created note type `TestSandbox2` with fields `[Front, Back, Extra]`
- Added dummy note to `TestSandbox`:
  - `Front = "TAG_TEST_FRONT"`, `Back = "TAG_TEST_BACK"`
  - tags: `["test::tag_preservation", "test::sandbox"]`

### Test sequence and assertions

| # | Action | Expected | Observed |
|---|---|---|---|
| 1 | `add_model_field(TestSandbox, "Extra")` | Returns null, no error | ✓ |
| 2 | `notes_info(note_id)` after add | Front/Back values unchanged; `Extra` field present and empty | ✓ |
| 3 | `remove_model_field(TestSandbox, "Extra")` | Returns null, no error | ✓ |
| 4 | `notes_info(note_id)` after remove | Front/Back values unchanged; `Extra` field absent | ✓ |
| 5 | `update_note_model(note_id, "TestSandbox2", {Front, Back, Extra=""})` — tags omitted | Returns null, no error | ✓ |
| 6 | `notes_info(note_id)` after model change | `modelName == "TestSandbox2"`; Front/Back values unchanged; Extra empty; **tags preserved** (`["test::sandbox","test::tag_preservation"]`); card ID unchanged | ✓ |

### Bug found and fixed during testing

**Symptom:** When `tags` is not passed to `update_note_model`, AnkiConnect's `updateNoteModel` internally defaults to `note.get('tags', [])` — silently clearing all tags.

**Fix in `notes.py`:** When `tags=None`, auto-fetch current tags via `notesInfo` before calling `updateNoteModel`, then include them in the payload.

```python
if tags is None:
    info = _call("notesInfo", notes=[note_id])
    tags = info[0]["tags"] if info else []
note = {"id": note_id, "modelName": model_name, "fields": fields, "tags": tags}
```

**Verification:** Re-ran step 5–6 after fix and restart. Tags preserved correctly.

### Invariants for unit tests

- `add_model_field` on a model with existing notes must not alter any existing field values
- `remove_model_field` on a model with existing notes must not alter remaining field values
- `update_note_model` must preserve: field values (for fields present in both models), card IDs, scheduling data, and tags (when `tags` param is omitted)
- `update_note_model` must blank fields present in the new model but absent from the call's `fields` dict
- AnkiConnect `updateNoteModel` always requires `tags` to be explicitly in the payload — absence is not the same as "preserve"

---

## MCP Additions (`.claude/anki-mcp/tools/`)

| Tool | File | What |
|---|---|---|
| `add_model_field(model_name, field_name, index?)` | `models.py` | Add a field to an existing note type |
| `remove_model_field(model_name, field_name)` | `models.py` | Remove a field from an existing note type |
| `change_note_type(note_ids, old_model, new_model, ...)` | `models.py` | Bulk note type change with auto field mapping (wraps `changeNoteType` — verify availability) |
| `update_note_model(note_id, model_name, fields, tags?)` | `notes.py` | Change a single note's type in-place via `updateNoteModel`; preserves scheduling |

---

## Files Modified

| File | Change |
|---|---|
| `decks/languages/cloze-deletion.md` | Added "When NOT to Generate a Cloze" section — generic, applies to all language decks |
| `decks/languages/spanish/rioplatense-anki.md` | Updated Cloze triggers with "distinct knowledge" constraint; added Hint field to Production card type |
| `.claude/anki-mcp/tools/models.py` | Added `add_model_field`, `remove_model_field`, `change_note_type` |
| `.claude/anki-mcp/tools/notes.py` | Added `update_note_model` |
| `.claude/anki-mcp/README.md` | Documented all new tools in Models and Note mutations tables |
| Anki `Basic` note type | Added `Hint` field; updated front template (temporary — to be reverted after migration) |
| Anki `Production` note type | Created; awaiting note migration |
