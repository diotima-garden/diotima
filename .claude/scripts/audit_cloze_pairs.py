#!/usr/bin/env python3
"""
Audit Spanish deck for redundant production+cloze pairs.

A cloze is REDUNDANT when:
  - It shares a fine-grained vocab tag with a production note, AND
  - The word it hides already appears verbatim in the production note's Back.

A cloze is DISTINCT when it tests:
  - Grammatical structure/choice (ser/estar, por/para, subjunctive, pronouns, tense)
  - Voseo forms
  - Argentine vocabulary
  - Fixed expressions or idioms

Prints a report grouping notes into: DELETE (redundant), KEEP (distinct), REVIEW.
"""

import json
import re
import html as html_lib
import urllib.request

ANKI_URL = "http://127.0.0.1:8765"

# Tags that signal a cloze is testing grammatical structure, not vocabulary
GRAMMAR_TAGS = {
    "grammar::ser_estar", "grammar::structure::ser_estar",
    "grammar::pronouns::direct", "grammar::pronouns::indirect",
    "grammar::pronouns::reflexive",
    "grammar::structure::para", "grammar::structure::por",
    "grammar::tense::subjunctive", "grammar::tense::conditional",
    "grammar::tense::imperfect", "grammar::tense::future",
    "grammar::structure::ir_a", "grammar::structure::comparatives",
    "grammar::structure::exclamatory", "grammar::structure::concessive",
    "grammar::structure::llevar_tiempo",
    "grammar::structure::al_plus_infinitive",
    "grammar::structure::voseo",
    "grammar::imperative", "grammar::modal_verbs::poder",
    "grammar::adjective_adverb::intensifier",
    "grammar::adjective::superlative",
    "grammar::irregular_verbs",
}

IDIOM_TAGS = {"vocab::idiom", "vocab::expression"}

def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, payload)
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data["result"]

def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return html_lib.unescape(s)

def extract_cloze_words(text):
    """Extract the hidden words from cloze syntax {{c1::word::hint}} → 'word'."""
    return re.findall(r"\{\{c\d+::([^:}]+)(?:::[^}]*)?\}\}", text)

def vocab_tags(tags):
    """Return the fine-grained vocab/grammar tags (not level, freq, cardtype)."""
    return {t for t in tags if t.startswith("vocab::") or t.startswith("grammar::")}

def has_grammar_tag(tags):
    return bool(set(tags) & GRAMMAR_TAGS)

def is_idiom(tags):
    return any(t.startswith("vocab::idiom") or t.startswith("vocab::expression")
               for t in tags)

# --- Fetch data ---
print("Fetching production notes...")
prod_ids = anki("findNotes", query="deck:Español tag:cardtype::production note:Production")
print(f"  {len(prod_ids)} production notes")

prod_data = anki("notesInfo", notes=prod_ids)

print("Fetching cloze notes...")
cloze_ids = anki("findNotes", query="deck:Español tag:cardtype::cloze")
print(f"  {len(cloze_ids)} cloze notes")

cloze_data = anki("notesInfo", notes=cloze_ids)

# --- Build lookup: vocab_tag → list of production notes ---
prod_by_tag = {}
for note in prod_data:
    for tag in note["tags"]:
        if tag.startswith("vocab::"):
            prod_by_tag.setdefault(tag, []).append(note)

# --- Analyse each cloze ---
DELETE  = []  # confirmed redundant
KEEP    = []  # clearly distinct
REVIEW  = []  # uncertain — no production pair found or ambiguous

for cloze in cloze_data:
    cid   = cloze["noteId"]
    text  = cloze["fields"]["Text"]["value"]
    tags  = cloze["tags"]
    clean = strip_html(text)
    hidden_words = [w.strip().lower() for w in extract_cloze_words(text)]

    # 1. Grammar-structure tag → KEEP
    if has_grammar_tag(tags):
        KEEP.append((cid, "grammar tag", clean[:80]))
        continue

    # 2. Idiom/expression → KEEP (expression is the primary test)
    if is_idiom(tags):
        KEEP.append((cid, "idiom/expression", clean[:80]))
        continue

    # 3. Try to find a production pair via shared vocab tag
    shared_vtags = [t for t in tags if t.startswith("vocab::")]
    paired_prods = []
    for vt in shared_vtags:
        paired_prods.extend(prod_by_tag.get(vt, []))

    if not paired_prods:
        REVIEW.append((cid, "no production pair found", clean[:80]))
        continue

    # 4. Check if any hidden word appears in any paired production back
    redundant = False
    matched_prod = None
    for prod in paired_prods:
        back = strip_html(prod["fields"]["Back"]["value"]).lower()
        for hw in hidden_words:
            # Match whole word (or word start for multi-word cloze)
            first_token = hw.split()[0]
            if re.search(r"\b" + re.escape(first_token) + r"\b", back):
                redundant = True
                matched_prod = prod
                break
        if redundant:
            break

    prod_front = (
        strip_html(matched_prod["fields"]["Front"]["value"])[:60]
        if matched_prod else "?"
    )
    cloze_short = clean[:70]

    if redundant:
        DELETE.append((cid, f"paired with: [{prod_front}]", cloze_short))
    else:
        REVIEW.append((cid, "pair found but word not in back", cloze_short))

# --- Report ---
print(f"\n{'='*70}")
print(f"REDUNDANT — DELETE ({len(DELETE)})")
print(f"{'='*70}")
for cid, reason, text in DELETE:
    print(f"  {cid}  |  {reason}")
    print(f"           cloze: {text}")

print(f"\n{'='*70}")
print(f"REVIEW — uncertain ({len(REVIEW)})")
print(f"{'='*70}")
for cid, reason, text in REVIEW:
    print(f"  {cid}  |  {reason}")
    print(f"           cloze: {text}")

print(f"\n{'='*70}")
print(f"KEEP — distinct knowledge ({len(KEEP)})")
print(f"{'='*70}")
for cid, reason, text in KEEP:
    print(f"  {cid}  |  {reason}")

print(f"\nSummary: {len(DELETE)} delete, {len(REVIEW)} review, {len(KEEP)} keep")
