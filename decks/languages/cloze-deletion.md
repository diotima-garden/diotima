### User Input Syntax - very strict

- `{word}` — explicit cloze deletion. Always generate a cloze card for this word. If no cue is provided, generate one. 
- `{word::cue}` — explicit cloze with user-provided cue. Use the cue verbatim.

### Output Format

- Cloze deletion **always** belongs to the front of the card
    + Single cloze: `{{c1::hidden expression}}`
    + With cue: `{{c1::hidden expression::cue}}`
    + Multiple: `{{c1::word1}} a b c {{c2::word2}}`
    + Single card, multiple clozes: `{{c1::word1}} a b c {{c1::word2}}`


### When NOT to Generate a Cloze

Do NOT pair a cloze with a production card unless the cloze isolates **knowledge the production card does not force**.

A cloze is redundant when:
- The production card already requires recall of the exact hidden word
- Surrounding sentence context makes the answer inferrable — this makes the cloze much easier than production; SRS intervals diverge and the pair stops supporting each other

**Scaffold alternative:** If your deck's production note type has a `Hint` field, put the key word or form there instead. The hint is hidden by default and revealed on demand — gentle scaffold without SRS overhead or scheduling divergence from a parallel cloze track.

### Quality Check 
- Is cloze actually improving retention?
- Does this cloze test something the paired production card does NOT already force?