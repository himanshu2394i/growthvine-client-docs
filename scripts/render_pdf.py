"""PDF drawing for render.py (reportlab). Layout uses top-left coordinates;
`_y` flips them for reportlab, whose origin is bottom-left."""
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from render import (ASSETS, MARK, MARK_RATIO, shot_for, BAR, COLORS, CONTENT_BOTTOM, FOOT_Y, GREY, H, LINE, M,
                    MINT_TINT, NOTE_H, PEACH_TINT, SOFT, W, blend, is_numeric, palette,
                    to_number)

REG, SEMI = "Poppins", "Poppins-SemiBold"
INK, INDIGO, WHITE = COLORS["ink"], COLORS["indigo"], COLORS["white"]


def _fonts():
    if REG not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(REG, str(ASSETS / "fonts" / "Poppins-Regular.ttf")))
        pdfmetrics.registerFont(TTFont(SEMI, str(ASSETS / "fonts" / "Poppins-SemiBold.ttf")))


def _y(top):
    return H - top


_UNIT = re.compile(r"(?<=\d)\s+(?=(Cr|L|lakh|crore|years?|yrs?)\b)")


def keep_amounts(s):
    """Non-breaking space between a number and its unit, so '₹1.70 Cr' never splits."""
    return _UNIT.sub(" ", s)


