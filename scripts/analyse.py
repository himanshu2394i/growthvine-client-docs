"""Turn saved Growthvine fund data (MCP v3 responses) into the figures a
proposal needs: look-through, overlap, returns vs an index on one common date,
growth of ₹1 lakh, and projections from the advisor's own rates.

Usage:  python analyse.py request.json [analysis.json]

MCP tools can't be called from here, so Claude saves each response as a file
next to request.json first:
  - one file per fund: get_fund(scheme_id, include=[profile, returns, risk,
    factsheet, allocation, portfolio])
  - nav.json: get_fund_history(type="nav", scheme_ids=[...], interval="month",
    from_date=<5+ years ago>)
  - index.json: get_benchmark_series(name="Nifty 500 TRI", kind="tri",
    from_date=...), JSON as returned (or CSV text "date,value").

request.json:
{
  "total": 30000000,                       # the whole investment, rupees
  "funds": [{"label": "Invesco India Large & Mid Cap", "scheme_id": 102053,
             "amount": 1000000, "file": "fund_102053.json"}],
  "nav": "nav.json", "index": "index.json", "index_name": "Nifty 500 TRI",
  "growth_years": 5,
  "projection": {"amount": 30000000, "rates": ["13.5%", "14.8%"], "years": [5, 7, 10]}
}

The output's "fund_data" goes straight into inputs.json so verify.py accepts
every calculated figure.
"""
import calendar
import json
import sys
from datetime import date, timedelta
from itertools import combinations
from pathlib import Path

PERIODS = {"1m": 1, "3m": 3, "6m": 6, "1y": 12, "3y": 36, "5y": 60}
STALE_DAYS = 15     # a price older than this before the target date doesn't count


# ---------- formatting ----------

def rupees(x):
    if abs(x) >= 1e7:
        return f"₹{x / 1e7:.2f} Cr"
    return f"₹{x / 1e5:.1f} L"


def pct(v, signed=False, decimals=1):
    s = f"{v:.{decimals}f}%"
    return ("+" + s) if signed and v > 0 else s


# ---------- holdings ----------

def _weight(hld):
    return hld.get("weight_pct", hld.get("allocation")) or 0


def _equity(holdings):
    return [x for x in holdings or [] if x.get("isin") and (x.get("instrument") or "").lower() == "equity"]


HEDGE_GAP = 10   # % points: listed shares this far above net equity = hedged


def unhedged(funds):
    """Split {label: {"allocation": {...}, "holdings": [...]}} into funds whose
    listed shares are really owned, and hedged funds (long-short, arbitrage)
    whose share list mostly cancels out against derivatives."""
    kept, excluded = {}, []
    for label, f in funds.items():
        gross = sum(_weight(x) for x in _equity(f.get("holdings")))
        net = (f.get("allocation") or {}).get("equity_pct")
        if net is not None and gross - net > HEDGE_GAP:
            excluded.append(label)
        else:
            kept[label] = f.get("holdings")
    return kept, excluded


def lookthrough(amounts, holdings, total):
    """Shares and sectors owned through the funds, weighted by the money in each.
    amounts: {label: rupees}; holdings: {label: [holding]} (missing = not published)."""
    companies, sectors = {}, {}
    covered = 0.0
    for label, amount in amounts.items():
        eq = _equity(holdings.get(label))
        if not eq:
            continue
        covered += amount
        for x in eq:
            money = amount * _weight(x) / 100
            c = companies.setdefault(x["isin"], {"name": x["name"], "amount": 0.0})
            c["amount"] += money
            sectors[x.get("sector") or "Other"] = sectors.get(x.get("sector") or "Other", 0.0) + money
    equity_money = sum(sectors.values()) or 1
    ranked = sorted(companies.values(), key=lambda c: -c["amount"])
    for c in ranked:
        c["pct_of_total"] = c["amount"] / total * 100
    return {
        "covered_amount": covered,
        "covered_pct": covered / total * 100,
        "companies": ranked,
        "sectors": sorted(({"sector": s, "pct": m / equity_money * 100} for s, m in sectors.items()),
                          key=lambda s: -s["pct"]),
    }


