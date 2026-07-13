# r/AnkiAi law workflow reply (2026-07-13)

Target thread: r/AnkiAi — "[Anki / Law] How to stop over-creating cards and fix a slow legal workflow?"
https://www.reddit.com/r/AnkiAi/comments/1uct658/anki_law_how_to_stop_overcreating_cards_and_fix_a/
By: Zealousideal_Sort599 (score 3, 1 comment)

Existing comment to acknowledge: Xemorr (+2) — "the pop quiz problem": AI makes flashcards
of facts you'd need for a pop quiz, not a real exam; hasn't found a fix.

Venue key: `comment` (Reddit, link-tolerant) → footer disclosure.

## Draft body

> Xemorr's "pop quiz problem" is the crux, and I don't think it's a prompt-tuning
> problem — it's a missing-spec problem. AI dumps a wall of cards because it has no
> encoded definition of what's card-worthy *for your exam*, so it defaults to trivia.
> The wall isn't the AI being dumb; it's the AI having no taste you gave it.
>
> What worked for me (learning something with a similar "must produce, not just
> recognize" shape): write the card-worthiness rules down once, per deck, and make the
> generator obey them instead of free-associating. For you that spec is basically already
> in your post — "only what I can't look up fast in the Code," "conflicting arguments,
> not settled ones," "the trigger that starts a line of development." Feed *that* to the
> AI as the contract, not just the raw notes. It stops manufacturing pop-quiz facts
> because you've told it what the exam actually rewards.
>
> On your tree question: the fix for "thousands of micro-cards" is to stop doing
> one-fact-per-card for case law. One card whose *answer* is a small structured tree —
> holding → the two competing rationales → which prevailed and why — tests the shape of
> the development, which is what an oral/essay exam probes anyway. Fewer, denser cards
> beat a swarm of atoms when the exam rewards synthesis.
>
> On reading-vs-Anki for critiques: reading is enough for recognition, not for
> production. If the exam makes you *generate* the critique, pure reading will feel
> fluent and then collapse under load — the illusion of competence is real there. You
> don't need many cards, but you need a few that force production ("state the strongest
> objection to X and the counter"), not recognition.
>
> The pruning half is what I ended up building: when a card turns out to be pop-quiz
> junk mid-review, I annotate it in a field on the card and a batch job reworks or cuts
> it against the deck's spec later — so the wall gets pruned over time instead of by
> hand. Open source, early days, deck-aware rather than a generic generator:
> github.com/diotima-garden

## Notes
- Answers all three (Xemorr's problem + OP's Q1 and Q2) before any self-mention.
- Repo appears once, at the end, framed as "the pruning half," not the headline.
- Concedes "early days" — builder voice, not marketer.
- Link-tolerant venue, so a bare GitHub org link is fine; disclosure footer carries
  diotima.garden/ai per contract.
