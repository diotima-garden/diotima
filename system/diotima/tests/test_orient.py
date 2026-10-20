"""
orient.py: bank-content enrichment and git-status reporting on top of the
raw manifest. Each exit criterion in modes/meta/architect/grove_orientation.md
has a test here.

The empty-bank and clean-tree cases are deliberately asserted on the
*formatted* text, not just the dataclass -- the promise that an empty bank
or a clean tree reads as boring rather than broken lives entirely in
format_orientation(), since the data layer (populated_banks(), git_status)
is built to be lossy there by design.
"""
from pathlib import Path

import garden
from orient import format_orientation, orientation_for


def _write_manifest(grove: Path, banks: str = "") -> None:
    (grove / "DAFNE.md").write_text(
        "---\nformat: 0\n" + banks + "---\n\n# test grove\n"
    )


# --- bank content -------------------------------------------------------

def test_no_banks_declared(tmp_path):
    grove = tmp_path / "grove"
    grove.mkdir()
    _write_manifest(grove)

    o = orientation_for(grove)
    assert o.populated_banks == []
    assert "No grove-side memory captured yet" in format_orientation(o, grove)


def test_bank_declared_but_empty(tmp_path):
    grove = tmp_path / "grove"
    (grove / "memory").mkdir(parents=True)
    _write_manifest(grove, "banks:\n  - name: t\n    bank: ./memory\n")
    (grove / "memory" / "small-bank.md").write_text("")

    o = orientation_for(grove)
    assert o.populated_banks == []
    assert "No grove-side memory captured yet" in format_orientation(o, grove)


def test_bank_populated(tmp_path):
    grove = tmp_path / "grove"
    (grove / "memory").mkdir(parents=True)
    _write_manifest(grove, "banks:\n  - name: t\n    bank: ./memory\n")
    (grove / "memory" / "small-bank.md").write_text("## seeded session\ncontent here\n")

    o = orientation_for(grove)
    assert len(o.populated_banks) == 1
    bank_cfg, content = o.populated_banks[0]
    assert bank_cfg["name"] == "t"
    assert "seeded session" in content

    text = format_orientation(o, grove)
    assert "Populated mem-banks" in text
    assert "seeded session" in text
    assert "No grove-side memory captured yet" not in text


# --- private layer presence ------------------------------------------------
# Cases per modes/meta/architect/private_layer.md: absent, present-empty,
# present-populated -- the last asserts a distinctive filename and content
# never reach formatted output, only the count (presence, never content).

def test_no_private_dir(grove):
    o = orientation_for(grove)
    assert o.private.exists is False
    assert o.private.entry_count == 0

    text = format_orientation(o, grove)
    assert "Private layer: none yet" in text
    assert str(garden.private_root() / grove.name) in text


def test_private_dir_empty(grove):
    private_dir = garden.private_dir_for(grove)
    private_dir.mkdir(parents=True)

    o = orientation_for(grove)
    assert o.private.exists is True
    assert o.private.entry_count == 0

    text = format_orientation(o, grove)
    assert "Private layer:" in text
    assert "(empty)" in text
    assert "none yet" not in text


def test_private_dir_populated_reports_count_never_content(grove):
    private_dir = garden.private_dir_for(grove)
    private_dir.mkdir(parents=True)
    (private_dir / "therapy-notes-G.md").write_text(
        "G. Family -- patterns to watch, not cues\n"
    )
    (private_dir / "drafts").mkdir()
    (private_dir / "drafts" / "nested.md").write_text("more private content\n")

    o = orientation_for(grove)
    assert o.private.entry_count == 2   # counts the subdirectory itself, not its contents

    text = format_orientation(o, grove)
    assert "(2 entries)" in text
    assert "therapy-notes-G" not in text
    assert "patterns to watch" not in text.lower()
    assert "nested" not in text
    assert "more private content" not in text


# --- git status -----------------------------------------------------------

def test_dirty_tracked_file_appears(grove):
    (grove / "DAFNE.md").write_text("# fixture grove\nedited\n")

    o = orientation_for(grove)
    assert o.git_status is not None
    assert "uncommitted changes" in o.git_status
    assert "uncommitted changes" in format_orientation(o, grove)


def test_clean_tree_says_so_plainly(grove):
    o = orientation_for(grove)
    assert o.git_status is None
    assert "clean, up to date" in format_orientation(o, grove)


# --- CLI / hook parity ------------------------------------------------------

def _load_session_start():
    """session-start.py is hyphenated, so it's not plain-importable --
    load by file path, same as bank_union.load_mneme_main does for
    mneme's own hyphenated entry points."""
    import importlib.util

    path = Path(__file__).resolve().parent.parent / "session-start.py"
    spec = importlib.util.spec_from_file_location("diotima_session_start", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_matches_hook(grove, capsys):
    import orient as orient_module

    session_start = _load_session_start()
    hook_text = session_start.context_for(grove)

    orient_module.main(["--grove", str(grove)])
    cli_text = capsys.readouterr().out.rstrip("\n")

    assert cli_text == hook_text
