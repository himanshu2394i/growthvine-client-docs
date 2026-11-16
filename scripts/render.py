"""Render scenes.json into a cinematic Growthvine PDF or PPT.

Usage:  python render.py scenes.json out.pdf|out.pptx [--preview DIR]
Exit 0 = rendered, 1 = scenes.json has problems (listed), 2 = bad arguments.

Format of scenes.json: design/SCENES.md. Shared brand + layout lives here;
drawing lives in render_pdf.py and render_pptx.py.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Page: 16:9 widescreen, in points. All layout below uses top-left origin.
W, H = 960, 540
M = 56            # side margin
BAR = 10          # letterbox bar height on content scenes
FOOT_Y = H - 36   # footer text line
CONTENT_BOTTOM = H - 64
NOTE_H = 58

COLORS = {
    "indigo": "#9B81F5", "ink": "#1D1D1B", "white": "#FFFFFF",
    "mint": "#B1F0DB", "peach": "#FFBB90", "mustard": "#F1F68E",
}
GREY = "#6B6B66"        # secondary text on white
SOFT = "#CFCFCA"        # secondary text on ink
LINE = "#E6E6E2"        # hairlines
PALETTE_ORDER = ["indigo", "mint", "peach", "mustard", "ink"]


def blend(a, b, t):
    """Mix hex colour a towards b by t (0..1)."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(pa, pb))


ARC = blend(COLORS["ink"], COLORS["indigo"], 0.2)     # mark colour on ink

# The official fingerprint G (assets/textures/mark-on-ink.png, already tinted ARC),
# cropped off the right edge of dark scenes. Each act card frames it differently,
# like a camera moving across it. Shots keep x >= 680 so text stays clear.
MARK = ASSETS / "textures" / "mark-on-ink.png"
MARK_RATIO = 1018 / 1200          # width / height of the image
SHOTS = {"cover": (620, -330, 720), "close": (680, -330, 700)}   # (x, y_top, height)
ACT_SHOTS = [(690, -60, 640), (700, 150, 600), (720, -320, 900), (680, -20, 560)]


def shot_for(doc, n):
    """Framing of the mark for scene n (1-based)."""
    kind = doc["scenes"][n - 1]["type"]
    if kind in SHOTS:
        return SHOTS[kind]
    acts_before = sum(1 for s in doc["scenes"][:n - 1] if s["type"] == "act")
    return ACT_SHOTS[acts_before % len(ACT_SHOTS)]
MINT_TINT = blend(COLORS["white"], COLORS["mint"], 0.45)
PEACH_TINT = blend(COLORS["white"], COLORS["peach"], 0.4)


def palette(doc, labels):
    """Colour per label: explicit doc palette first, then PALETTE_ORDER."""
    explicit = doc.get("palette", {})
    used = {explicit[l] for l in labels if l in explicit}
    spare = [c for c in PALETTE_ORDER if c not in used] or PALETTE_ORDER
    out, i = {}, 0
    for label in labels:
        if label in explicit:
            out[label] = COLORS[explicit[label]]
        else:
            out[label] = COLORS[spare[i % len(spare)]]
            i += 1
    return out


NUMERIC = re.compile(r"^[\s₹+\-–—.,%()0-9]*(L|Cr|lakh|crore)?[\s%]*$")


def is_numeric(cell):
    s = str(cell).strip()
    return s in {"-", "–", "—", ""} or (any(ch.isdigit() for ch in s) and bool(NUMERIC.match(s)))


def to_number(cell):
    try:
        return float(re.sub(r"[^\d.\-]", "", str(cell)))
    except ValueError:
        return None


def col_widths(columns, rows, total):
    """Column widths in proportion to their longest text, within limits, so a
    'Why' column gets room and a numbers column stays narrow."""
    n = len(columns)
    weights = []
    for j in range(n):
        cells = [str(r[j]) for r in rows] + [str(columns[j])]
        longest = max(len(c) for c in cells)
        numeric = j > 0 and all(is_numeric(r[j]) for r in rows)
        longest_word = max((len(w) for c in cells for w in c.split()), default=0)
        weights.append(max(min(max(longest, 6), 14 if numeric else 48), longest_word + 3))
    s = sum(weights)
    return [total * w / s for w in weights]


# ---------- validation ----------

REQUIRED = {
    "cover": ["eyebrow", "title", "logline", "facts"],
    "act": ["number", "title", "logline"],
    "statement": ["title", "text"],
    "stats": ["title", "stats"],
    "donut": ["title", "slices"],
    "table": ["title", "columns", "rows"],
    "bars": ["title", "series", "categories"],
    "timeline": ["title", "stops"],
    "steps": ["title", "steps"],
    "text": ["title", "paragraphs"],
    "close": ["title", "contact", "disclaimer"],
    "fund": ["title", "stats", "facts", "what"],
    "line": ["title", "x", "series"],
    "panels": ["title", "layout", "panels"],
}
LAYOUTS = {"2": 2, "3": 3, "2x2": 4, "1+2": 3, "2+1": 3}
PANEL_REQUIRED = {"bars": ["series", "categories"], "donut": ["slices"], "table": ["columns", "rows"],
                  "text": ["bullets"], "stack": ["segments"], "line": ["x", "series"], "stats": ["stats"],
                  "scatter": ["points", "x_label", "y_label"]}
