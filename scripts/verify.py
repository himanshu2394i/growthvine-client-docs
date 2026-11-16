"""Check every number in a finished PDF/PPT against the confirmed inputs.

Usage:  python verify.py inputs.json document.pdf|document.pptx
Exit 0 = every figure traces back to the inputs, 1 = figures to check (listed).

A figure is accepted if it matches (to the precision it is printed at):
- a holding amount, an option total or the corpus,
- a sum of holdings grouped by any field or pair of fields (bucket, vehicle,
  asset class, liquidity, ...), per option,
- a summary-table cell or total in inputs.json,
- one of those as a % of its option total or of the corpus,
- a figure listed in "advisor_figures" (e.g. expected returns).
Plain decimals (table cells) may be in rupees, lakh, crore or %.
Integers without ₹ or % (page numbers, dates, step numbers) are ignored.
"""
import json
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

UNIT = {"cr": 1e7, "crore": 1e7, "l": 1e5, "lakh": 1e5}
SKIP_FIELDS = {"name", "amount", "percent", "source"}
TOKEN = re.compile(
    r"(?P<rupee>₹\s?(?P<rnum>\d[\d,]*(?:\.\d+)?)(?:\s?(?P<unit>Cr|crore|L|lakh)\b)?)"
    r"|(?P<pct>(?<![\d.])(?P<pnum>\d+(?:\.\d+)?)\s?%)"
    r"|(?P<plain>(?<![\d.,₹])\d+\.\d+(?!\d)(?!\s*(?:years?|yrs?|months?|days?|weeks?)\b))"
)


class Token:
    def __init__(self, text, kind, value, tolerance):
        self.text, self.kind, self.value, self.tolerance = text, kind, value, tolerance

    def __repr__(self):
        return f"Token({self.text!r}, {self.kind}, {self.value})"


def _half_step(num):
    """Half of the last printed decimal place: '1.20' -> 0.005, '70' -> 0.5."""
    decimals = len(num.split(".")[1]) if "." in num else 0
    return 0.5 * 10 ** -decimals


def tokens(text):
    out = []
    for m in TOKEN.finditer(text.replace(" ", " ")):
        if m.group("rupee"):
            num = m.group("rnum").replace(",", "")
            mult = UNIT[m.group("unit").lower()] if m.group("unit") else 1
            out.append(Token(m.group(0), "rupees", float(num) * mult, _half_step(num) * mult))
        elif m.group("pct"):
            num = m.group("pnum")
            out.append(Token(m.group(0), "percent", float(num), _half_step(num)))
        else:
            num = m.group("plain")
            out.append(Token(num, "plain", float(num), _half_step(num)))
    return out


def allowed(inputs):
    """(rupee values, percent values) that a document may show."""
    rupees, percents = set(), set()
    corpus = inputs.get("total")
    if corpus:
        rupees.add(corpus)
    for opt in inputs.get("options", []):
        hs = opt["holdings"]
        total = sum(h["amount"] for h in hs)
        option_values = {total, *(h["amount"] for h in hs)}
        fields = sorted({k for h in hs for k, v in h.items() if k not in SKIP_FIELDS and isinstance(v, str)})
        for group in [(f,) for f in fields] + list(combinations(fields, 2)):
            sums = defaultdict(float)
            for h in hs:
                sums[tuple(h.get(f) for f in group)] += h["amount"]
            option_values |= set(sums.values())
        rupees |= option_values
        for v in option_values:
            if total:
                percents.add(v / total * 100)
            if corpus:
                percents.add(v / corpus * 100)
    for t in inputs.get("tables", []):
        mult = {"rupees": 1, "lakh": 1e5, "crore": 1e7}[t.get("unit", "rupees")]
        nums = []
        for row in t["cells"].values():
            nums += list(row.values()) if isinstance(row, dict) else [row]
        nums += list(t.get("row_totals", {}).values()) + list(t.get("col_totals", {}).values())
        if "grand_total" in t:
            nums.append(t["grand_total"])
        rupees |= {n * mult for n in nums}
        percents |= set(t.get("row_percent", {}).values())
    for fig in inputs.get("advisor_figures", []):
        for tok in tokens(fig):
            (percents if tok.kind == "percent" else rupees).add(tok.value)
    return rupees, percents


def _near(value, pool, tol):
    return any(abs(value - p) <= tol + 1e-9 for p in pool)


def accepted(tok, rupees, percents):
    if tok.kind == "rupees":
        return _near(tok.value, rupees, tok.tolerance)
    if tok.kind == "percent":
        return _near(tok.value, percents, tok.tolerance)
    return (_near(tok.value, percents, tok.tolerance)
            or any(_near(tok.value * m, rupees, tok.tolerance * m) for m in (1, 1e5, 1e7)))


def pages(path):
    """Text per page/slide."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        import fitz
        with fitz.open(path) as doc:
            return [p.get_text() for p in doc]
    from pptx import Presentation
    out = []
    for slide in Presentation(path).slides:
        parts = []
        for sh in slide.shapes:
            if sh.has_text_frame:
                parts.append(sh.text_frame.text)
            if sh.has_table:
                parts += [c.text for r in sh.table.rows for c in r.cells]
            if sh.has_chart:
                for s in sh.chart.plots[0].series:
                    for i in range(len(list(s.values))):
                        dl = s.points[i].data_label
                        if dl.has_text_frame:
                            parts.append(dl.text_frame.text)
        out.append("\n".join(parts))
    return out


def check(inputs, document):
    rupees, percents = allowed(inputs)
    issues = []
    for n, text in enumerate(pages(document), 1):
        for tok in tokens(text):
            if not accepted(tok, rupees, percents):
                issues.append(f"'{tok.text}' on page {n} doesn't match anything in the confirmed inputs.")
    return issues


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print(__doc__)
        return 2
    inputs = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    issues = check(inputs, argv[1])
    if not issues:
        print("Every figure in the document matches the confirmed inputs.")
        return 0
    print(f"{len(issues)} figure(s) to check:")
    for i in issues:
        print(f"- {i}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
