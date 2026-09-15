"""Growthvine brand chart primitives: the two components that aren't a standard
chart type in any print/slide library. Direct port of the same math the web
prototypes use (mock-core.js's donutSvg/hundred) — draw it the same way here so a
donut in a PDF matches what's already been shown and approved, not a fresh
reinterpretation.

No dependencies. Usage: see SKILL.md and references/pdf-generation.md /
references/pptx-generation.md for how the output gets into an actual document.
"""
import math

# Growthvine brand palette (frontend/home-app/src/prototypes/mockFunds.js /
# Growthvine Brandbook.pdf) — see references/design-tokens.md for RGB/CMYK too.
COLORS = {
    "indigo": "#9B81F5",
    "ink": "#1D1D1B",
    "white": "#FFFFFF",
    "mint": "#B1F0DB",
    "peach": "#FFBB90",
    "mustard": "#F1F68E",
}

Slice = tuple  # (label: str, value: float, color: str) — kept loose deliberately;
# a Slice is whatever the caller's data already looks like, no schema to import.


def donut_svg(slices, width=7, gap=0.6, size=160):
    """Ring chart as an <svg> string, viewBox "0 0 42 42".

    Stacks stroke-dasharray'd circles on a r=15.915 circle — that radius makes the
    circumference come out to ~100 units, so each segment's dash length is just its
    percentage of the total, no circumference math per call. `gap` (in the same 0-100
    units) trims a sliver off each segment so adjacent slices show a hairline
    separation instead of touching.

    slices: iterable of (label, value, hex_color). Values need not sum to 100 —
        they're normalized against their own total, matching donutChart() in
        frontend/fund-logic.js (a partial split still reads honestly as a ring that
        doesn't fully close, rather than being stretched to fake 100%).
    size: rendered pixel size (the SVG is square). Rasterize at 3-4x this for print.
    """
    total = sum(value for _, value, _ in slices) or 1
    at = 0.0
    circles = []
    for _, value, color in slices:
        length = (value / total) * 100
        dash = max(length - gap, 0.2)
        offset = 25 - at  # start at 12 o'clock, advance clockwise
        circles.append(
            f'<circle cx="21" cy="21" r="15.915" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-dasharray="{dash:.2f} {100 - dash:.2f}" '
            f'stroke-dashoffset="{offset:.2f}"/>'
        )
        at += length
    inner = "".join(circles)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 42 42" width="{size}" height="{size}">{inner}</svg>'


def waffle_cells(slices):
    """A flat list of exactly 100 hex colors (one per 1%-cell), largest-remainder
    rounded so the 100 cells always account for the true total even when the raw
    percentages don't divide evenly (58.4/36.2/5.4 floors to 58/36/5 = 99 — the
    leftover cell goes to whichever slice had the largest fractional remainder,
    here Equity's .4, not to whichever slice happens to be listed first).

    slices: iterable of (label, value, hex_color).
    Render as a 10x10 or 20x5 CSS/SVG grid, one square per returned color.
    """
    total = sum(value for _, value, _ in slices) or 1
    raw = [(value / total) * 100 for _, value, _ in slices]
    counts = [math.floor(v) for v in raw]
    remainder = 100 - sum(counts)
    order = sorted(range(len(raw)), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[:remainder]:
        counts[i] += 1
    cells = []
    for (_, _, color), n in zip(slices, counts):
        cells.extend([color] * n)
    return cells


def _demo():
    """Runnable self-check — the waffle rounding has a branch and a loop, so it gets
    one. `python charts.py` runs this."""
    slices = [
        ("Equity", 58.4, COLORS["indigo"]),
        ("Debt", 36.2, COLORS["ink"]),
        ("Other", 5.4, COLORS["peach"]),
    ]
    cells = waffle_cells(slices)
    assert len(cells) == 100, f"waffle must always total 100 cells, got {len(cells)}"
    # 58.4/36.2/5.4 floors to 58/36/5 = 99, one cell short - some slice must get the
    # leftover. Which one is a floating-point near-tie between Equity and Other (their
    # remainders differ by ~5e-16), so this only asserts the invariant that matters:
    # every slice still gets its floor at minimum, and the total is exactly 100.
    assert cells.count(COLORS["indigo"]) in (58, 59)
    assert cells.count(COLORS["ink"]) == 36, "Debt's .2 remainder is clearly smallest, it never gets the extra cell"
    assert cells.count(COLORS["peach"]) in (5, 6)
    assert cells.count(COLORS["indigo"]) + cells.count(COLORS["peach"]) == 64, "the one leftover cell goes to exactly one of Equity/Other"

    # A case with no near-tie, to show the remainder logic unambiguously: floors to
    # 70+20+9=99, remainders .7/.2/.1 aren't close, so Equity must win outright.
    clear = [("Equity", 70.7, COLORS["indigo"]), ("Debt", 20.2, COLORS["ink"]), ("Other", 9.1, COLORS["peach"])]
    clear_cells = waffle_cells(clear)
    assert len(clear_cells) == 100
    assert clear_cells.count(COLORS["indigo"]) == 71, "largest remainder (.7) gets the one leftover cell"
    assert clear_cells.count(COLORS["ink"]) == 20
    assert clear_cells.count(COLORS["peach"]) == 9

    uneven = [("A", 33.33, COLORS["indigo"]), ("B", 33.33, COLORS["mint"]), ("C", 33.34, COLORS["peach"])]
    assert len(waffle_cells(uneven)) == 100, "must total 100 even on a three-way near-even split"

    svg = donut_svg(slices)
    assert svg.count("<circle") == 3, "one <circle> per slice"
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 42 42"')

    print("charts.py self-check passed")
    print(f"\nSample donut SVG ({len(slices)} slices):\n{donut_svg(slices, size=200)}")


if __name__ == "__main__":
    _demo()
