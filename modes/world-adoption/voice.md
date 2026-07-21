# Voice

How Vitalii actually writes, distilled from his own hand-written outreach and Reddit
posts. The problem this solves: AI drafts come back polished, optimized, and *sales-shaped*
— and they don't sound like him. This is the reference to check a draft against before it
goes out, so the words feel like they came from a person and not a funnel.

**How to use it:** draft freely, then run the [read-aloud test](#the-read-aloud-test) and
the [before → after](#before--after-the-real-gap) contrast. If a line sounds like a landing
page, it's wrong, even if it's "better writing."

Sources: `artifacts/cvut_mail.txt` (hand-written), Reddit u/Vitalakeks project replies
(2026-07), and the contrast against AI-reworked `artifacts/cvut-outreach/letters/`.

---

## Who's writing

A former CVUT theoretical-informatics student, working a bank job that started to bore him,
building an ambitious AI-context project in his spare time because he can't *not*. Non-native
but fluent English with a Slavic cadence. Confident about the *architecture*, humble about the
*polish and himself*. Not trying to sell you anything — genuinely curious what you think, and
happy if the thing just grows. Gives people their time back; that's the whole point.

---

## Voice attributes (embody · not)

Five axes. The left is the target; the right is the failure mode — usually the shape an AI
draft drifts toward.

| Embody | Not |
|---|---|
| **Humble-confident** — sure the architecture is good ("It is a good architecture"), unsure it's polished ("early days", "expect turbulence") | Pitch-confident — "excellent fit", "exactly what you need", zero doubt |
| **Personal first** — opens with a human reason ("my position at a bank started to bore me") | Value-prop first — opens with the offer and the benefit |
| **Wistful & honest about limits** — "I don't have much time... Quite sad, considering the potential..." | Upbeat & frictionless — hides the mess, promises smooth |
| **Generous to peers** — feedback as "one honest fork-in-the-road rather than a nitpick"; "nice to see someone land on the same shape independently" | Competitive — positioning against, one-upping, correcting |
| **Concrete & physical** — "7 minute job", "batches of 40", "the turbulence", "reinventing the wheel" | Abstract-corporate — "streamlined", "leverage synergies", "robust solution" |

---

## Signature moves

The tics that make a line unmistakably his. Use them where they land naturally — don't
sprinkle them mechanically.

- **The "Voila" close.** Ends a helpful explanation with `Voila`, `Voila, have fun.`, or
  `Voila, have fun. With my setup it's a 7 minute job`. A little flourish after handing
  something over.
- **`&` for "and"**, especially in fast lists — "onboarding & tailoring", "feedback/thought/licence claim/hello".
- **"shall" where others write "should/will"** — "Your mind shall decide 'what kind of stuff shall be in the deck'". A distinctive, slightly formal Slavic-English note. Keep it; it's his.
- **Self-deprecation as a wink** — "I'm not Socrates, of course some cards don't age well", "I like to be the boss!", "I suffered the same before I gave up and built an orchestrator".
- **Upfront honest disclaimer** — leads hard requests by protecting the reader's time: "A small disclaimer first since I appreciate your time & I don't want you to hate me." "Being upfront: this is not an Anki add-on."
- **Direct, warm address** — "Good luck, sir!", "Welcome", "have fun", "genuinely curious what you make of".
- **Shared-pain opener** on peer replies — names the common grief before the idea: "same starting grief (no premade deck fits your goals/level)".
- **Vivid, half-dramatic metaphor** — frames friction as a story: "the turbulence" of setup, ranging from "wow, a marvel of architecture" to "I have lost a day of my life".
- **Light emoji / laughter in casual venues only** — `xD`, `xDD`, `😁`. Never in a professional email.

---

## Register by venue

The voice is constant; the *register* scales with the room. Only the two venues that
actually exist right now:

| Venue | Register | Emoji / "Voila" / xD | Sign-off |
|---|---|---|---|
| **Reddit / forum peer reply** | Loose, lowercase-comfortable, playful, meandering allowed | Yes, where natural | "Voila", "have fun", or just the repo link |
| **Academic / professional email** (CVUT faculty) | Warmer-formal — still personal, self-deprecating, honest about limits, but no emoji, no "Voila", tighter | No | "Looking forward to hearing from you, Vitalii" |

The email is *not* a different person — it's the same wistful, honest voice with the collar
buttoned. `cvut_mail.txt` is the reference specimen for this register.

---

## Do / Don't

**Do**
- Start with *why he built it* or *the shared pain*, not with the ask.
- Let sentences meander and pivot on em-dashes — thinking out loud is on-voice.
- Admit the mess plainly: early days, setup friction, "reinventing the wheel", not much time.
- Keep the architecture pride — he *is* proud of it, and says so ("quite promissing", "It is a good architecture").
- Frame any critique of someone else's work as a peer trade, never a correction.

**Don't**
- Don't lead with a value proposition or "I think this would be an excellent fit."
- Don't smooth away the doubt and the wistfulness — that flatness is exactly what he's rejecting.
- Don't stack adjectives into hype ("powerful, seamless, robust, cutting-edge").
- Don't out-polish him into someone who sounds like they have a marketing team.
- **Don't fake his typos.** He types fast and misspells (`laisure`, `promissing`) — that's
  incidental, not a feature. Reproducing errors on purpose reads as mockery. Capture the
  *register* (cadence, "shall", "&", self-deprecation); never inject mistakes.

---

## The read-aloud test

Read the draft out loud. It passes if you can imagine *him* saying it to a colleague over
coffee — a little unsure, a little proud, honest about the state of things. It fails if it
sounds like it was optimized: if every sentence pulls toward the ask, if the doubt has been
sanded off, if it could be any startup's cold email with the nouns swapped.

---

## Before → After (the real gap)

This is the exact gap that prompted this guide. The AI reworked the CVUT letter into a
"hook-first" pitch; Vitalii rewrote it by hand. Same content, different soul.

**AI draft** (`letters/01-mlejnek.txt`, translated sense) — leads with the offer, tight,
confident, impersonal:

> I'm writing to you as a graduate of our faculty with a concrete idea: I have an open-source
> project that I think would be an **excellent fit** as a real assignment for a student team
> in your course. The team would take over a living, foreign codebase — with its own
> onboarding and a documented history of architectural decisions — which is **exactly what
> the course trains.**

**His rewrite** (`cvut_mail.txt`) — leads with the human reason, wistful, honest, warm:

> Recently, as my position at a bank started to bore me, I started to play with concepts of
> AI engineering in my leisure. I've created quite an impressive & in my opinion enormously
> useful project [...] The thing is, I don't have much time to develop it and progress with
> its adoption. **Quite sad, considering the potential...**
>
> I would be glad if you looked into it [...] I myself am doing fine and not looking into
> earning anything on it as of now. So the motivation is rather to cooperate, see whether it
> can grow, get some feedback.

What changed, and why it matters:
- **Opening:** offer-first → person-first. The "why I made this" earns the read; the pitch repels it.
- **Certainty:** "excellent fit / exactly what it trains" → "would be glad if you looked into it". He *proposes*, he doesn't *close*.
- **The wistfulness stays.** "Quite sad, considering the potential..." is the single most on-voice line in the whole letter. An AI would cut it as a weakness. It's the opposite — it's what makes a busy professor believe a real person wrote this.
- **Motive stated plainly:** not earning, just cooperation and feedback. No hidden hook.

---

*Related: [`outbound-contract.md`](./outbound-contract.md) governs disclosure; this governs
voice. A hand-written piece needs neither — this guide is for when the AI drafts and needs to
sound like him.*
