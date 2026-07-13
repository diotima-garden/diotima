# Sanderson clip response (2026-07-13)

Video: "The Trick to Using LLMs to Learn – Grant Sanderson" (Dwarkesh Clips, 2026-07-08)
https://www.youtube.com/watch?v=q06rLw6imT0

Target thread: @latentspaceexplorer ("conducted learning… prepared by human experts")
→ reply by @progamer1196: "Any app for this?"

## YouTube reply draft (no URLs — links get auto-removed on this channel)

> Working on an open-source attempt at exactly this. The idea: an expert writes down
> how they break a domain apart — what's worth encoding, what "good" looks like, the
> order that keeps the motivation alive — and an AI runtime plays that spec in dialogue
> with you. So the LLM isn't inventing the pedagogy (the flatness Grant describes), it's
> executing an educator's expository arc. Anyone can fork a package and re-aim the same
> method at their own subject. Early days — today it drives spaced repetition (Anki) —
> but the format is the point. Called Diotima; searching "diotima garden" finds it.

Notes:
- Reply under @progamer1196's comment, not top-level — answers a live question instead
  of cold-pitching.
- "diotima garden" as searchable name-drop instead of URL.
- Deliberately concedes "early days" — reads as builder, not marketer.

## Essay outline — "LLMs flatten pedagogy. A package format that preserves it."

Venue: HN (Show HN or essay link), cross-post r/artificial, lobste.rs. Link-friendly,
unlike YouTube. Timely while the clip circulates (~2 weeks).

1. **Hook.** Sanderson on Dwarkesh: LLM explanations sit in a "local minimum of
   correctness" — every sentence factual, no expository arc. Great teaching needs
   "correctness on the way": simplified models first, refined later.
2. **Why flatness is structural, not a model deficiency.** Each LLM answer is optimized
   to be standalone-correct — the same force that flattens Wikipedia via crowd-editing.
   Bigger models don't fix an objective-function problem.
3. **Sanderson's fix is half right.** LLM-as-router to human artifacts works, but
   artifacts are static. Steelman the strongest comment pushback (@ajaypande6391): a
   prompted LLM *can* adapt to your level and pace, which no fixed book does. Both
   sides hold a real piece.
4. **The third option: encode the author, not the artifact.** Don't route to the
   expert's *output* — package the expert's *method*: how they decompose the domain,
   what's worth encoding, what good looks like, the motivational sequence. A generative
   spec an AI runtime plays. You get the authored arc AND the adaptivity.
5. **Preserving the "who."** Sanderson: "who matters more than what." So packages are
   sovereign and single-author — you fork-and-refocus, you never wiki-edit someone's
   pedagogy. Docker-image analogy: inherit and recombine, don't homogenize.
6. **What exists today.** Diotima (diotima.garden): groves + runtime, daily-driven
   Anki/spaced-repetition workflow, trust mechanics (backup → diff → approval → log).
   Honest maturity statement: format semantics still being designed.
7. **Ask.** Open source; looking for educators who want their method to outlive their
   artifacts — grove authors. Repo link.

Title options:
- "LLMs flatten pedagogy. Here's a package format that preserves it"
- "Grant Sanderson is right about LLM learning — and routing isn't the whole answer"
- "Encode the teacher, not the textbook"
