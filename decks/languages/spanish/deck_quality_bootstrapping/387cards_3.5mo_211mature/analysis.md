# Spanish Deck Quality Analysis
**Snapshot date:** 2026-05-25  
**Deck age:** ~3.5 months (first cards Feb 2026)

## Deck State

| Metric | Value |
|---|---|
| Total cards | 387 |
| Total notes | 368 |
| Mature (interval ≥ 21d) | 211 (55%) |
| Young (interval 1–20d) | 151 |
| Learning | 0 |
| New (unseen) | 25 (the manos idiom batch) |
| Estimated vocabulary | 316 |

---

## What Anki Does Well in Language Learning

Anki is a **form storage and retrieval tool**, not a fluency builder. It earns its keep for:
- Fixed forms that must be exact: irregular conjugations, pronoun placement, prepositions
- High-frequency vocabulary and collocations
- EN→ES production patterns that prime active recall under conversational pressure
- Idioms and fixed expressions where the exact wording matters

It cannot build fluency, pragmatic judgment, listening comprehension, or grammar understanding. Those need real conversation and immersive input. Anki builds the inventory; real use drills the retrieval.

---

## Strengths

**Production-first design.** EN→ES cards dominate, no ES→EN recognition cards. Correct call for active speaking goals.

**Dialect awareness.** Most backs note Argentine vs Spain variants explicitly. Not sleepwalking through textbook Spanish.

**Level tagging with progression.** A1→B2 spread is coherent. Oldest mature cards (interval 157–378 days) are the right ones: ser/estar, ir a, hacer, saber, pronouns, direct/indirect objects.

**Healthy core.** Zero cards currently in learning. The grammatical base is holding.

**Cloze used correctly in early cards.** Early cloze cards isolate irregular forms ("fui", "hago", "hice", "sé") in sentence context — that's the right use.

**Rich backs on hard items.** Etymologies and grammar notes on complex cards (*cría cuervos*, *mamá mona*, *chancha y los veinte*, *ser un rata*) are genuinely useful for encoding.

---

## Efficiency Leaks

### Leak 1 — Production + cloze duplication (~30% of deck, ~100–120 parallel pairs)

Almost every item has both an EN→ES production card and a cloze card hiding the key word. Scheduling data shows cloze consistently runs easier than the production pair because the Spanish sentence context gives away the answer:

| Item | Type | Factor | Lapses | Interval |
|---|---|---|---|---|
| "I do my homework every day" | production | 1300 | 2 | 25d |
| "Yo ___ la tarea todos los días" | cloze | 2650 | 0 | 335d |
| "I made dinner yesterday" | production | 1300 | 2 | 21d |
| "Ayer ___ la cena" | cloze | 1800 | 2 | 36d |

The cloze tests an easier version of the same knowledge. At ~15s/review this is meaningful time.

**Fix:** Keep cloze only when it isolates something the production card doesn't force — a preposition choice buried in a longer sentence, a tricky pronoun position, an irregular form inside a clause that the production card doesn't highlight. Delete cloze when the production back already leads with the exact form being tested.

---

### Leak 2 — 7 leech cards (factor ≤ 1500)

These cards have been failed 3–4 times and are not being retained. They're costing repeated review sessions while contributing near-zero fluency.

| Card ID | Content | Factor | Lapses | Interval | Problem |
|---|---|---|---|---|---|
| 1772046452577 | "I was tired, so I went home." | 1300 | 4 | 20d | Too many moving parts; *entonces* + preterite + imperfect |
| 1772366251957 | "May I have the menu?" | 1300 | 3 | 2d | Voseo *traés* keeps slipping |
| 1772484840013 | "Puedo darte un abrazo?" | 1450 | 4 | 23d | Pronoun attachment to infinitive |
| 1774207509479 | "I've been going since I was little..." | 1300 | 2 | 17d | Complex present perfect; constructed, not heard in speech |
| 1774207509486 | "What has been occupying your thoughts?" | 1300 | 2 | 16d | Abstract; no conversational anchor |
| 1774207462172 | "¡Qué sorpresa! ¡Cuánto tiempo sin verte!" (cloze) | 1900 | 3 | 3d | Cloze hiding *sorpresa* — low signal |
| 1774207462173 | "El cajero se ha tragado mi tarjeta" (cloze) | 1600 | 3 | 15d | *Tragarse* reflexive construction |

**Fix:** Restructure or delete. Repeated failure is a card design signal, not a discipline problem. Cards 1774207509479 and 1774207509486 are particularly suspect — they're constructed sentences with no real-world anchor. They will be re-learned naturally once encountered in conversation.

---

