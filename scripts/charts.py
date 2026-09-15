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


def chart_svg(
    fund,
    bench=None,
    x_labels=None,
    *,
    width=720,
    height=280,
    area="#9B81F5",
    aria="Rolling returns",
):
    """Rolling line chart as an <svg> string, ported from mock-core.js `chartSvg`.

    fund: list of floats (one per month). bench: same length, or None / nulls where
    the index has no point. x_labels: optional 3 strings for start, mid, end.

    Solid Vine Indigo line + last-point circle. Index is a dashed Foundation Grey
    stroke. Optional indigo area fill under the fund (mock C split uses this).
    """
    n = len(fund)
    if n < 2:
        return '<p class="gv-empty">No rolling returns for this fund yet.</p>'
    bench = list(bench) if bench is not None else [None] * n
    if len(bench) != n:
        raise ValueError("bench must be the same length as fund")
    numeric = [v for v in fund if v is not None] + [v for v in bench if v is not None]
    lo, hi = min(numeric), max(numeric)
    pad = (hi - lo) * 0.12 or 1
    lo -= pad
    hi += pad
    p_l, p_r, p_t, p_b = 46, 18, 16, 30

    def x(i):
        return round(p_l + (i / (n - 1)) * (width - p_l - p_r), 1)

    def y(v):
        return round(p_t + (1 - (v - lo) / (hi - lo)) * (height - p_t - p_b), 1)

    def path(arr):
        pen, parts = "M", []
        for i, v in enumerate(arr):
            if v is None:
                pen = "M"
                continue
            parts.append(f"{pen}{x(i)} {y(v)}")
            pen = "L"
        return " ".join(parts)

    fund_d = path(fund)
    has_bench = any(v is not None for v in bench)
    bench_d = path(bench) if has_bench else ""
    last_i = n - 1
    area_d = f"{fund_d} L{x(last_i)} {height - p_b} L{x(0)} {height - p_b} Z"
    y_ticks = []
    for k in range(4):
        v = lo + ((hi - lo) * k) / 3
        y_ticks.append((y(v), f"{v:.1f}%"))
    if not x_labels:
        x_labels = ["", "", ""]
    x_ticks = [
        (x(0), x_labels[0] if len(x_labels) > 0 else "", "start"),
        (x(n // 2), x_labels[1] if len(x_labels) > 1 else "", "middle"),
        (x(last_i), x_labels[2] if len(x_labels) > 2 else "", "end"),
    ]
    gid = "a" + hex(abs(hash(fund_d)))[2:8]
    grid = "rgba(29,29,27,.08)"
    muted = "#6b6b69"
    y_lines = "".join(
        f'<line x1="{p_l}" x2="{width - p_r}" y1="{yy}" y2="{yy}" stroke="{grid}"/>'
        f'<text x="{p_l - 8}" y="{yy + 4}" text-anchor="end" font-size="11" fill="{muted}">{lab}</text>'
        for yy, lab in y_ticks
    )
    x_text = "".join(
        f'<text x="{xx}" y="{height - 8}" text-anchor="{anc}" font-size="11" fill="{muted}">{lab}</text>'
        for xx, lab, anc in x_ticks if lab
    )
    area_el = (
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{area}" stop-opacity=".3"/>'
        f'<stop offset="1" stop-color="{area}" stop-opacity="0"/></linearGradient></defs>'
        f'<path d="{area_d}" fill="url(#{gid})"/>'
        if area else ""
    )
    bench_el = (
        f'<path d="{bench_d}" fill="none" stroke="{COLORS["ink"]}" stroke-width="1.6" stroke-dasharray="5 5"/>'
        if bench_d else ""
    )
    return (
        f'<svg class="gv-chart" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="100%" role="img" aria-label="{aria}">'
        f"{area_el}{y_lines}{x_text}{bench_el}"
        f'<path d="{fund_d}" fill="none" stroke="{COLORS["indigo"]}" stroke-width="3.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{x(last_i)}" cy="{y(fund[last_i])}" r="5" fill="{COLORS["indigo"]}"/>'
        f"</svg>"
    )


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

    line = chart_svg([10, 14, 12, 16], [9, 13, 11, 15], ["Jan 2023", "Jun 2024", "Dec 2025"])
    assert "gv-chart" in line
    assert line.count("<path") >= 3, "area + dashed bench + fund line"
    assert 'stroke-dasharray="5 5"' in line
    assert "<circle" in line

    print("charts.py self-check passed")
    print(f"\nSample donut SVG ({len(slices)} slices):\n{donut_svg(slices, size=200)}")


if __name__ == "__main__":
    _demo()