def size_split(amounts, allocations):
    """Large / mid / small share of the shares owned across the plan, weighted by
    the rupees each fund puts into shares. Funds without the split are skipped
    (never counted as zero)."""
    totals = {"large": 0.0, "mid": 0.0, "small": 0.0}
    for label, amount in amounts.items():
        a = allocations.get(label) or {}
        parts = [a.get(f"{k}_cap_pct") for k in totals]
        if any(v is None for v in parts) or not sum(parts):
            continue
        equity_money = amount * (a.get("equity_pct", 100) or 0) / 100
        for k, v in zip(totals, parts):
            totals[k] += equity_money * v / sum(parts)
    whole = sum(totals.values())
    return {k: v / whole * 100 for k, v in totals.items()} if whole else {}


def overlap(a, b):
    """% of one fund's money in the same shares as the other (min-weight overlap)."""
    wa = {x["isin"]: _weight(x) for x in _equity(a)}
    wb = {x["isin"]: _weight(x) for x in _equity(b)}
    return sum(min(wa[i], wb[i]) for i in wa.keys() & wb.keys())


def overlap_matrix(holdings):
    labels = [k for k, v in holdings.items() if _equity(v)]
    m = [[None] * len(labels) for _ in labels]
    pairs = []
    for i, j in combinations(range(len(labels)), 2):
        o = overlap(holdings[labels[i]], holdings[labels[j]])
        m[i][j] = m[j][i] = o
        pairs.append(([labels[i], labels[j]], o))
    highest = max(pairs, key=lambda p: p[1]) if pairs else None
    return {
        "labels": labels,
        "matrix": m,
        "average": sum(o for _, o in pairs) / len(pairs) if pairs else None,
        "highest": {"pair": highest[0], "pct": highest[1]} if highest else None,
    }


# ---------- prices ----------

def _shift(d, months):
    """Move back `months` months; from a month-end (day 26+) land on a month-end,
    so 30 Sep - 6 months is 31 Mar, matching month-end price series."""
    m = d.month - 1 - months
    y, m = d.year + m // 12, m % 12 + 1
    last = calendar.monthrange(y, m)[1]
    return date(y, m, last if d.day >= 26 else min(d.day, last))


def value_at(points, d):
    """Last value on or before d, if it's recent enough."""
    best = None
    for pd, v in points:
        if pd <= d:
            best = (pd, v)
        else:
            break
    if best and (d - best[0]).days <= STALE_DAYS:
        return best[1]
    return None


def common_end(series_list):
    """Latest date on which every series has a real (recent) value. NAVs may be
    month-ends to mid-November while the index stops in late October: the fair
    comparison date is then the last month-end both have."""
    series_list = [s for s in series_list if s]
    limit = min(s[-1][0] for s in series_list)
    candidates = sorted({d for s in series_list for d, _ in s if d <= limit}, reverse=True)
    for d in candidates:
        if all(value_at(s, d) is not None and _near_point(s, d) for s in series_list):
            return d
    return limit


def _near_point(points, d, days=3):
    return any(abs((pd - d).days) <= days for pd, _ in points)


def period_returns(points, end):
    """Simple % for periods up to a year, annualised (CAGR) beyond."""
    v1 = value_at(points, end)
    out = {}
    for key, months in PERIODS.items():
        start = _shift(end, months)
        v0 = value_at(points, start)
        if not v0 or not v1 or points[0][0] > start + timedelta(days=STALE_DAYS):
            out[key] = None
        elif months <= 12:
            out[key] = (v1 / v0 - 1) * 100
        else:
            years = (end - start).days / 365.25
            out[key] = ((v1 / v0) ** (1 / years) - 1) * 100
    return out


