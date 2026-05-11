# `.claude/utils` — shared utilities

Thin helpers reused across hooks and skills. Scan this list before writing new helper code — if something fits, read the source (files are short).

| Module | What it provides |
|---|---|
| `log.py` | Project-wide standardized file logger |
| `llm_triggers.py` | `call_isolated` (Claude subprocess), `call_gemini` (Gemini text), `call_gemini_video` (Gemini + YouTube URL), `list_gemini_models` (model list), `probe_gemini_model` (availability check) |
| `session_crawler.py` | Read, parse, and pattern-match session transcripts; detect session mode |

## Import

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.log import make_logger
from utils.llm_triggers import call_isolated
from utils.session_crawler import read_transcript, detect_mode, matched_any
```
