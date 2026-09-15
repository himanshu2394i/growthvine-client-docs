"""Skill docs must encode cover clearance, page breaks, and a real logo file."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8").lower()


def test_cover_fingerprint_clears_stairs():
    text = _read("references/c-split.md") + _read("references/pdf-generation.md")
    assert "arcs-slot" in text or "clip" in text
    assert "12mm" in text or "16mm" in text
    assert "920px" in text
    assert "stair" in text
    assert "overlap" in text or "clearance" in text or "gap" in text


def test_page_breaks_are_specified():
    text = _read("references/pdf-generation.md")
    assert "page-break-after: always" in text
    assert "one chapter" in text
    assert "pin" in text and "flow" in text
    assert "cover" in text


def test_logo_assets_and_cover_placement():
    tokens = _read("references/design-tokens.md")
    skill = _read("SKILL.md")
    assert "cover" in tokens and "logo" in tokens
    assert (ROOT / "assets" / "gv-mark.svg").is_file()
    assert (ROOT / "assets" / "logo-inverse.png").is_file()
    assert (ROOT / "assets" / "fp-arcs.svg").is_file()
    assert "gv-mark.svg" in skill or "gv-mark.svg" in tokens


def test_kit_says_what_is_executable():
    skill = _read("SKILL.md")
    assert "charts.py" in skill
    assert "donut" in skill and "waffle" in skill
    assert "chart_svg" in _read("scripts/charts.py")
    figures = _read("references/figures.md")
    assert "paired bar" in figures or "pair-bars" in figures
    assert "riskometer" in figures
    assert "cy-strip" in figures or "calendar" in figures


if __name__ == "__main__":
    test_cover_fingerprint_clears_stairs()
    test_page_breaks_are_specified()
    test_logo_assets_and_cover_placement()
    test_kit_says_what_is_executable()
    print("test_print_rules.py passed")
