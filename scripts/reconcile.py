"""Cross-check an advisor's inputs before anything is built.

Usage:  python reconcile.py inputs.json
Exit 0 = no issues, 1 = issues printed (one plain-English line each).

inputs.json (write tables exactly as the documents state them; fix nothing):

{
  "total": 30000000,                         # corpus in rupees (optional)
  "options": [{
    "name": "Option 1", "source": "Options PDF",
    "stated_total": 30000000,                # optional
    "holdings": [{"name": "...", "vehicle": "MF", "asset_class": "Hybrid",
                  "amount": 2000000, "bucket": "Core Growth",
                  "percent": 6.7}]          # percent optional
  }],
  "tables": [{                               # summary tables the advisor gave
    "name": "Bucket x Vehicle", "source": "Plan PDF", "option": "Option 1",
    "unit": "lakh",                          # rupees | lakh | crore
    "rows": {"field": "bucket", "map": [...]},
    "cols": {"field": "vehicle", "map": [...]},   # or omit for a 1-D table
    "cells": {"Core Growth": {"MF": 60}},         # 1-D: {"Core Growth": 100}
    "row_totals": {...}, "col_totals": {...}, "grand_total": 300,
    "row_percent": {...}                     # % of grand total, optional
  }]
}

"map" rules translate a holding into the table's labels when the table groups
differently: [{"match": {"vehicle": "AIF"}, "to": "Alternatives"}]. First match
wins; no match = the holding's own field value. If a rule moves a holding away
from a label it states that the table also uses, that is reported as a conflict.
"""
import json
import sys

UNITS = {"rupees": 1, "lakh": 100000, "crore": 10000000}
PCT_TOL = 0.06      # percentages are usually shown to 1 decimal
TABLE_TOL = 0.051   # in the table's own unit, for 1-decimal tables
RUPEE_TOL = 1


def fmt(rupees):
    if abs(rupees) >= 10000000:
        return f"₹{rupees / 10000000:.2f} Cr"
    return f"₹{rupees / 100000:.1f} L"


def _issue(kind, message):
    return {"kind": kind, "message": message}


def _label(holding, axis):
    for rule in axis.get("map", []):
        if all(holding.get(k) == v for k, v in rule["match"].items()):
            return rule["to"]
    return holding.get(axis["field"])


def _check_option(opt, corpus):
    issues = []
    total = sum(h["amount"] for h in opt["holdings"])
    stated = opt.get("stated_total")
    if stated is not None and abs(total - stated) > RUPEE_TOL:
        issues.append(_issue("option_total",
            f"{opt['name']} ({opt['source']}) states a total of {fmt(stated)}, "
            f"but its holdings add up to {fmt(total)}."))
    if corpus is not None and abs(total - corpus) > RUPEE_TOL:
        issues.append(_issue("option_vs_corpus",
            f"{opt['name']} adds up to {fmt(total)}, but the total investment is {fmt(corpus)}."))
    for h in opt["holdings"]:
        if "percent" in h and total:
            actual = h["amount"] / total * 100
            if abs(actual - h["percent"]) > PCT_TOL:
                issues.append(_issue("holding_percent",
                    f"{h['name']} in {opt['name']} is shown as {h['percent']}%, "
                    f"but {fmt(h['amount'])} of {fmt(total)} is {actual:.1f}%."))
    return issues


def _check_table_internal(t):
    issues, two_d = [], "cols" in t
    cells = t["cells"]
    where = f"{t['name']} ({t['source']})"
    row_sums = {r: (sum(v.values()) if two_d else v) for r, v in cells.items()}
    for r, stated in t.get("row_totals", {}).items():
        if abs(row_sums.get(r, 0) - stated) > TABLE_TOL:
            issues.append(_issue("table_row_total",
                f"{where}: the {r} row totals {stated}, but its cells add up to {row_sums.get(r, 0):g}."))
    if two_d:
        for c, stated in t.get("col_totals", {}).items():
            got = sum(row.get(c, 0) for row in cells.values())
            if abs(got - stated) > TABLE_TOL:
                issues.append(_issue("table_col_total",
                    f"{where}: the {c} column totals {stated}, but its cells add up to {got:g}."))
    grand = sum(row_sums.values())
    if "grand_total" in t and abs(grand - t["grand_total"]) > TABLE_TOL:
        issues.append(_issue("table_grand_total",
            f"{where}: the grand total is {t['grand_total']}, but the cells add up to {grand:g}."))
    for r, pct in t.get("row_percent", {}).items():
        actual = row_sums.get(r, 0) / grand * 100 if grand else 0
        if abs(actual - pct) > PCT_TOL:
            issues.append(_issue("table_percent",
                f"{where}: {r} is shown as {pct}%, but it is {actual:.1f}% of the total."))
    return issues


def _check_table_vs_holdings(t, opt):
    issues, two_d = [], "cols" in t
    mult = UNITS[t.get("unit", "rupees")]
    where = f"{t['name']} ({t['source']})"
    row_labels = set(t["cells"]) | set(t.get("row_totals", {}))
    col_labels = set()
    if two_d:
        for row in t["cells"].values():
            col_labels |= set(row)
        col_labels |= set(t.get("col_totals", {}))

    computed = {}
    for h in opt["holdings"]:
        r = _label(h, t["rows"])
        c = _label(h, t["cols"]) if two_d else None
        for axis, got, labels in ((t["rows"], r, row_labels), ((t["cols"] if two_d else None), c, col_labels)):
            if axis is None:
                continue
            raw = h.get(axis["field"])
            if got not in labels:
                issues.append(_issue("label_not_in_table",
                    f"{h['name']} is '{got}' ({axis['field']}) in {opt['name']}, "
                    f"but {where} has no '{got}'. Where does it belong?"))
            elif raw != got and raw in labels:
                issues.append(_issue("label_conflict",
                    f"{h['name']} is '{raw}' ({axis['field']}) in {opt['name']} ({opt['source']}), "
                    f"but {where} counts it under '{got}'. Which is right?"))
        key = (r, c)
        computed[key] = computed.get(key, 0) + h["amount"]

    stated = {}
    for r, v in t["cells"].items():
        if two_d:
            for c, amt in v.items():
                stated[(r, c)] = amt * mult
        else:
            stated[(r, None)] = v * mult
    for key in sorted(set(stated) | set(computed), key=str):
        r, c = key
        if r not in row_labels or (two_d and c not in col_labels):
            continue  # already reported as label_not_in_table
        s, got = stated.get(key, 0), computed.get(key, 0)
        if abs(s - got) > TABLE_TOL * mult:
            cell = f"{r} / {c}" if two_d else r
            issues.append(_issue("table_vs_holdings",
                f"{where} says {cell} = {fmt(s)}, but {opt['name']}'s holdings add up to {fmt(got)}."))
    return issues


def check(data):
    issues = []
    options = {o["name"]: o for o in data.get("options", [])}
    for opt in options.values():
        issues += _check_option(opt, data.get("total"))
    for t in data.get("tables", []):
        issues += _check_table_internal(t)
        opt = options.get(t.get("option"))
        if opt is None:
            issues.append(_issue("unknown_option",
                f"{t['name']} ({t['source']}) is for '{t.get('option')}', which isn't one of the options."))
            continue
        issues += _check_table_vs_holdings(t, opt)
    return issues


def main(path):
    with open(path, encoding="utf-8") as f:
        issues = check(json.load(f))
    if not issues:
        print("No issues found.")
        return 0
    print(f"{len(issues)} issue(s) to check with the advisor:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue['message']}")
    return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
