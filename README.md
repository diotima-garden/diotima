# Project Diotima
> *The choice of what one learns manifests their taste & essence*
>
> *Learning itself is a mere waste of time dictated by biology of mind.*

`[Hmm... the second part doesn't age well...]`

Imagine, Aristotele sharing his reasoning dogmas with you and approaches on how
exactly he filters information, and in what format he would like to preserve it in his being.
What if he could share it with you via one thin 'plugin'?

Imagine the most efficient way for Aristotele to learn would be to build this 'plugin'
for his own daily use and reasoning. This way, sharing it would cost him nothing.



Basically one abstraction layer higher.

Instead of sharing domain knowledge
We share taste, knowledge filter & generator.


In a way, Internet itself does it but how many sailors has it's tide consumed..?! (for the amount of noise)
In a way - universities are quite good at it... And in fact they shall be the most zealous to jump on board.
Enough words! Go! Explore!!

## details for nerds like myself ;)
An AI-powered **learning conductor**: a generalized interface for learning any skill,
built on spaced repetition (Anki) and context engineering. Describe a domain once, and
the system takes over the boring machinery.

> Not just automating Anki; automating the
> [*rules about how automation gets written*](modes/meta/memory/big-bank/trajectory-snapshot.md#L32).

---

## You don't operate this — an LLM does

**This is not a tool you drive by hand.** There are no commands to memorize and no UI to
learn. You talk to an LLM (today, Claude Code); it reads `CLAUDE.md`, sees the available
skills and MCP tools, and from that alone has *full coverage of the project*. The whole
repo is built, from the ground up, to be *legible to a model reading it cold*.

- **For a curious user:** don't judge it by the install length below. Once it's running,
  you don't wrangle it — you ask, and it acts.
- **For a contributor:** the same property makes it unusually easy to work on. Point an
  LLM at the repo and it will orient itself the same way it orients an end user.

---

## What it does today

**Context-aware card generation for a specific domain.** Point it at a *grove* (a
per-domain knowledge spec) and an input, and it compiles the domain's rules into the
prompt, backs up the deck, generates cards at your skill level, and syncs them in.

One real run, start to finish, is narrated in
[Example: adding two sentences to the Spanish deck](#example-adding-two-sentences-to-the-spanish-deck).

**Context-aware extraction from YouTube**, specific to the area you're focusing on
(via the Gemini API) — turn a video into deck-ready material without watching it end to end.

<img width="1893" height="803" alt="YouTube extraction via Gemini" src="https://github.com/user-attachments/assets/d5b4c3bf-2a11-4372-a009-214192da60fc" />

### A feedback loop runs the other direction, too

Write a plain-language fix onto any card in Anki, and the system finds it, edits the
fields, and keeps an append-only log of every change. One card's full round trip,
screenshotted:
[`plugins/anki-mcp/README.md` → Example: feedback loop in action](https://github.com/diotima-garden/anki-mcp/blob/main/README.md#example-feedback-loop-in-action).

---

## Example: adding two sentences to the Spanish deck

The whole interface is one casual message — two phrases jotted down mid-conversation,
one of them with a typo and no accents:

```
add these to my spanish deck:
Monsieur es todo un conocedor de la alta cocina.
Estas hecho un limon
```

That's enough to launch the `/pipe:anki-add-cards` pipeline. Before anything is
generated, the trust machinery runs: the grove's context compiles in the background
while the collection syncs, "spanish" fuzzy-matches to the actual deck name
**Español**, and the deck is backed up to a dated `.apkg` — every run, not just risky
ones:

![Deck names resolved via MCP, "spanish" matched to Español, backup skill launching](assets/add-cards-01-resolve-backup.png)

Generation happens in an isolated subprocess that sees only the compiled grove
context — the deck's dialect rules (Rioplatense, voseo), card-design constraints, and
tagging taxonomy. The two sentences come back as five proposed cards: each input's
primary production card plus supporting pattern cards, already scanned against known
quality leaks. Nothing has touched Anki yet — the batch stops at an approval gate, and
the answer doesn't have to be yes or no:

![The five generated cards previewed with an approval prompt, the user typing "only add 1 and 4"](assets/add-cards-02-preview-approve.png)

`only add 1 and 4` is respected exactly — the two chosen cards are pushed, the three
others dropped, and the collection syncs back to AnkiWeb:

![Report: added 2 cards to Español and synced, listing both cards](assets/add-cards-03-report.png)

The result, rendered live in Anki. Note what the pipeline did beyond translation: the
front is a *situational English cue* (per the grove's rule that idiom fronts must
trigger production, not recognition), the input's missing accents came back as *Estás
hecho un limón* on card 4, and the etymology landed in a collapsible
"interesting facts" section that stays out of the way during review:

![The Monsieur card rendered in Anki: English cue on front, Spanish answer, collapsible interesting-facts section](assets/add-cards-04-rendered.png)

---

## Why it's built this way

Basic "LLM makes Anki cards" is a solved, crowded space. What's different here is the
architecture around it:

- **Context garden** — each domain is a declarative spec (`groves/…`), compiled into the
  generation context. Rules live as data, not as prompts you retype.
- **One conductor across domains** — languages, instruments, and anything you add next
  reuse the same orchestration layer instead of each getting a bespoke script.
- **Deep Anki-state feedback** — vocabulary maturity, learning velocity, and review
  history feed *back* into what the AI generates. Most tools only push cards in; this one
  reads the collection's state and adapts.
- **Automation about automation** — pipelines, skills, and enforcement rules are
  first-class, versioned artifacts, so the system's own construction is legible and safe
  to evolve.

Start with `CLAUDE.md` for the full map, or `groves/languages/spanish/context.md` for a
worked example of a domain.

---

## Where this is going: a grove marketplace

The obvious "marketplace" idea for a project like this would be a **shared library of Anki
decks**. I think a **library of shared *groves*** is the better primitive — and it's the
direction I want to take this.

A deck is a frozen output: someone's finished cards, take them or leave them. A grove is
the *generative spec* — how a knowledgeable person chose to break the subject down:
what's worth a card, what card types fit, what "good" looks like, how source material
gets pulled in. Sharing that is sharing the *method*, not just the result, and the
method is what's actually hard to reproduce.

Because a grove is easy to point an LLM at, you don't adopt it wholesale — you remix it:

> *Say someone publishes a history grove — its whole approach is populating an Anki deck
> with the important dates and pulling in matching images from Wikipedia. You point the
> LLM at it and say: "I like how they approach history knowledge at Harvard; take their
> grove, but let's focus it on the history of mathematics instead."*

You inherit an expert's *encoding of a domain* and re-aim it at what you actually want to
learn, in one sentence. The full trajectory — grove format, inheritance and composition,
distribution — lives in
[`modes/meta/architect/product-vision.md`](modes/meta/architect/product-vision.md).

### Licensing: open runtime, sovereign groves

The runtime is open source under
[Apache-2.0](LICENSE). Groves are a different thing: a grove you create is *your*
content — the runtime's license doesn't touch it, and you choose how to share it (or
not to). For groves meant to be forked and re-aimed, a share-alike content license like
[CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/) is the natural fit — it
keeps the remix chain open the same way the grove format keeps it traceable. As the
grove format matures, each grove will declare its license in its manifest so an
inheritance chain stays legally clear end to end.

---

## Status: works on my machine — and that's exactly where help is wanted

Honest disclosure, because it changes what you should expect: **this is a power-user
setup, not a product yet.** It delivers real daily value on my machine, but getting it
running elsewhere is currently a technically involved, hand-assembled process. The
architecture and the direction are set; what's left is largely engineering to make it
portable and packaged — work that's a great fit for a contributor and a poor fit for the
time I have available.

If you like the idea and enjoy turning "works on my machine" into "works anywhere," this
is an unusually clean on-ramp: the vision is stable, the seams are mapped below, and the
first contributions are self-contained.

### The moving parts (what a fresh install currently touches)

- **[Claude Code](https://claude.com/claude-code)** — the whole thing runs as skills,
  pipelines, and MCP tools inside the Claude Code harness.
- **Anki desktop + [AnkiConnect](https://ankiweb.net/shared/info/2055492159)** add-on,
  installed and running — the MCP server drives Anki through it.
- **Two git submodules** — `plugins/anki-mcp` (the Anki MCP server) and `.claude/utils`
  (shared Python helpers), referenced over HTTPS so anonymous clones work with no
  GitHub SSH key. If you prefer pushing over SSH, add a rewrite to your own global
  gitconfig instead of editing the tracked URLs:
  `git config --global url."git@github.com:diotima-garden/".insteadOf "https://github.com/diotima-garden/"`
- **Several Python virtualenvs**, gitignored and set up per machine:
  `plugins/anki-mcp/.venv` (needs `mcp`), `plugins/context-compiler/.venv`, and
  `.claude/gemini/.venv` (needs `google-genai`).
- **A `GOOGLE_API_KEY`** — *optional.* Only needed for the advanced, Google-native
  YouTube extraction (Gemini-backed). You don't need it to get started; skip it and the
  rest of the system works without the video-extraction feature
  ([free tier key](https://aistudio.google.com/apikey) if you want it later).
- **`.mcp.json` wiring** that spawns the server with a `--managed-config` path.

### Rough install path (until this is packaged)

1. Install and open Anki; add the AnkiConnect add-on; leave Anki running.
2. Install Claude Code.
3. Clone this repo, then `git submodule update --init --recursive`.
4. Create the virtualenvs above and install each one's dependency (`mcp`, plus
   context-compiler's; add `google-genai` only if you want YouTube extraction).
   Components with their own Python setup document the exact commands in their own
   READMEs — see `plugins/anki-mcp/README.md` and `.claude/gemini/README.md`; check a
   component's README whenever its setup looks non-obvious.
5. *(Optional, for YouTube extraction only)* export `GOOGLE_API_KEY`.
6. Open the repo in Claude Code and restart it once so the MCP server is picked up.

Yes — that's more steps than it should be. That's the point of the next section.

---

## Where help is wanted (the contributor backlog)

These are the seams between "works for me" and "works for anyone." Each is fairly
self-contained:

1. **Cross-platform support** — the plugin/config directory layout is non-standard and
   has bitten a Windows setup already. Making paths OS-agnostic is the highest-value fix.
2. **Automated setup → a single deliverable** — replace the manual venv-and-key dance with
   a reproducible bootstrap, and ultimately package the whole thing as one installable
   artifact so an end user runs a single command instead of assembling parts by hand.
3. **LLM-provider-agnostic core** — migrate the Claude-Code-shaped runtime toward
   [opencode](https://opencode.ai) as a portable, provider-agnostic base, restructuring
   `.claude/` into harness-neutral homes along the way. The layout rules driving this
   are in [`modes/meta/architect/product-vision.md`](modes/meta/architect/product-vision.md).

If any of these looks fun, open an issue to say hi — the architecture is documented and
I'm happy to orient you.