def growth(points, start, end, base=100000):
    v0 = value_at(points, start)
    out, d, k = [], start, 0
    while d <= end:
        v = value_at(points, d)
        if v is not None:
            out.append((d, base * v / v0))
        k += 1
        d = _shift(start, -k)
    if out and out[-1][0] != end and value_at(points, end) is not None:
        out.append((end, base * value_at(points, end) / v0))   # always end on the common date
    return out


def project(amount, rate, years):
    r = float(str(rate).strip().rstrip("%")) / 100
    return amount * (1 + r) ** years


# ---------- loading ----------

def _points(raw, key):
    pts = sorted((date.fromisoformat(p["date"]), float(p[key])) for p in raw if p.get(key) is not None)
    return pts


def _load_index(path):
    text = Path(path).read_text(encoding="utf-8").strip()
    if text.startswith("{"):
        data = json.loads(text)
        return data.get("name", "Index"), _points(data["points"], "value")
    rows = [line.split(",") for line in text.splitlines()[1:] if line.strip()]
    return "Index", sorted((date.fromisoformat(r[0]), float(r[-1])) for r in rows)


def _csv_rows(path):
    import csv
    with open(path, encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if not (r.get("scheme_id") or "").startswith("#")]


def _from_csv(folder, req, funds):
    """Fund data from MCP CSV exports: find_funds(format="csv") for the flat
    fields, get_fund_history(type="holdings", format="csv") for portfolios
    (latest date per fund; sold rows dropped)."""
    by_id = {f["scheme_id"]: f["label"] for f in funds if f.get("scheme_id") is not None}
    out = {label: {} for label in by_id.values()}
    if req.get("funds_csv"):
        for row in _csv_rows(folder / req["funds_csv"]):
            label = by_id.get(int(row["scheme_id"]))
            if label:
                out[label]["allocation"] = {k: float(row[k]) for k in
                                            ("equity_pct", "large_cap_pct", "mid_cap_pct", "small_cap_pct")
                                            if row.get(k) not in (None, "")}
    if req.get("holdings_csv"):
        rows = [r for r in _csv_rows(folder / req["holdings_csv"]) if r.get("removed", "false").lower() != "true"]
        latest = {}
        for r in rows:
            sid = int(r["scheme_id"])
            latest[sid] = max(latest.get(sid, ""), r["date"])
        for r in rows:
            sid = int(r["scheme_id"])
            label = by_id.get(sid)
            if label and r["date"] == latest[sid] and r.get("weight_pct"):
                out[label].setdefault("holdings", []).append(
                    {"isin": r.get("isin") or None, "name": r["name"], "instrument": r.get("instrument"),
                     "sector": r.get("sector"), "weight_pct": float(r["weight_pct"])})
    return out


