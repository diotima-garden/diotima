---
name: generate-cards
description: Generate Anki cards from a compiled deck context and user input. Internal skill — invoked by the anki-add-cards pipeline step only. ARGUMENTS: compiled deck context, available note types, and card input — passed inline by the orchestrator.
context: fork
disable-model-invocation: false
user-invocable: false
---

$ARGUMENTS


Output ONLY the cards in the exact format specified. No preamble, no commentary, no explanation.
