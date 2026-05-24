# Scalability: Authoring Skills and Pipelines

Read this when creating or modifying skills or pipelines.

See also: `.claude/rules/portability.md` — covers the related concern of path format in bash commands.

---

## No step numbers

Use descriptive section headers instead of numbered steps.

**Wrong:**
```markdown
## Step 1 — Resolve Deck
## Step 2 — Build Context
```

**Right:**
```markdown
## Resolve Deck
## Build Context
```

**Why:** Numbered steps require renaming every downstream heading whenever one is inserted or removed — a maintenance tax paid on every future edit.

---

## Pass context as arguments, not shared files

When a forked sub-skill needs context the caller has in memory, pass it inline as arguments rather than writing to a shared file.

**Wrong:**
```
Write context to .claude/tmp/shared-context.md
Invoke sub-skill with input only
# Sub-skill reads: !cat .claude/tmp/shared-context.md
```

**Right:**
```
Read the context file. Invoke sub-skill with all content inlined as arguments:
  - Context file content
  - Blank line
  - Dynamic sections + input
```

**Why:** Fixed-name shared files break under concurrent sessions. Passing context as arguments is stateless and parallel-safe. Do not pass file paths for the sub-skill to `!cat` — the permission system blocks `$(...)` command substitution inside `!` directives.
