# User Experience Principles

---

## The Standard

Pipelines are the user's primary interface. A clean run — no prompts, no errors,
no unexpected pauses — is the baseline expectation.
Pipelines rely on .claude/skills which are developt in this project, those shall run
smoothily as well.
Any deviation is a defect.

---

## When Something Is Rough

If a pipeline produces friction (prompts, errors, pauses), diagnose before patching:
1. Is it a missing allowlist entry?
2. Is it a path format issue (absolute vs. relative)?
3. Is it a command chaining issue?
4. Is it a genuine one-time setup step (leave it unwhitelisted)?

Propose the minimal fix. Don't over-whitelist.