### Leak 3 — Animal idiom batch uses Spanish-front format (26 cards)

The May animal idiom batch has **Spanish definition → Spanish idiom** format:

> Front: "Hay algo oculto o un misterio"  
> Back: "Hay gato encerrado"

This is neither EN→ES production nor ES→EN recognition — it's Spanish paraphrase → Spanish idiom mapping. It violates the deck's own rule and tests a weaker skill. You will never encounter a Spanish paraphrase in conversation and need to produce the idiom; you'll encounter a *situation* in English and want to reach for the expression.

**Fix:** Flip all 26 fronts to situational English cues:
> Front: "There's something fishy going on here."  
> Back: "Hay gato encerrado."

Affected cards: 1778617822219 through 1778617822309 (the full animal idiom batch).

---

### Leak 4 — Idiom concentration

~26 animal idioms + 26 manos idioms (unseen) + ~20+ expressions ≈ **70+ idiom cards**, ~20% of the deck and growing. Idioms have a specific Anki problem: you remember them in the sterile review environment but can't fire them spontaneously in conversation because they need a situational trigger you only encounter in real speech. Adding 26 at once also creates mutual interference — similar-looking expressions (*irse de las manos / irse a las manos / estar hasta las manos*) compete during recall.

**Fix:** Add idioms reactively — when you've actually heard or read one in context. That gives the card a real memory anchor. Batch-generated idiom blocks are the lowest ROI card category. The manos batch (all 26 unseen) should be reviewed carefully before adding more.

---

### Leak 5 — European Spanish vocabulary in an Argentine deck

Cards with Spain-register forms: *chulo*, *cuqui*, *majo*, *ostras*, *vale*, *caña* ("ser la caña"), *patatas*, and **coger** (functionally vulgar in Argentina — "coger el tren" is a problem). Using these in Buenos Aires signals "ese que habla como español" and creates review interference: during recall, which form is correct for Argentine?

Cards to audit:
- `vocab::adjective::chulo`, `vocab::adjective::majo`, `vocab::adjective::cuqui`
- `vocab::expression::vale`, `vocab::expression::ser_la_cana`
- Any card using *patatas* (Argentine: *papas*), *ostras*, *coger* (transport sense)

**Fix:** Either tag `register::european` if you want them as reference, or retire if the goal is purely Rioplatense. The ambiguity in the current deck leaks into reviews.

---

### Leak 6 — Back content verbosity on some cards

Some backs are excellent and rich. A few have grown so long the key form gets buried. The form you need to produce should be the **first line** of the back. Everything else is optional context, read only when needed. *Chancha y los veinte* and *mamá mona* are close to the limit — the etymology is valuable but the payoff form should lead.

No bulk fix needed — just a design principle for new cards.

---

## Priority Order for Execution

| # | Direction | Effort | Impact |
|---|---|---|---|
| 1 | Delete / restructure 7 leeches | Low | High (immediate queue relief) |
| 2 | Fix animal idiom fronts (ES→EN) | Medium | High (wrong card type) |
| 3 | Audit + retire redundant cloze pairs | High | High (deck size reduction, ~50–80 cards) |
| 4 | Audit + tag/retire European Spanish cards | Low-Medium | Medium (dialect coherence) |
| 5 | Review manos batch, then decide | None yet | Medium |
| 6 | Pause idiom batching; switch to reactive | Behavioral | Medium (prevents future debt) |

---

## Execution Artifacts (added as work progresses)

_This section will track decisions made, cards retired, and findings discovered during execution._

| Date | Direction | Action | Notes |
|---|---|---|---|
| 2026-05-26 | Leak 1 | Created `Production` note type `[Front, Back, Hint]`; fixed `update_note_model` tag-preservation bug; sandbox tested | See `leak1_inefficient_cloze.md` |
| 2026-05-26 | Leak 1 | Migrated 249 `Basic` production notes → `Production`; 66 notes received Hint (irregular forms, voseo, pronoun attachment) | `migrate_to_production.py` |
| 2026-05-26 | Leak 1 | Deleted 19 redundant cloze notes (paired production card forces the same form); 83 cloze cards remain | `audit_cloze_pairs.py` |
| 2026-05-26 | Leak 2 | Deleted 4 notes (2 constructed/no-anchor production, 1 redundant cloze, 1 cloze converted); restructured 2 production backs; added 1 replacement Production note (darte) | 6 of 7 leeches resolved; note 1774207462172 was already gone |
| 2026-05-26 | Leak 4 | Closed — manos batch was extracted from a YouTube video (Spanish explanations present), giving each idiom a real-world anchor; reactive extraction from consumed content is the right intake pattern | No further action |
