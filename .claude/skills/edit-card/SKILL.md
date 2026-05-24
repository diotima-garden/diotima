---
name: edit-card
description: Apply an edit instruction to an existing Anki card using compiled deck guidelines. Internal skill — invoked by anki-process-red-edit only. ARGUMENTS: compiled deck context and card batch — passed inline by the orchestrator.
context: fork
disable-model-invocation: false
user-invocable: false
---

$ARGUMENTS


Output ONLY the edited cards in the exact output format specified above. Prefix each card result with its `note_id` anchor on its own line: `[note_id: <id>]`. Preserve the order of input cards. No preamble, no commentary, no explanation.
