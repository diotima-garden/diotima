#!/usr/bin/env python3
"""
Extract learnable Spanish phrases from a YouTube video.

Usage:
    python3 .claude/skills/youtube-extract/extract.py <url> <context_file> [bias_hint]

Writes phrases to <context_file_dir>/youtube-phrases.txt and prints to stdout.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
from utils.llm_triggers import call_gemini_video

MODEL = "gemini-flash-latest"


def build_prompt(context: str, bias_hint: str | None) -> str:
    hint = f"\n\nAdditional focus: {bias_hint}" if bias_hint else ""
    return f"""You are analyzing a Spanish video to extract phrases worth learning for an Anki deck.

## Deck Context

{context}

## Your Task

Watch this video and extract Spanish phrases and sentences worth adding as Anki cards.
Output ONLY the raw Spanish phrases, one per line. No numbering, no prefixes, no commentary, no blank lines.

## Extraction Criteria

Select phrases that:
- Are natural, spoken Argentine Spanish (Rioplatense register)
- Contain reusable vocabulary, structure, or expressions (collocations, voseo forms, Argentine idioms, connectors)
- Match the level calibration in the deck context above
- Would make the learner think "I want to be able to say that"

Skip phrases that:
- Are too basic for the deck's current level
- Are proper-noun-heavy with no reusable structure
- Are isolated filler unlikely to generalize ("bueno", "dale", "okay")
- Repeat a structure already extracted from this video{hint}"""


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <url> <context_file> [bias_hint]", file=sys.stderr)
        sys.exit(2)

    url = sys.argv[1]
    context_file = pathlib.Path(sys.argv[2])
    bias_hint = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None

    deck_context = context_file.read_text()
    output_path = context_file.parent / "youtube-phrases.txt"

    prompt = build_prompt(deck_context, bias_hint)
    result = call_gemini_video(url, prompt, MODEL)

    output_path.write_text(result + "\n")
    print(result)


if __name__ == "__main__":
    main()
