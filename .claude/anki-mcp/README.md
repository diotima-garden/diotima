# Anki MCP Subsystem

Self-contained MCP server that exposes Anki operations as native Claude tools.
Claude calls tools directly instead of constructing JSON strings and invoking bash.


---

## Package layout

```
.claude/anki-mcp/
├── server.py       Entry point — sets sys.path, imports core + tools, runs mcp
├── launcher.py     Anki process lifecycle (ensure_anki_running)
├── core.py         Shared state: mcp instance, _call(), FLAGS, _log
└── tools/
    ├── __init__.py     Imports all submodules → triggers @mcp.tool() registration
    ├── cards.py        Card search, metadata, flag ops
    ├── notes.py        Note create/update/delete
    ├── tags.py         Tag operations (note-level)
    ├── decks.py        Deck management + sync
    ├── scheduling.py   Suspend, forget, relearn, answer, intervals
    ├── models.py       Note type introspection
    ├── media.py        Media store/retrieve/delete
    ├── stats.py        Review history and collection stats
    ├── aggregate.py    Higher-level aggregation (get_all_notes, get_flagged_notes)
    └── analytics.py    Computed metrics (vocabulary_snapshot, learning_velocity)
```

**Adding a tool:** add a `@mcp.tool()` function to the appropriate `tools/*.py` file.
Import `mcp` and `_call` from `core`. Restart Claude Code after any server change.

---

## Tools

### Search

| Tool | What |
|---|---|
| `find_cards(query)` | Search cards by raw Anki query. Returns card IDs. |
| `find_flagged_cards(flag, deck?)` | Find cards by flag name, optionally scoped to a deck. |
| `find_notes(query)` | Search notes by raw Anki query. Returns note IDs. |

### Card & note metadata

| Tool | What |
|---|---|
| `cards_info(card_ids)` | Full metadata per card — fields, tags, flags, scheduling. |
| `notes_info(note_ids)` | Full metadata per note — fields, tags, card IDs. |
| `cards_to_notes(card_ids)` | Convert card IDs → note IDs. |

### Note mutations

| Tool | What |
|---|---|
| `add_notes(notes)` | Add notes. Each: `{deckName, modelName, fields, tags}`. |
| `can_add_notes(notes)` | Duplicate check before adding. |
| `update_note_fields(note_id, fields)` | Update specific fields in-place. |
| `update_note(note_id, fields?, tags?)` | Atomically update fields and/or tags. |
| `update_note_model(note_id, model_name, fields, tags?)` | Change a note's type in-place. Preserves card IDs and scheduling. All fields must be supplied — omitted fields are blanked. |
| `delete_notes(note_ids)` | Permanently delete notes and all their cards. |
| `remove_empty_notes()` | Remove notes with no cards. |

### Tags

| Tool | What |
|---|---|
| `get_tags()` | All tags in the collection. |
| `add_tags(note_ids, tags)` | Add space-separated tags (preserves existing). |
| `remove_tags(note_ids, tags)` | Remove space-separated tags. |
| `update_note_tags(note_id, tags)` | Replace all tags on a note. |
| `clear_unused_tags()` | Remove tags unused by any note. |
| `replace_tags_in_all_notes(old, new)` | Rename a tag collection-wide. |

### Flags

| Tool | What |
|---|---|
| `set_card_flag(card_id, flag)` | Set flag by name: none/red/orange/green/blue/pink/turquoise/purple. |

### Decks

| Tool | What |
|---|---|
| `deck_names()` | All deck names. |
| `deck_stats(decks)` | New/learn/review/total counts per deck. |
| `get_decks(card_ids)` | Map deck name → card IDs for given cards. |
| `create_deck(deck)` | Create a deck. Returns deck ID. |
| `get_deck_config(deck)` | Deck configuration object. |
| `save_deck_config(config)` | Save a configuration object. |
| `change_deck(card_ids, deck)` | Move cards to another deck. |
| `delete_decks(decks, cards_too?)` | Delete decks (optionally with cards). |
| `export_deck(deck, path, include_sched?)` | Export to .apkg. |
| `import_package(path)` | Import an .apkg file. |
| `sync()` | Trigger AnkiWeb sync (background). |

### Scheduling

