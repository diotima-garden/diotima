### User Input Syntax

- `{word}` — explicit cloze deletion. Always generate a cloze card for this word. If no cue is provided, generate one. 
- `{word::cue}` — explicit cloze with user-provided cue. Use the cue verbatim.

### Output Format

- Cloze deletion **always** belongs to the front of the card
    + Single cloze: `{{c1::hidden expression}}`
    + With cue: `{{c1::hidden expression::cue}}`
    + Multiple: `{{c1::word1}} a b c {{c2::word2}}`
    + Single card, multiple clozes: `{{c1::word1}} a b c {{c1::word2}}`


### Quality Check 
- Is cloze actually improving retention?