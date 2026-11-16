"""Tests for analyse.py. Run: python -m unittest discover -s scripts/tests"""
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import analyse  # noqa: E402


def h(isin, name, sector, w, instrument="Equity"):
    return {"isin": isin, "name": name, "sector": sector, "weight_pct": w, "instrument": instrument}


FUND_A = [h("I1", "ICICI Bank", "Banking", 10), h("I2", "Infosys", "IT", 5), h(None, "TREPS", "Cash", 3, "Trep")]
FUND_B = [h("I1", "ICICI Bank", "Banking", 4), h("I3", "Sun Pharma", "Pharma", 6)]


class LookThrough(unittest.TestCase):
    def test_weights_holdings_by_money(self):
        out = analyse.lookthrough({"A": 1000000, "B": 500000}, {"A": FUND_A, "B": FUND_B}, total=3000000)
        icici = next(c for c in out["companies"] if c["name"] == "ICICI Bank")
        self.assertAlmostEqual(icici["amount"], 100000 + 20000)       # 10% of 10 L + 4% of 5 L
        self.assertAlmostEqual(icici["pct_of_total"], 4.0)            # of the whole ₹30 L
        self.assertEqual(out["companies"][0]["name"], "ICICI Bank")   # biggest first

    def test_cash_is_not_a_company_and_coverage_is_reported(self):
        out = analyse.lookthrough({"A": 1000000, "C": 2000000}, {"A": FUND_A}, total=3000000)
        self.assertNotIn("TREPS", [c["name"] for c in out["companies"]])
        self.assertAlmostEqual(out["covered_amount"], 1000000)
        self.assertAlmostEqual(out["covered_pct"], 33.33, places=2)

    def test_sectors_as_share_of_covered_equity(self):
        out = analyse.lookthrough({"A": 1000000}, {"A": FUND_A}, total=1000000)
        sectors = {s["sector"]: s["pct"] for s in out["sectors"]}
        self.assertAlmostEqual(sectors["Banking"], 100 * 10 / 15)
        self.assertNotIn("Cash", sectors)


class HedgedFunds(unittest.TestCase):
    """Real-data finding: long-short/arbitrage funds list shares they've hedged away."""

    def test_hedged_fund_is_left_out_and_named(self):
        hedged = {"allocation": {"equity_pct": -0.33}, "holdings": [h("I1", "ICICI Bank", "Banking", 39.7)]}
        normal = {"allocation": {"equity_pct": 98}, "holdings": FUND_A}
        kept, excluded = analyse.unhedged({"A": normal, "H": hedged})
        self.assertEqual(list(kept), ["A"])
        self.assertEqual(excluded, ["H"])

    def test_fund_without_allocation_is_kept(self):
        kept, excluded = analyse.unhedged({"A": {"holdings": FUND_A}})
        self.assertEqual(list(kept), ["A"])
        self.assertEqual(excluded, [])


class Overlap(unittest.TestCase):
    def test_min_weight_overlap_on_shared_shares(self):
        self.assertAlmostEqual(analyse.overlap(FUND_A, FUND_B), 4.0)

    def test_matrix_and_summary(self):
        out = analyse.overlap_matrix({"A": FUND_A, "B": FUND_B, "C": [h("I9", "X", "Y", 50)]})
        self.assertEqual(out["labels"], ["A", "B", "C"])
        self.assertIsNone(out["matrix"][0][0])
        self.assertAlmostEqual(out["matrix"][0][1], 4.0)
        self.assertEqual(out["highest"]["pair"], ["A", "B"])
        self.assertAlmostEqual(out["average"], 4 / 3)


def series(start_year, years, start_value=100.0, yearly=0.10):
    """Month-end points growing `yearly` per year."""
    pts, v = [], start_value
    for m in range(years * 12 + 1):
        y, mo = start_year + m // 12, m % 12 + 1
        pts.append((date(y, mo, 28), start_value * (1 + yearly) ** (m / 12)))
    return pts