| Tool | What |
|---|---|
| `are_suspended(card_ids)` | Suspension state per card. |
| `are_due(card_ids)` | Due state per card. |
| `get_intervals(card_ids, complete?)` | Current intervals (days). |
| `suspend_cards(card_ids)` | Exclude cards from review. |
| `unsuspend_cards(card_ids)` | Restore to review queue. |
| `forget_cards(card_ids)` | Reset to new. |
| `relearn_cards(card_ids)` | Move to learning queue. |
| `answer_cards(answers)` | Simulate review answers `[{cardId, ease}]`. |

### Resources

Read-only data served alongside tools. Access via `ListMcpResourcesTool` (catalog) and `ReadMcpResourceTool` (content).

| URI | What |
|---|---|
| `anki://template-reference` | Anki card template syntax and CSS conventions — read before calling `update_model_templates` or `update_model_styling`. |

### Models

| Tool | What |
|---|---|
| `model_names()` | All note type names. |
| `model_field_names(model_name)` | Field names in definition order. |
| `model_templates(model_name)` | Card template HTML. |
| `model_styling(model_name)` | Note type CSS. |
| `rename_model_field(model_name, old, new)` | Rename a field in an existing note type. |
| `add_model_field(model_name, field_name, index?)` | Add a field to an existing note type. `index` sets insertion position; omit to append. |
| `remove_model_field(model_name, field_name)` | Remove a field from an existing note type. Field data is permanently lost. |
| `change_note_type(note_ids, old_model, new_model, field_mapping?, template_mapping?)` | Change the note type of a list of notes. `field_mapping`/`template_mapping` are `{old_name: new_name}`; omit to auto-map by matching names. |
| `update_model_templates(model_name, templates)` | Update card template HTML for an existing note type. `templates` format: `{"Card 1": {"Front": "...", "Back": "..."}}`. |
| `update_model_styling(model_name, css)` | Replace the CSS stylesheet for an existing note type. |
| `create_model(model_name, fields, is_cloze?)` | Create a new note type with default templates. `is_cloze=True` sets cloze template and flag. |

### Media

| Tool | What |
|---|---|
| `store_media_file(filename, data?, path?, url?)` | Store a file in Anki's media dir. `url` lets AnkiConnect download directly from a public URL. |
| `retrieve_media_file(filename)` | Retrieve a file as base64. |
| `get_media_files_names(pattern?)` | List media files by glob. |
| `get_media_dir_path()` | Absolute path to media directory. |
| `delete_media_file(filename)` | Delete a media file. |

### Statistics

| Tool | What |
|---|---|
| `get_collection_stats()` | Collection-wide stats as HTML. |
| `card_reviews(deck, start_id?)` | Raw review log entries. |
| `get_reviews_of_cards(card_ids)` | Full review history per card. |
| `get_latest_review_id(deck)` | ID of most recent review (for incremental fetches). |

### Aggregation

Higher-level tools that collapse multi-step roundtrips and return clean, merged objects.

| Tool | What |
|---|---|
| `get_all_notes(deck, include_scheduling?)` | All notes in a deck, fields flattened. Foundation for bulk AI operations. |
| `get_flagged_notes(deck, flag)` | Flagged notes merged and ready for editing — card_id + flattened fields in one call. |

### Analytics

Computed metrics derived from raw AnkiConnect data.

| Tool | What |
|---|---|
| `vocabulary_snapshot(deck)` | Maturity breakdown + weighted vocabulary estimate + sample words. |
| `learning_velocity(deck, days?)` | Learning rate + 30-day and 365-day projections. |

---

## Prompts

Prompts are user-triggered templates that load live Anki data into the conversation as context.
Invoke them via the slash menu in Claude Code as `/mcp__anki__<name>`.

| Prompt | Args | What |
|---|---|---|
| `deck_briefing` | `deck` | Vocabulary breakdown, learning velocity, and all pending flags for a deck. |

---

## Setup

**Create the venv and install the MCP SDK (one-time):**
```
python3 -m venv <this anki-mcp directory>/.venv
<this anki-mcp directory>/.venv/bin/pip install mcp
```

The venv is gitignored — run after cloning or on a fresh machine.

**Restart Claude Code** after any changes to `.mcp.json` or the server — it is spawned at startup.

---

## Stdio discipline

Stdout is the JSON-RPC protocol channel.
- Never `print()` outside the SDK — it corrupts the stream silently
- All debug/log output goes to `anki-mcp.log` via `core._log`

---

## AnkiConnect reference

https://git.sr.ht/~foosoft/anki-connect
