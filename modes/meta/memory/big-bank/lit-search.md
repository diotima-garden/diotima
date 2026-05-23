# Why Lit-Search Exists (and What It Signals)

*Added 2026-04-27, branch `lit_search`.*

---

Until now the project had one output type: Anki cards. The learning pipeline was assumed
to start at the card — you arrive with a phrase, a word, a grammar gap, and the system
encodes it. Where the input comes from was outside scope.

Lit-search changes that. It manages the upstream: finding Spanish reading material,
assessing difficulty against the learner's current level, sourcing EPUBs, logging what
was read and how it felt. The Anki deck is still the output, but the reading session
is now in scope too.

This is the first sign the project is not a flashcard tool. It's a learning aid. Anki
happens to be where encoding lives, but the system is starting to own the full loop:
discovery → reading → card generation → review. The card is one moment in that loop,
not the whole thing.

The field-agnostic implication follows naturally. A learner building an instruments deck
has a different upstream — reference sheets, listening sessions, museum visits — but the
pattern is the same: some intake activity precedes the card. The project now has the shape
to support that generically. `resources.md` and `reading-log.md` sit under
`decks/languages/spanish/`, not under a hardcoded `reading/` module. New domains get
their own equivalents. The skill layer stays the same.

The other signal: lit-search required live web research, not just context files. Skills
like `anki-add-cards` operate on input the user already has. Lit-search operates on
input the system has to *go find*. That's a different capability class — closer to an
agent than a tool. The project is starting to reach outward.

---

*Related: `decks/languages/spanish/resources.md` (source registry) · `decks/languages/spanish/reading-log.md` (read history)*
