 but remind me what audience is this essay for? Where are we sending it?

Per the outline we set: Hacker News (as a link post to the essay hosted on diotima.garden or the repo), cross-posted to r/artificial, and optionally lobste.rs. The audience is technical builders and self-directed learners — the same people watching Dwarkesh clips — and the window is the next ~2 weeks while the Sanderson clip is still circulating.

One honest caveat now that the AI-disclosure note is in it: that note plays differently per venue.

- Lobste.rs — effectively off the list. Their community norms prohibit AI-generated submissions, and the disclosure would get it flagged regardless of the framing.
- HN — risky but defensible. HN is broadly hostile to AI-written content, but your framing ("the intent and taste are mine, and that's literally the essay's thesis") is the strongest possible version of the disclosure — it's self-demonstrating. Some readers will engage with exactly that; some will dismiss it on principle. Expect the disclosure itself to become a comment thread.
- r/artificial — lowest friction; AI-assisted writing is unremarkable there, though the audience is also the least likely to contain grove-author educators.

There's also a venue we didn't have in the outline but arguably fits best: your own blog at diotima.garden first, always — the essay needs a home URL anyway, and every other channel (HN submission, the Reddit threads you already have live, the possible Sanderson email) then points at it. The YouTube reply and your existing r/Anki presence can reference it once it's up.

So the realistic sequence: publish on diotima.garden → submit to HN → mention in r/artificial and alongside your existing Reddit threads. Drop lobste.rs.



# Encode the teacher, not the textbook

*A note before anything else: this essay was drafted with an AI. I consider that a
feature of honesty, not a confession — the intent and the taste that guided it are
mine, and the essay's own argument is that intent and taste are the part that matters,
whatever vehicle carries them. Judge it on whether that holds.*

---

Grant Sanderson — 3Blue1Brown, a person who has thought harder about explanation than
almost anyone alive — recently said something on the Dwarkesh Podcast that names a
problem I've been building against for months.

LLM explanations, he observed, feel like Wikipedia: stuck in a **local minimum of
correctness**. Every sentence is factual. Nothing is wrong. And yet nothing carries you
anywhere, because great teaching is not a sequence of true sentences — it's an
expository arc. A good educator will hand you a simplified model that is technically
80% wrong, let it do its intuitive work, and only then show you where it breaks.
Sanderson calls this **correctness on the way**. Wikipedia can't do it, because
crowd-editing sands off anything that isn't immediately defensible sentence-by-sentence.
LLMs can't do it either — and I think it's worth being precise about why.

## The flatness is structural

It's tempting to file this under "models aren't good enough yet." I don't think that's
it. An LLM answer is optimized to be *standalone-correct*: whatever you ask, the
response should be defensible on its own, because the model has no idea whether this is
the first thing you'll read or the fortieth, and it will be judged — by you, by
evaluators, by the internet — on that single response. That is the same selection
pressure that flattens Wikipedia. A thousand edits, each individually reasonable, each
removing a sentence that was "misleading out of context," and the article converges to
a list of facts. The pedagogical white lie — the load-bearing simplification that a
teacher plants deliberately, intending to break it later — cannot survive an
optimization process that scores each unit of text in isolation.

Bigger models won't fix this, because it isn't a capability problem. It's an objective
problem. The arc was never in the loss function.

## Sanderson's fix is half right

His practical advice: use the LLM as a souped-up Google. Don't ask it to explain
semiconductors; ask it *who explains semiconductors well*, and go read the human. The
model's knowledge of the artifact landscape is genuinely superhuman even when its
attributions are shaky — in his own anecdote, Claude invented a 3Blue1Brown video that
doesn't exist, yet still linked him to exactly the right video by someone else.

But the comments under that clip contain the strongest counterargument, and it deserves
a steelman. One commenter described directing an LLM precisely: *lay out the top-level
concepts, here's my background, now recurse depth-first into the ones I don't know.*
A static artifact can't do that. A book has one pace and one assumed reader; the finest
lecture in the world cannot pause when *you* are confused. Adaptivity is the one thing
generative models are unambiguously better at than any fixed artifact, and "just go
read the human" throws it away.

So we have a real tension. Human artifacts have the arc but can't adapt. LLMs adapt
but have no arc. Routing picks the first side. Prompting picks the second.

## The third option: package the method, not the material

Here's the thing routing misses: the artifact was never the asset. The asset is the
**author's method** — the way Sanderson decomposes a subject, decides what's worth
encoding, knows which simplification to plant and when to break it. The video is one
rendering of that method at one pace for one imagined viewer.

So encode the method itself. Let an expert write down, explicitly, as a package: how
this domain breaks apart, what "good understanding" looks like at each stage, which
intuitions to build first and which corrections to schedule later, how to pull source
material in. Not a textbook — a *generative spec*. Then let an AI runtime **play** it:
the dialogue adapts to you, the arc comes from the author. The LLM stops being the
educator and becomes the instrument the educator's score is performed on. You get
correctness on the way *and* a tutor that pauses when you're confused.

This also answers Sanderson's deeper point, the one he opens with: **who matters more
than what**. Pick your educator, not your topic. A format like this has to protect the
*who* — which means packages must be sovereign and single-author. Nobody wiki-edits
someone's pedagogy into gray paste. If you want a different arc, you **fork** the
package and re-aim its method at your own subject — inherit, recombine, redirect, the
way software packages compose. The educator's taste stays intact all the way down the
lineage; the crowd contributes by forking, not by flattening.

## What exists today

I'm building this, in the open, under the name **Diotima** (diotima.garden). The
packages are called *groves*; the runtime is a learning conductor that plays them.
Honest maturity report: the daily-driven part today is memory — groves that drive
spaced repetition through Anki, with trust mechanics I'd want from any AI touching
years of my own review history (backup, then diff, then explicit approval, then a log).
The grove format's full semantics — inheritance, composition, distribution — are still
being designed, and that's exactly the stage where outside taste changes the outcome.

The person I'm looking for is the educator whose method deserves to outlive their
artifacts. If you've ever watched a student struggle and known *precisely* which wrong
model to hand them first — that knowledge is currently trapped in your head and your
videos. I want it to be a package.

Repo: github.com/diotima-garden. The clip that prompted this:
"The Trick to Using LLMs to Learn" on Dwarkesh Clips.
