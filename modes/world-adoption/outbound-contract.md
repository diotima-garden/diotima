# Outbound Contract

Governance contract for every piece of content this system prepares for the public
internet — posts, comments, emails, replies. Canonical location: this file. Skills and
pipelines render from here and never hardcode or paraphrase the wording.

**Invariant core** (present in every rendering, every venue):
the author's name + the phrase **"AI-drafted, human-sent."**

---

## Disclosure — canonical stance (v1)

<!-- DEFAULT IMPLEMENTATION — rewrite this in your own voice, then bump the version.
     This is the full statement. It lives here and, once published, at diotima.garden/ai.
     Venue renderings below compress it; they change only when this changes. -->

> You are reading text drafted by an AI and sent by me. My time and capacity are
> limited, and I choose to spend them on intent and direction rather than wordsmithing.
> The words may be imperfect — I may not even love all of them myself. Their job is
> narrower than perfection: to bring you into a specific room, hand you the context of
> one idea, and let you judge it. The taste that selected the idea, and the decision to
> send it to you, are mine.
>
> — Vitalii

---

## Venue renderings

Same meaning everywhere; wording varies to fit venue norms and link policies. The
rendering is applied **verbatim** — the preparing skill never rewrites it.

| Venue key | Placement | Rendering |
|---|---|---|
| `post` (Reddit, forums, blog cross-posts) | header, above the content | *This post is AI-drafted, human-sent: my time is limited, so an AI wrote the words and I chose the idea, reviewed it, and stand behind sending it. Full stance: diotima.garden/ai — Vitalii* |
| `comment` (Reddit/HN comments, link-tolerant) | footer | *— Vitalii (AI-drafted, human-sent — full stance: diotima.garden/ai)* |
| `bare` (link-hostile venues, e.g. YouTube comments) | footer | *— Vitalii (AI-drafted, human-sent; search "diotima garden" for my full stance)* |
| `email` | header + normal signature | *A note before the content: this email is AI-drafted, human-sent — I chose the idea and reviewed every word, but an AI wrote them, because my capacity is limited and I'd rather reach you imperfectly than not at all. Full stance: diotima.garden/ai* |

Exception: content the author writes or substantially rewrites by hand carries no
disclosure — the contract covers AI-drafted text, not the author's own.

---

## Outbound standards

Labeling is necessary, not sufficient. Every outbound piece also satisfies:

- **Human approval, per piece.** Nothing is sent that Vitalii has not seen assembled in
  final form. The preparing skill stops at an approval gate; it never posts.
- **No bulk identical bodies.** The same body is never sent to multiple venues without
  venue-specific adaptation — both courtesy and spam-filter hygiene (identical repeated
  text is a dedup signature).
- **Venue rules first.** Self-promotion, link, and automation rules of the target venue
  are checked before preparing; a disclosure does not license breaking them.
- **Rate discipline.** No posting bursts. Volume is throttled by the human approval
  gate by design.
- **Ledger entry per sent piece.** See below.
- **Version bump on stance change.** Editing the canonical stance increments its
  version; renderings are re-derived.

---

## Ledger

Every piece confirmed as sent is appended to `outbound/ledger.md`:

```
## <YYYY-MM-DD> · <venue key> · v<disclosure version>
Target: <where exactly — thread, subreddit, address>
Content: <one-line description, or path to the draft file>
```

The ledger is the audit trail and, later, the source for a public transparency page.

---

## Planned enforcement

When outbound posting tools are added (Reddit/YouTube MCP or scripts), a **PreToolUse
hook must gate every send on the presence of the invariant core** ("AI-drafted,
human-sent" + author name). Adding a posting tool without that hook violates this
contract — the disclosure must be structurally unskippable, not a convention.
