# context-compiler plugin

General-purpose preprocessor for resolving `#include` directives in markdown files, plus skills for compiling layered context into a single flat document.

## Subsystem files

| File | Role |
|---|---|
| `include_graph.py` | Shared `#include` graph traversal (`resolve_include_path`, `collect_inputs`) |
| `preprocess.py` | CLI preprocessor — resolves `#include` chains |
| `compiled-is-fresh.py` | Freshness check — exits 0 if compiled output is up-to-date |
| `skills/compile/` | LLM merge step — collapses preprocessed layers into one readable doc |
| `skills/compile-context/` | Orchestrator — freshness check → preprocess → compile |

## `#include` directive

```
#include <path>
```

- Must be the entire line, no leading whitespace.
- Path resolves relative to the **including file** when it starts with `.` or `..`; otherwise relative to the **project root**.

**Always put `#include` at the top of the file** — this preserves general → specific order in the output, which the compile merge step depends on.

## Deduplication and cycle detection

Each file is included at most once (keyed by canonical resolved path). Circular includes are an error.

## CLI

```bash
# Write to file
python3 .claude/plugins/context-compiler/preprocess.py <entry-file> <output-file>

# Print to stdout
python3 .claude/plugins/context-compiler/preprocess.py <entry-file>
```

## Skills

| Command | What it does |
|---|---|
| `/context-compiler:compile <preprocessed.md>` | LLM merge into `compiled.md` (fork context) |
| `/context-compiler:compile-context <deck>` | Full pipeline: freshness check → preprocess → compile |

## Notes

`include_graph.py` handles path resolution and input collection for both the preprocessor and the freshness check. If cross-directory includes are ever introduced, update `resolve_include_path` there — both tools pick up the change automatically.
