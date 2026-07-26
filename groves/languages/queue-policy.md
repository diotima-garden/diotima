# Queue policy

Post-add scheduling rules for language decks. These are **declarative** — they describe
intended queue behavior *after* cards are pushed, and govern scheduling, not card content.
This file is deliberately **not** `#include`d into any deck spec, so it never enters the
generation context.

Execution is pending the grove-policy consumption mechanism (diotima#31). Until that
lands, this file is documentation, not enforced behavior.

## Idiom-batch cap

Idioms generated ahead of real exposure are low-ROI and interfere with each other in
review. When more than 3 cards tagged `vocab::idiom` or `vocab::expression` are added in
one batch, keep the first 3 active (input order) and suspend the rest; unsuspend each
reactively as you meet it in real context. The surplus is preserved, not discarded.

> Previously hardcoded in the generic card-add skill — the wrong home, since it would fire
> on non-language decks too. Relocated here during the add-cards decoupling.