def wrap(s, font, size, width):
    """Greedy line wrap on ordinary spaces only (reportlab's simpleSplit also
    breaks on non-breaking spaces, which would split amounts from units)."""
    lines, line = [], ""
    for word in keep_amounts(s).split(" "):
        trial = f"{line} {word}" if line else word
        if line and pdfmetrics.stringWidth(trial, font, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


class Page:
    def __init__(self, c, doc, n, total):
        self.c, self.doc, self.n, self.total = c, doc, n, total

    # --- primitives (top-left coordinates) ---
    def rect(self, x, y, w, h, fill, radius=0):
        self.c.setFillColor(HexColor(fill))
        if radius:
            self.c.roundRect(x, _y(y + h), w, h, radius, stroke=0, fill=1)
        else:
            self.c.rect(x, _y(y + h), w, h, stroke=0, fill=1)

    def text(self, x, y, s, size, font=REG, color=INK, align="left", spacing=0):
        """Single line; y is the top of the text."""
        c = self.c
        c.setFillColor(HexColor(color))
        base = _y(y + size * 0.82)
        if spacing:
            t = c.beginText()
            t.setFont(font, size)
            t.setCharSpace(spacing)
            width = pdfmetrics.stringWidth(s, font, size) + spacing * len(s)
            t.setTextOrigin(x - (width if align == "right" else 0), base)
            t.textLine(s)
            t.setCharSpace(0)  # char spacing persists in PDF text state otherwise
            c.drawText(t)
            return
        c.setFont(font, size)
        {"left": c.drawString, "right": c.drawRightString, "center": c.drawCentredString}[align](x, base, s)

    def para(self, x, y, s, width, size, font=REG, color=INK, leading=None, align="left"):
        """Wrapped text; returns the height used."""
        leading = leading or size * 1.45
        lines = wrap(s, font, size, width)
        for i, line in enumerate(lines):
            self.text(x if align == "left" else x + width, y + i * leading, line, size, font, color, align)
        return len(lines) * leading

    def image(self, name, x, y, h):
        img = ImageReader(str(ASSETS / "logos" / name))
        iw, ih = img.getSize()
        w = h * iw / ih
        self.c.drawImage(img, x, _y(y + h), w, h, mask="auto")
        return w

    def mark(self):
        x, y, h = shot_for(self.doc, self.n)
        self.c.drawImage(ImageReader(str(MARK)), x, _y(y + h), h * MARK_RATIO, h, mask="auto")

    # --- frames ---
    def dark(self):
        self.rect(0, 0, W, H, INK)
        self.mark()

    def counter(self, color):
        self.text(W - M, FOOT_Y, f"{self.n:02d} / {self.total:02d}", 8, REG, color, "right")

    def content_frame(self, s):
        """White scene with letterbox bars, header and footer. Returns content top."""
        self.rect(0, 0, W, H, WHITE)
        self.rect(0, 0, W, BAR, INK)
        self.rect(0, H - BAR, W, BAR, INK)
        top = 40
        if s.get("kicker"):
            self.text(M, top, s["kicker"].upper(), 9, SEMI, INDIGO, spacing=1.2)
            top += 20
        if s.get("as_of"):
            self.text(W - M, 42, s["as_of"], 8.5, REG, GREY, "right")
        top += self.para(M, top, s["title"], W - 2 * M - 150, 25, SEMI, INK, leading=31)
        lw = self.image("logo-light.png", M, FOOT_Y - 3, 13)
        footer = self.doc.get("meta", {}).get("footer", "")
        if footer:
            self.text(M + lw + 12, FOOT_Y, footer, 8, REG, GREY)
        self.counter(GREY)
        return top + 26

    def note(self, s):
        """Draw the note box if present; returns the bottom limit for content."""
        n = s.get("note")
        if not n:
            return CONTENT_BOTTOM
        y = CONTENT_BOTTOM - NOTE_H
        fill = PEACH_TINT if n.get("tone") == "caution" else MINT_TINT
        self.rect(M, y, W - 2 * M, NOTE_H, fill, radius=6)
        self.text(M + 20, y + 12, n.get("label", "").upper(), 8.5, SEMI, INK, spacing=1)
        self.para(M + 20, y + 28, n["text"], W - 2 * M - 40, 11, REG, INK, leading=15)
        return y - 18


# ---------- scenes ----------

def cover(p, s):
    p.dark()
    p.image("logo-dark.png", M, 44, 30)
    p.text(M, 150, s["eyebrow"].upper(), 11, SEMI, INDIGO, spacing=2)
    p.para(M, 172, s["title"], 640, 60, SEMI, WHITE, leading=66)
    h = p.para(M, 262, s["logline"], 560, 17, REG, SOFT, leading=26)
    p.rect(M, 262 + h + 18, 64, 3, INDIGO)
    facts = s["facts"]
    col = (W - 2 * M) / len(facts)
    for i, f in enumerate(facts):
        x = M + i * col
        p.text(x, 420, f["label"].upper(), 8.5, SEMI, SOFT, spacing=1)
        p.para(x, 438, f["value"], col - 16, 17, SEMI, WHITE, leading=22)
    meta = p.doc.get("meta", {})
    credit = " · ".join(v for v in (meta.get("rm") and f"Prepared by {meta['rm']}", meta.get("date")) if v)
    if credit:
        p.text(M, FOOT_Y, credit, 8.5, REG, SOFT)


def act(p, s):
    p.dark()
    p.text(M, 196, s["number"], 13, SEMI, INDIGO)
    p.rect(M + 30, 203, 48, 2, INDIGO)
    p.para(M, 222, s["title"], 640, 52, SEMI, WHITE, leading=58)
    width = 600
    lines = wrap(s["logline"], REG, 18, width)
    if len(lines) == 2 and len(lines[1].split()) <= 2:   # avoid a lonely last word
        width = pdfmetrics.stringWidth(s["logline"], REG, 18) / 2 + 40
    p.para(M, 296, s["logline"], width, 18, REG, SOFT, leading=27)
    p.counter(SOFT)


def statement(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    mid = top + (bottom - top) / 2 - 50
    p.rect(M, mid, 4, 96, INDIGO)
    h = p.para(M + 28, mid, s["text"], 700, 30, SEMI, INK, leading=40)
    if s.get("sub"):
        p.para(M + 28, mid + h + 14, s["sub"], 640, 14, REG, GREY, leading=21)


def stats(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    items = s["stats"]
    col = (W - 2 * M) / len(items)
    y = top + max(0, (bottom - top - 150) / 2)
    for i, st in enumerate(items):
        x = M + i * col
        p.rect(x, y, 28, 3, INDIGO)
        p.para(x, y + 22, st["value"], col - 24, 46 if len(items) < 4 else 38, SEMI, INK, leading=52)
        p.para(x, y + 90, st["label"], col - 36, 14, REG, GREY, leading=20)


def donut(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    slices = s["slices"]
    colors = palette(p.doc, [sl["label"] for sl in slices])
    r = min(130, (bottom - top) / 2 - 4)
    cx, cy = M + 150, top + (bottom - top) / 2
    total = sum(sl["value"] for sl in slices) or 1
    c, ang = p.c, 90.0
    c.setStrokeColor(HexColor(WHITE))
    c.setLineWidth(2.5)
    for sl in slices:
        ext = -360.0 * sl["value"] / total
        c.setFillColor(HexColor(colors[sl["label"]]))
        c.wedge(cx - r, _y(cy + r), cx + r, _y(cy - r), ang, ext, stroke=1, fill=1)
        ang += ext
    c.setFillColor(HexColor(WHITE))
    c.circle(cx, _y(cy), r * 0.58, stroke=0, fill=1)
    if s.get("center"):
        p.text(cx, cy - 12, s["center"], 19, SEMI, INK, "center")
    # legend
    x0, x1 = M + 360, W - M
    row = min(44, (bottom - top) / len(slices))
    y = cy - row * len(slices) / 2
    for sl in slices:
        p.rect(x0, y + row / 2 - 6, 12, 12, colors[sl["label"]], radius=2)
        p.text(x0 + 24, y + row / 2 - 8, sl["label"], 13, REG, INK)
        p.text(x1 - 90, y + row / 2 - 8, sl["display"], 13, SEMI, INK, "right")
        p.text(x1, y + row / 2 - 8, sl["share"], 13, REG, GREY, "right")
        p.rect(x0, y + row - 1, x1 - x0, 1, LINE)
        y += row


def table(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    cols, rows = s["columns"], [list(r) for r in s["rows"]]
    total = s.get("total")
    body = rows + ([total] if total else [])
    n = len(cols)
    width = W - 2 * M
    first = width * (0.32 if n > 3 else 0.45)
    rest = (width - first) / max(1, n - 1)
    widths = [first] + [rest] * (n - 1)
    numeric = [j > 0 and all(is_numeric(r[j]) for r in body) for j in range(n)]
    row_h = min(32, (bottom - top) / (len(body) + 1))
    size = 11 if row_h >= 28 else 10
    heat_max = max([to_number(r[j]) or 0 for r in rows for j in range(1, n) if numeric[j]] or [1]) or 1

    def cell(x, y, w, text, font, color, j):
        pad = 10
        if numeric[j]:
            p.text(x + w - pad, y + (row_h - size) / 2, text, size, font, color, "right")
        else:
            lines = wrap(text, font, size, w - 2 * pad)
            p.text(x + pad, y + (row_h - size) / 2, lines[0] if lines else "", size, font, color)

    y = top
    x = M
    p.rect(M, y, width, row_h, INK)
    for j, h in enumerate(cols):
        cell(x, y, widths[j], h, SEMI, WHITE, j)
        x += widths[j]
    y += row_h
    for r in rows:
        x = M
        for j, v in enumerate(r):
            if s.get("heat") and numeric[j] and j < n - (1 if cols[-1].lower() == "total" else 0):
                val = to_number(v)
                if val:
                    p.rect(x, y, widths[j], row_h, blend(WHITE, INDIGO, 0.1 + 0.5 * val / heat_max))
            cell(x, y, widths[j], str(v), SEMI if j == 0 else REG, INK, j)
            x += widths[j]
        p.rect(M, y + row_h - 1, width, 1, LINE)
        y += row_h
    if total:
        p.rect(M, y, width, row_h, MINT_TINT)
        x = M
        for j, v in enumerate(total):
            cell(x, y, widths[j], str(v), SEMI, INK, j)
            x += widths[j]


def bars(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    series, cats = s["series"], s["categories"]
    scolors = [INDIGO, INK, COLORS["peach"]][:len(series)]
    # legend
    x = W - M
    for name, col in reversed(list(zip(series, scolors))):
        w = 22 + len(name) * 6.5
        x -= w
        p.rect(x, top - 4, 10, 10, col, radius=2)
        p.text(x + 16, top - 6, name, 10, REG, INK)
        x -= 18
    top += 22
    label_w, val_w = 230, 90
    x0, x1 = M + label_w, W - M - val_w
    vmax = max(v for c in cats for v in c["values"]) or 1
    block = (bottom - top) / len(cats)
    bh = min(20, block * 0.72 / len(series))
    y = top
    for c in cats:
        group_h = bh * len(series) + 4 * (len(series) - 1)
        gy = y + (block - group_h) / 2
        p.para(M, gy + group_h / 2 - 9, c["label"], label_w - 20, 12.5, SEMI, INK, leading=16)
        for k, (v, d) in enumerate(zip(c["values"], c["display"])):
            by = gy + k * (bh + 4)
            bw = max(2, (x1 - x0) * v / vmax)
            p.rect(x0, by, bw, bh, scolors[k], radius=2)
            p.text(x0 + bw + 8, by + (bh - 11) / 2, d, 11, SEMI if k == 0 else REG, INK)
        y += block


def timeline(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    stops = s["stops"]
    gap = (W - 2 * M) / len(stops)
    line_y = top + max(50, (bottom - top - 190) / 2)
    p.rect(M + gap / 2, line_y - 1, gap * (len(stops) - 1), 2, LINE)
    for i, st in enumerate(stops):
        cx = M + gap * i + gap / 2
        p.text(cx, line_y - 40, f"{i + 1:02d}", 12, SEMI, INDIGO, "center")
        p.c.setFillColor(HexColor(INDIGO if i == 0 else INK))
        p.c.circle(cx, _y(line_y), 7, stroke=0, fill=1)
        lines = wrap(st["label"], SEMI, 18, gap - 24)
        for k, ln in enumerate(lines):
            p.text(cx, line_y + 26 + k * 24, ln, 18, SEMI, INK, "center")
        ty = line_y + 36 + len(lines) * 24
        for k, ln in enumerate(wrap(st["text"], REG, 13.5, gap - 28)):
            p.text(cx, ty + k * 20, ln, 13.5, REG, GREY, "center")


def steps(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    items = s["steps"]
    col = (W - 2 * M) / len(items)
    y = top + max(0, (bottom - top - 200) / 2)
    for i, st in enumerate(items):
        x = M + i * col
        p.rect(x, y, col - 28, 2, LINE)
        p.text(x, y + 18, f"{i + 1:02d}", 46, SEMI, INDIGO)
        h = p.para(x, y + 84, st["title"], col - 32, 19, SEMI, INK, leading=24)
        p.para(x, y + 92 + h, st["text"], col - 36, 14, REG, GREY, leading=20)


def text(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    y = top + 6
    for para in s["paragraphs"]:
        y += p.para(M, y, para, 700, 19, REG, INK, leading=30) + 18
        if y > bottom:
            break


def close(p, s):
    p.dark()
    p.image("logo-dark-tagline.png", M, 52, 44)
    p.para(M, 190, s["title"], 640, 52, SEMI, WHITE, leading=58)
    y = 262
    if s.get("rm"):
        p.text(M, y, s["rm"], 15, SEMI, WHITE)
        y += 26
    p.text(M, y, s["contact"], 14, REG, SOFT)
    p.para(M, 398, s["disclaimer"], 760, 8.5, REG, SOFT, leading=13)


DRAW = {"cover": cover, "act": act, "statement": statement, "stats": stats, "donut": donut,
        "table": table, "bars": bars, "timeline": timeline, "steps": steps, "text": text,
        "close": close}


def render(doc, out):
    _fonts()
    c = canvas.Canvas(str(out), pagesize=(W, H))
    meta = doc.get("meta", {})
    c.setTitle(f"Growthvine · {meta.get('client', '')}".strip(" ·"))
    c.setAuthor("Growthvine")
    scenes = doc["scenes"]
    for n, s in enumerate(scenes, 1):
        DRAW[s["type"]](Page(c, doc, n, len(scenes)), s)
        c.showPage()
    c.save()
