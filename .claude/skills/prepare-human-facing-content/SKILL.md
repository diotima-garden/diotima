---
name: prepare-human-facing-content
description: Wrap a draft in the outbound disclosure contract before it goes to the internet — venue-aware rendering, approval gate, ledger entry
disable-model-invocation: false
---

Prepare a piece of AI-drafted content for the public internet. Renders the disclosure
from the outbound contract, assembles the final piece, and stops for the user's
approval. This skill **never posts** — it prepares.

**Usage** `/prepare-human-facing-content <venue> [draft text or path]`

`venue` is a venue key from the contract's renderings table. If the draft is omitted,
use the content being worked on in the current conversation.

## Load the contract

Read `modes/world-adoption/outbound-contract.md`. All disclosure wording, placements,
and standards come from there — never hardcode, paraphrase, or "improve" them.

## Resolve the rendering

Pick the rendering row matching `<venue>`. If the venue key is not in the table, stop
and ask the user which existing rendering applies — or propose a new row for the
contract and wait for their decision. Never invent a rendering inline.

## Check the standards

Walk the contract's outbound standards against this piece (venue rules, no duplicate
bodies, rate discipline). Flag any violation to the user before assembling — a
disclosure does not license breaking venue rules.

## Assemble

Combine the draft with the rendering, verbatim, at its prescribed placement (header or
footer). Do not alter the draft's content in this step beyond the insertion.

## Approval gate

Present the assembled piece to the user in full and wait for explicit approval. Edits
requested by the user are applied and the piece is re-presented. Approved content is
handed back to the user (or the calling pipeline) — sending is not this skill's job.

## Record in the ledger

Only after the user confirms the piece was actually **sent** (approval alone is not
enough), append an entry to `modes/world-adoption/outbound/ledger.md` in the format the
contract prescribes.