GAP = 18


def bar_block(avail, n_cats, n_series):
    """Height per category in a bars panel: share the space, but never more than
    the bars need plus a small gap, so a few bars don't float apart."""
    return min(avail / n_cats, n_series * 14 + (n_series - 1) * 3 + 14)


def nice_ticks(lo, hi, target=4):
    """Round tick values (steps of 1, 2 or 5 x 10^k) covering lo..hi."""
    import math
    raw = (hi - lo) / target or 1
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 5, 10) if m * mag >= raw)
    t = math.ceil(lo / step) * step
    out = []
    while t <= hi + 1e-9:
        out.append(round(t, 10))
        t += step
    return out


def boxes(layout, top, bottom, left=M, right=W - M):
    """Panel rectangles (x, y, w, h) for a layout, inside the content area."""
    w, h = right - left, bottom - top
    half_w, half_h = (w - GAP) / 2, (h - GAP) / 2
    if layout == "2":
        return [(left, top, half_w, h), (left + half_w + GAP, top, half_w, h)]
    if layout == "3":
        tw = (w - 2 * GAP) / 3
        return [(left + i * (tw + GAP), top, tw, h) for i in range(3)]
    if layout == "2x2":
        return [(left + c * (half_w + GAP), top + r * (half_h + GAP), half_w, half_h) for r in (0, 1) for c in (0, 1)]
    big = w * 0.56
    small = w - big - GAP
    if layout == "1+2":
        return [(left, top, big, h), (left + big + GAP, top, small, half_h), (left + big + GAP, top + half_h + GAP, small, half_h)]
    if layout == "2+1":
        return [(left, top, small, half_h), (left, top + half_h + GAP, small, half_h), (left + small + GAP, top, big, h)]
    raise ValueError(f"Unknown layout '{layout}'")


def _strings(obj, path=""):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _strings(v, f"{path}[{i}]")
COUNTS = {  # field: (min, max)
    "cover": {"facts": (1, 4)}, "stats": {"stats": (1, 4)}, "donut": {"slices": (2, 7)},
    "table": {"columns": (1, 8), "rows": (1, 11)}, "bars": {"series": (1, 3), "categories": (1, 8)},
    "timeline": {"stops": (2, 6)}, "steps": {"steps": (2, 5)},
    "fund": {"stats": (1, 3), "facts": (1, 7)}, "line": {"series": (1, 5), "x": (2, 400)},
}
LENGTHS = {"title": 90, "text": 160, "disclaimer": 900, "what": 260, "watch": 220, "sources": 900}


def validate(doc):
    errors = []
    for where, scope in [("meta", doc.get("meta", {}))] + [(f"Scene {n}", s) for n, s in enumerate(doc.get("scenes", []), 1)]:
        for path, text in _strings(scope):
            if "·" in text:
                errors.append(f"{where}: don't use '·' as a separator ({path}: '{text[:50]}'). Use a comma or a new line.")
    for n, s in enumerate(doc.get("scenes", []), 1):
        where, kind = f"Scene {n}", s.get("type")
        if kind not in REQUIRED:
            errors.append(f"{where}: unknown type '{kind}'. Use one of: {', '.join(REQUIRED)}.")
            continue
        missing = [f for f in REQUIRED[kind] if f not in s]
        if missing:
            errors.append(f"{where} ({kind}): missing {', '.join(missing)}.")
            continue
        for field, (lo, hi) in COUNTS.get(kind, {}).items():
            if not lo <= len(s[field]) <= hi:
                errors.append(f"{where} ({kind}): {field} has {len(s[field])}; allowed {lo}-{hi}. "
                              f"Split it into more scenes or trim.")
        for field, cap in LENGTHS.items():
            if isinstance(s.get(field), str) and len(s[field]) > cap and not (kind == "cover" and field == "title"):
                errors.append(f"{where} ({kind}): {field} is {len(s[field])} characters; max {cap}.")
        if kind == "text" and sum(len(p) for p in s["paragraphs"]) > 700:
            errors.append(f"{where} (text): paragraphs exceed 700 characters in total.")
        if "note" in s and len(s["note"].get("text", "")) > 220:
            errors.append(f"{where}: note text is longer than 220 characters.")
        if kind == "table":
            width = len(s["columns"])
            for r, row in enumerate(s["rows"] + ([s["total"]] if "total" in s else []), 1):
                if len(row) != width:
                    errors.append(f"{where} (table): row {r} has {len(row)} cells but there are {width} columns.")
        if kind == "panels":
            need = LAYOUTS.get(s["layout"])
            if need is None:
                errors.append(f"{where} (panels): layout must be one of {', '.join(LAYOUTS)}.")
            elif len(s["panels"]) != need:
                errors.append(f"{where} (panels): layout {s['layout']} holds {need} panels, got {len(s['panels'])}.")
            if len(s.get("strip", [])) > 6:
                errors.append(f"{where} (panels): strip holds at most 6 numbers.")
            for i, pn in enumerate(s["panels"], 1):
                pk = pn.get("kind")
                if pk not in PANEL_REQUIRED:
                    errors.append(f"{where} panel {i}: unknown kind '{pk}'. Use one of: {', '.join(PANEL_REQUIRED)}.")
                    continue
                missing = [f for f in PANEL_REQUIRED[pk] if f not in pn]
                if missing:
                    errors.append(f"{where} panel {i} ({pk}): missing {', '.join(missing)}.")
        if kind == "line":
            for sr in s["series"]:
                if len(sr.get("values", [])) != len(s["x"]):
                    errors.append(f"{where} (line): '{sr.get('name')}' needs one value per x label "
                                  f"({len(s['x'])}), has {len(sr.get('values', []))}.")
        if kind == "bars":
            for c in s["categories"]:
                if not (len(c.get("values", [])) == len(c.get("display", [])) == len(s["series"])):
                    errors.append(f"{where} (bars): '{c.get('label')}' needs one value and one display per series.")
    if not doc.get("scenes"):
        errors.append("No scenes.")
    return errors