class Returns(unittest.TestCase):
    def test_cagr_and_simple_returns(self):
        r = analyse.period_returns(series(2020, 6), date(2026, 1, 28))
        self.assertAlmostEqual(r["1y"], 10.0, places=1)
        self.assertAlmostEqual(r["3y"], 10.0, places=1)       # annualised
        self.assertAlmostEqual(r["6m"], (1.1 ** 0.5 - 1) * 100, places=1)

    def test_too_short_history_is_none(self):
        r = analyse.period_returns(series(2025, 1), date(2026, 1, 28))
        self.assertIsNotNone(r["1y"])
        self.assertIsNone(r["3y"])

    def test_common_end_is_the_latest_date_every_series_has(self):
        # Real case: fund NAVs are month-ends to 13 Nov; the index is daily but stops 26 Oct.
        monthly = [(date(2026, 9, 30), 1.0), (date(2026, 10, 30), 1.0), (date(2026, 11, 13), 1.0)]
        daily = [(date(2026, 9, 29), 1.0), (date(2026, 9, 30), 1.0), (date(2026, 10, 26), 1.0)]
        self.assertEqual(analyse.common_end([monthly, daily]), date(2026, 9, 30))

    def test_month_end_shifts_land_on_month_ends(self):
        month_ends = [(date(2026, 3, 31), 100.0), (date(2026, 6, 30), 105.0), (date(2026, 9, 30), 110.0)]
        r = analyse.period_returns(month_ends, date(2026, 9, 30))
        self.assertAlmostEqual(r["6m"], 10.0)
        self.assertAlmostEqual(r["3m"], (110 / 105 - 1) * 100)


class Growth(unittest.TestCase):
    def test_growth_of_one_lakh(self):
        g = analyse.growth(series(2021, 5), date(2021, 1, 28), date(2026, 1, 28))
        self.assertAlmostEqual(g[0][1], 100000)
        self.assertAlmostEqual(g[-1][1], 100000 * 1.1 ** 5, delta=50)


class Projection(unittest.TestCase):
    def test_future_value_from_advisor_rate(self):
        p = analyse.project(30000000, "13.5%", 7)
        self.assertAlmostEqual(p, 30000000 * 1.135 ** 7)


class Formatting(unittest.TestCase):
    def test_rupees_and_percent(self):
        self.assertEqual(analyse.rupees(71234567), "₹7.12 Cr")
        self.assertEqual(analyse.rupees(450000), "₹4.5 L")
        self.assertEqual(analyse.pct(4.0), "4.0%")
        self.assertEqual(analyse.pct(-5.123, signed=True), "-5.1%")
        self.assertEqual(analyse.pct(2.3, signed=True), "+2.3%")


class EndToEnd(unittest.TestCase):
    def test_build_writes_figures_for_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "fund_A.json").write_text(json.dumps({"scheme_id": 1, "portfolio": {"holdings": FUND_A}}))
            (d / "fund_B.json").write_text(json.dumps({"scheme_id": 2, "portfolio": {"holdings": FUND_B}}))
            nav = {"data": [{"scheme_id": 1, "points": [{"date": str(d0), "nav": v} for d0, v in series(2020, 6)]},
                            {"scheme_id": 2, "points": [{"date": str(d0), "nav": v} for d0, v in series(2020, 6, yearly=0.05)]}]}
            (d / "nav.json").write_text(json.dumps(nav))
            idx = {"name": "Nifty 500 TRI", "points": [{"date": str(d0), "value": v} for d0, v in series(2020, 6, yearly=0.08)]}
            (d / "index.json").write_text(json.dumps(idx))
            request = {
                "total": 3000000,
                "funds": [{"label": "A", "scheme_id": 1, "amount": 1000000, "file": "fund_A.json"},
                          {"label": "B", "scheme_id": 2, "amount": 500000, "file": "fund_B.json"}],
                "nav": "nav.json", "index": "index.json",
                "projection": {"amount": 3000000, "rates": ["13.5%"], "years": [7]},
            }
            (d / "request.json").write_text(json.dumps(request))
            out = analyse.build(d / "request.json")
        self.assertEqual(out["returns"]["end_date"], "2026-01-28")
        self.assertIn("Nifty 500 TRI", out["returns"]["rows"])
        self.assertTrue(out["lookthrough"]["companies"])
        figures = [f for fd in out["fund_data"] for f in fd["figures"].values()]
        self.assertIn(analyse.rupees(3000000 * 1.135 ** 7), figures)
        self.assertIn("4.0%", figures)                     # A/B overlap