def build(request_path):
    request_path = Path(request_path)
    folder = request_path.parent
    req = json.loads(request_path.read_text(encoding="utf-8"))
    total = req["total"]
    funds = req["funds"]
    data = {f["label"]: json.loads((folder / f["file"]).read_text(encoding="utf-8")) for f in funds if f.get("file")}
    if req.get("funds_csv") or req.get("holdings_csv"):
        data.update(_from_csv(folder, req, funds))
    holdings, hedged = unhedged({label: {"allocation": d.get("allocation"),
                                         "holdings": (d.get("portfolio") or {}).get("holdings") or d.get("holdings")}
                                 for label, d in data.items()})
    amounts = {f["label"]: f["amount"] for f in funds}

    out = {"lookthrough": lookthrough(amounts, holdings, total), "overlap": overlap_matrix(holdings)}
    out["lookthrough"]["hedged_excluded"] = hedged
    out["size_split"] = size_split({k: v for k, v in amounts.items() if k in holdings},
                                   {label: d.get("allocation") for label, d in data.items()})

    series = {}
    if req.get("nav"):
        nav = json.loads((folder / req["nav"]).read_text(encoding="utf-8"))
        by_id = {row["scheme_id"]: row["points"] for row in nav.get("data", [])}
        for f in funds:
            if f.get("scheme_id") in by_id:
                series[f["label"]] = _points(by_id[f["scheme_id"]], "nav")
    if req.get("nav_csv"):
        by_id = {}
        for row in _csv_rows(folder / req["nav_csv"]):
            by_id.setdefault(int(row["scheme_id"]), []).append(row)
        for f in funds:
            if f.get("scheme_id") in by_id:
                series[f["label"]] = _points(by_id[f["scheme_id"]], "nav")
    if req.get("index"):
        name, pts = _load_index(folder / req["index"])
        name = req.get("index_name", name)
        series[name] = pts
        index_name = name
    else:
        index_name = None

    if series:
        end = common_end(list(series.values()))
        rows = {label: period_returns(pts, end) for label, pts in series.items()}
        out["returns"] = {"end_date": end.isoformat(), "rows": rows, "index": index_name}
        years = req.get("growth_years", 5)
        start = _shift(end, 12 * years)
        out["growth"] = {"start": start.isoformat(), "end": end.isoformat(),
                         "series": {label: [(d.isoformat(), v) for d, v in growth(pts, start, end)]
                                    for label, pts in series.items()
                                    if value_at(pts, start) is not None}}

    proj = req.get("projection")
    if proj:
        out["projection"] = [{"rate": r, "years": y, "value": project(proj["amount"], r, y)}
                             for r in proj["rates"] for y in proj["years"]]

    out["fund_data"] = _figures(out)
    return out


def _figures(out):
    """Every calculated figure as the display string a scene would use."""
    as_of = out.get("returns", {}).get("end_date", "")
    src = "Calculated from Growthvine fund data"
    figs = {}
    lt = out["lookthrough"]
    figs["covered"] = rupees(lt["covered_amount"])
    figs["covered_pct"] = pct(lt["covered_pct"])
    for i, c in enumerate(lt["companies"][:10]):
        figs[f"company_{i}_amount"] = rupees(c["amount"])
        figs[f"company_{i}_pct"] = pct(c["pct_of_total"], decimals=2)
    for i, s in enumerate(lt["sectors"][:10]):
        figs[f"sector_{i}"] = pct(s["pct"])
    for k, v in out.get("size_split", {}).items():
        figs[f"size_{k}"] = pct(v, decimals=0)
    ov = out["overlap"]
    for i, row in enumerate(ov["matrix"]):
        for j, v in enumerate(row):
            if v is not None and j > i:
                figs[f"overlap_{i}_{j}"] = pct(v)
                figs[f"overlap_{i}_{j}_whole"] = pct(v, decimals=0)
    if ov["average"] is not None:
        figs["overlap_average"] = pct(ov["average"])
    for label, row in out.get("returns", {}).get("rows", {}).items():
        for k, v in row.items():
            if v is not None:
                figs[f"{label} {k}"] = pct(v)
    for label, pts in out.get("growth", {}).get("series", {}).items():
        if pts:
            figs[f"{label} growth end"] = rupees(pts[-1][1])
    for p in out.get("projection", []):
        figs[f"projection {p['rate']} {p['years']}y"] = rupees(p["value"])
    return [{"name": "Calculated figures", "source": src, "as_of": as_of, "figures": figs}]


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) not in (1, 2):
        print(__doc__)
        return 2
    out = build(argv[0])
    dest = Path(argv[1]) if len(argv) == 2 else Path(argv[0]).with_name("analysis.json")
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    lt = out["lookthrough"]
    print(f"Look-through covers {rupees(lt['covered_amount'])} ({pct(lt['covered_pct'])} of the money).")
    if out.get("returns"):
        print(f"Returns measured to {out['returns']['end_date']} for: {', '.join(out['returns']['rows'])}")
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