# ---------- entry points ----------

def render(doc, out):
    out = Path(out)
    errors = validate(doc)
    if errors:
        raise ValueError("\n".join(errors))
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() == ".pdf":
        import render_pdf
        render_pdf.render(doc, out)
    elif out.suffix.lower() == ".pptx":
        import render_pptx
        render_pptx.render(doc, out)
    else:
        raise ValueError(f"Output must end in .pdf or .pptx, not '{out.suffix}'.")
    return out


def preview(pdf_path, out_dir, dpi=60):
    """One PNG per page, for looking at the result."""
    import fitz
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, 1):
            p = out_dir / f"page-{i:02d}.png"
            page.get_pixmap(dpi=dpi).save(str(p))
            paths.append(p)
    return paths


SPARSE_BY_DESIGN = {"cover", "act", "statement", "close"}


def empty_space(pdf_path, doc, limit=0.3):
    """Content pages whose lower part is mostly blank, as messages to fix."""
    import fitz
    msgs = []
    with fitz.open(pdf_path) as pdf:
        for n, (page, s) in enumerate(zip(pdf, doc["scenes"]), 1):
            if s["type"] in SPARSE_BY_DESIGN:
                continue
            ys = [b[3] for b in page.get_text("blocks") if b[3] < CONTENT_BOTTOM]
            ys += [d["rect"].y1 for d in page.get_drawings()
                   if d["rect"].y1 < CONTENT_BOTTOM and d["rect"].height < H * 0.9]
            gap = (CONTENT_BOTTOM - max(ys, default=0)) / (CONTENT_BOTTOM - 110)
            if gap > limit:
                msgs.append(f"Scene {n} ('{s['title'][:50]}'): about {gap:.0%} of the page is empty at the bottom. "
                            "Add a strip of key numbers, a note, or another panel (e.g. a chart for the "
                            "same figures), merge it with the next page, or use a layout with more panels.")
    return msgs


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) not in (2, 4) or (len(argv) == 4 and argv[2] != "--preview"):
        print(__doc__)
        return 2
    src, out = Path(argv[0]), Path(argv[1])
    if out.suffix.lower() not in (".pdf", ".pptx"):
        print("Output must end in .pdf or .pptx.")
        return 2
    doc = json.loads(src.read_text(encoding="utf-8"))
    errors = validate(doc)
    if errors:
        print(f"{len(errors)} problem(s) in {src.name}:")
        for e in errors:
            print(f"- {e}")
        return 1
    try:
        render(doc, out)
    except ValueError as e:          # layout problems found while drawing
        print(f"1 problem in {src.name}:")
        print(f"- {e}")
        if out.exists():
            out.unlink()
        return 1
    print(f"Rendered {len(doc['scenes'])} scenes to {out}")
    if out.suffix.lower() == ".pdf":
        gaps = empty_space(out, doc)
        if gaps:
            print(f"{len(gaps)} page(s) with too much empty space (fill them before sending):")
            for g in gaps:
                print(f"- {g}")
    if len(argv) == 4:
        if out.suffix.lower() != ".pdf":
            print("Previews are made from PDFs; render a .pdf to preview.")
        else:
            for p in preview(out, argv[3]):
                print(f"Preview: {p}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main(sys.argv[1:]))
