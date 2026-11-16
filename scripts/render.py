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
}
COUNTS = {  # field: (min, max)
    "cover": {"facts": (1, 4)}, "stats": {"stats": (1, 4)}, "donut": {"slices": (2, 7)},
    "table": {"columns": (1, 8), "rows": (1, 11)}, "bars": {"series": (1, 3), "categories": (1, 8)},
    "timeline": {"stops": (2, 6)}, "steps": {"steps": (2, 5)},
}
LENGTHS = {"title": 90, "text": 160, "disclaimer": 900}


def validate(doc):
    errors = []
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
    render(doc, out)
    print(f"Rendered {len(doc['scenes'])} scenes to {out}")
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