class SizeSplit(unittest.TestCase):
    """Real-data finding: an inline calculation treated a missing field as zero."""

    def test_weighted_by_equity_money(self):
        allocs = {"A": {"equity_pct": 100, "large_cap_pct": 40, "mid_cap_pct": 40, "small_cap_pct": 20},
                  "B": {"equity_pct": 50, "large_cap_pct": 80, "mid_cap_pct": 10, "small_cap_pct": 10}}
        out = analyse.size_split({"A": 1000000, "B": 1000000}, allocs)
        # A puts ₹10 L in shares, B ₹5 L: large = (4 + 4) / 15
        self.assertAlmostEqual(out["large"], 100 * 8 / 15)
        self.assertAlmostEqual(sum(out.values()), 100)

    def test_funds_missing_the_split_are_skipped_not_zeroed(self):
        allocs = {"A": {"equity_pct": 100, "large_cap_pct": 60, "mid_cap_pct": 30, "small_cap_pct": 10},
                  "B": {"equity_pct": 60}}
        out = analyse.size_split({"A": 1000000, "B": 2000000}, allocs)
        self.assertAlmostEqual(out["large"], 60)


class CsvInputs(unittest.TestCase):
    """MCP CSV exports pasted as-is: find_funds csv, holdings history csv, nav history csv."""

    FUNDS = "scheme_id,scheme_name,equity_pct,return_1y\n1,Fund A,98,10\n2,Hedged H,-0.3,9\n"
    HOLD = ("scheme_id,date,isin,name,instrument,sector,weight_pct,removed\n"
            "1,2026-10-14,I9,Old Co,Equity,IT,5,false\n"
            "1,2026-11-14,I1,ICICI Bank,Equity,Banking,10,false\n"
            "1,2026-11-14,I2,Infosys,Equity,IT,5,false\n"
            "1,2026-11-14,I3,Sold Co,,,,true\n"
            "1,2026-11-14,,TREPS,Trep,Cash,3,false\n"
            "2,2026-11-14,I1,ICICI Bank,Equity,Banking,40,false\n")
    NAV = "scheme_id,date,nav\n" + "".join(f"1,{d},{v}\n" for d, v in series(2020, 6))

    def test_build_from_csv_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "funds.csv").write_text(self.FUNDS)
            (d / "holdings.csv").write_text(self.HOLD)
            (d / "nav.csv").write_text(self.NAV)
            (d / "request.json").write_text(json.dumps({
                "total": 1500000,
                "funds": [{"label": "A", "scheme_id": 1, "amount": 1000000}, {"label": "H", "scheme_id": 2, "amount": 500000}],
                "funds_csv": "funds.csv", "holdings_csv": "holdings.csv", "nav_csv": "nav.csv"}))
            out = analyse.build(d / "request.json")
        names = [c["name"] for c in out["lookthrough"]["companies"]]
        self.assertEqual(names, ["ICICI Bank", "Infosys"])          # latest date only, no sold/cash rows
        self.assertEqual(out["lookthrough"]["hedged_excluded"], ["H"])
        self.assertIn("A", out["returns"]["rows"])


if __name__ == "__main__":
    unittest.main()
