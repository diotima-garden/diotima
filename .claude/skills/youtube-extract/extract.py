#!/usr/bin/env python3
"""
Extract learnable content from a YouTube video.

Usage:
    python3 extract.py <url> <context_file> [bias_hint]

Requires <context_file_dir>/focus_area.md — extraction criteria for the deck area.
Writes extracted content to <context_file_dir>/youtube-phrases.txt and prints to stdout.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
from utils.llm_triggers import call_gemini_video

MODEL = "gemini-flash-latest"


def build_prompt(focus_area: str, bias_hint: str | None) -> str:
    hint_section = f"\n\n## Additional Focus\n\n{bias_hint}" if bias_hint else ""
    return f"""Watch this video and extract content worth adding as Anki cards for the area described below.

Output ONLY the raw content, one per line. No numbering, no prefixes, no commentary, no blank lines.

## Extraction Focus

{focus_area}{hint_section}
"""


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <url> <context_file> [bias_hint]", file=sys.stderr)
        sys.exit(2)

    url = sys.argv[1]
    context_file = pathlib.Path(sys.argv[2])
    bias_hint = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None

    focus_area_path = context_file.parent / "focus_area.md"
    if not focus_area_path.exists():
        print(f"Error: focus_area.md not found at {focus_area_path}", file=sys.stderr)
        print("Create focus_area.md in the deck directory to define extraction criteria.", file=sys.stderr)
        sys.exit(1)
    focus_area = focus_area_path.read_text()

    output_path = context_file.parent / "youtube-phrases.txt"

    prompt = build_prompt(focus_area, bias_hint)
    result = call_gemini_video(url, prompt, MODEL)

    output_path.write_text(result + "\n")
    print(result)


if __name__ == "__main__":
    main()
