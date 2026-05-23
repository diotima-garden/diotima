# Python Virtual Environments

When a subsystem needs third-party Python packages, use an isolated venv scoped to that subsystem. Never install packages system-wide or into the global Python.

## Pattern

```
<subsystem-dir>/
  .venv/          ← gitignored, must be reproduced after clone
  README.md       ← documents the one-time setup step
```

**Create and populate (one-time setup):**
```bash
python3 -m venv .claude/<subsystem>/.venv
.claude/<subsystem>/.venv/bin/pip install <package>
```

**Run scripts inside the venv:**
```bash
.claude/<subsystem>/.venv/bin/python3 <script.py>
```

**Run tests inside the venv:**
```bash
.claude/<subsystem>/.venv/bin/python3 -m pytest <tests/>
```

## Gitignore entry

Add a scoped entry to `.gitignore` — never a blanket `**/.venv/`:

```
# <Subsystem name> — venv (reproducible via README setup step)
.claude/<subsystem>/.venv/
```

## README requirement

Every subsystem with a venv must document the setup step in its README under a **Setup** section:

```markdown
## Setup

**Create the venv and install dependencies (one-time):**
\`\`\`
python3 -m venv .claude/<subsystem>/.venv
.claude/<subsystem>/.venv/bin/pip install <package>
\`\`\`

The venv is gitignored — run these commands after cloning or on a fresh machine.
```

## Checklist

- [ ] Venv lives at `<subsystem-dir>/.venv/`
- [ ] `.gitignore` has a scoped entry for this venv path
- [ ] README documents the one-time setup step
- [ ] Scripts invoke `.venv/bin/python3`, not bare `python3`
