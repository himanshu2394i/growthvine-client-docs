# Data rules

## Sources, in order of authority

1. **The advisor** (answers, files, comments). Final word. Locked.
2. **Growthvine fund data (MCP)**: supports the advisor's data, for funds and
   categories it covers. Never overrides.
3. Nothing else. No figures from memory or general knowledge.

## The rules

1. **Locked data.** Copy the advisor's numbers exactly. No rounding to "look
   cleaner" (12.73% stays 12.73%). Lakh/crore format as the advisor wrote it.
2. **MCP conflicts with the advisor:** advisor wins; mention the gap in chat.
3. **Missing data** (common: AIF, PMS, SIF, MLD / structured products are usually
   not in the MCP). For each such holding, ask the advisor to pick:
   - provide the figures (paste, file or factsheet),
   - show an empty "to be added" table,
   - leave it out of data pages, with a one-line honest note.
   Never guess. Never put "N/A" inside a chart.
4. **Mismatched inputs:** run the reconcile check (`check/CHECK.md`, part A) and
   ask about every issue it finds.
5. **Not enough information:** ask. This includes what a bucket is for: use only
   what the advisor's inputs say.
6. **Dates:** every page with returns, NAV, ranks or holdings shows its as-of date.
   If sources have different dates, the page says so.
7. **Forecasts:** only the advisor's own figures, with a not-a-guarantee note,
   never on the cover.

## Growthvine fund data (MCP): use it fully

The fund data is the backbone of a rich document, not a footnote. A fund-level
proposal should use it for every holding it covers: profile, returns vs the
market, risk, cost, holdings, look-through, overlap and growth charts.

If the MCP isn't connected, say so at the start and offer to continue with the
advisor's data only.

**Use the v3 tools only.** The older tools (`search_schemes`, `get_fund_details`,
`get_fund_holdings`, `compare_funds`, `get_nav_history*`, `get_benchmark_history`,
`get_data_freshness`, ...) are frozen and being removed. Call
`get_analysis_guide` once before any derived maths.

| Need | v3 tool |
|---|---|
| Find a fund by name | `find_funds(q="<distinctive words>", filters={"plan": "regular", "option": "growth"})` |
| Everything about one fund | `get_fund(scheme_id, include=["profile", "returns", "risk", "factsheet", "allocation", "portfolio"])` |
| Several funds side by side | `find_funds(ids=[...], include=["returns", "risk", "factsheet"])` (never loop) |
| Monthly NAV for many funds | `get_fund_history(type="nav", scheme_ids=[...], interval="month", from_date="<5+ years ago>")` |
| Market index (Nifty 500 TRI, Nifty 50 TRI, daily since 2001) | `list_benchmark_series(kind=["tri"])`, then `get_benchmark_series(name=..., kind="tri", from_date=...)` |
| "Typical for this category" | `summarize_funds(filters={"category": ..., "plan": "regular"}, stats=[...])` |
| Rank in category | `find_funds(filters={"ranking_category": ..., "plan": ...}, sort="rank_in_category")` |
| How fresh is this? | `get_freshness` |

**Plan:** v3 rows say `plan` (`regular` / `direct`) and `option` (`growth` /
`idcw...`) directly. Use the plan the advisor confirmed (QUESTIONS.md C4) and
tell them which plan you resolved for each fund.

**What `get_fund` gives you** (all per fund, use it): `returns` (1m, 3m, 6m,
1y, 3y, 5y, 10y, SIP returns, rank and quartile in category, `returns_date`),
`risk` (std dev = typical yearly swing, max drawdown 3y/5y with peak and trough
dates, days to recover, up/down capture, Sharpe, holdings count, top-10 share),
`factsheet` (manager, objective, exit load, expense ratio, AUM, minimum),
`allocation` (equity/debt/cash and large/mid/small split), `portfolio`
(every holding with ISIN, sector and weight; sector weights).

**Reading the data correctly** (learned from test runs):
- NSE index factsheets are dated the 1st of the month after the data: the
  factsheet dated 1 Oct 2026 holds **September** figures. Label the month the
  figures cover, not the factsheet date.
- `summarize_funds` averages for alpha, beta, Sortino, P/E and similar can count
  new funds as 0 (their `count` equals the number of funds). Use the median for
  those, and check `count` before quoting any average.
- `get_fund_history(type="rolling")` gives monthly points already; only `nav`
  takes `interval="month"`.
- Holdings history lists only dates when something changed; `removed: true`
  marks a full exit. An ISIN change for the same company is not a sale.
- `find_funds(format="csv")` ignores `limit` and returns the whole match.

## Calculations: `scripts/analyse.py`

Scripts can't call the MCP, so save each response as a file in a `data/`
folder, then let `analyse.py` do the maths (format in its docstring):

1. `get_fund(...)` per fund → `data/fund_<scheme_id>.json`
2. One `get_fund_history(type="nav", interval="month", ...)` for all funds →
   `data/nav.json`
3. `get_benchmark_series("Nifty 500 TRI", kind="tri", from_date=...)` →
   `data/index.json`
4. Write `data/request.json` (funds with label, scheme_id, amount, file; nav;
   index; projection from the advisor's rates) and run
   `python scripts/analyse.py data/request.json`.

It returns: look-through (companies and sectors owned through the funds,
weighted by the money in each), overlap
between every pair of funds, returns for each fund **and the index measured to
the same end date** (index data often ends earlier than NAVs; never compare
across different dates), growth of ₹1 lakh for a line chart, and projections.
Copy its `fund_data` block into `inputs.json` so the number check accepts every
calculated figure. Use its numbers as given; don't recompute by hand.

**Use the CSV exports.** They're 3-4 times smaller than JSON and can be pasted
into a file as-is:
- `find_funds(ids=[...], include=["returns", "risk", "factsheet", "allocation"], format="csv")`:
  one row per fund with every flat field (returns, drawdowns, swing, cost,
  manager, exit load, market-cap split, asset mix) → `data/funds.csv`.
- `get_fund_history(type="holdings", scheme_ids=[...], from_date="<about a month ago>", format="csv")`:
  every holding of every fund → `data/holdings.csv` (analyse.py keeps the
  latest date per fund and drops sold rows).
- `get_fund_history(type="nav", scheme_ids=[...], interval="month", from_date=..., format="csv")`
  → `data/nav.csv`.
- `get_benchmark_series(..., kind="tri", format="csv")` → month-end rows in
  `data/index.csv`.
CSV answers are capped at 1,000 rows for an agent; split by date range or by
funds when a call would exceed that. In `request.json` point to them with
`funds_csv`, `holdings_csv`, `nav_csv`, `index`.

**If you use JSON instead (keep it small, it's re-typed into files):**
- Per fund, save only what the pages and maths use: `returns`, `risk`,
  `factsheet`, `allocation`, `profile` name/category/inception, and
  `portfolio.holdings` filtered to **equity rows with an ISIN** (isin, name,
  sector, weight_pct). Skip cash, bonds and derivative lines.
- Index: the TRI series is daily and the tool returns at most 1,000 CSV rows;
  fetch in two date ranges if needed and save **month-end values only** (the last
  trading day of each month, plus the latest point). That matches the monthly
  NAVs and is all the maths needs.
- Very large responses may be saved to a file by the tool; read from that file
  instead of re-typing.

**Built into `analyse.py`, so say it in the document:**
- Returns for funds and the index are measured to the **latest date every series
  has** (e.g. 30 Sep when NAVs run to mid-November but the index stops in
  late October). Print that date on the scene.
- **Hedged funds** (long-short, arbitrage: listed shares far above net equity)
  are left out of look-through and overlap, because their shares mostly cancel
  out. They're named in `lookthrough.hedged_excluded`.

**Writing fund pages:** summarise long factsheet text (exit loads, objectives)
faithfully in plain words, keeping every number ("0.50% within 30 days, nil
after"). Every figure you write into explanation text (a market-cap split, a
worst fall, a yield) must come from the fund data and be recorded in `fund_data`.

Holdings that publish no portfolio (most PMS, AIF, MLD) are left out of
look-through and overlap automatically. Don't narrate that in the document. If the advisor
has those portfolios (often in their Excel), ask for them: they can be added to
the fund files in the same `portfolio.holdings` shape.

## Nulls and dates

Nulls on category-dependent fields are expected (valuation is equity-only; credit
and YTM are debt/hybrid). Not missing data; don't substitute.

Most SIFs, and new funds, have null returns: too new for a track record. Say
"New fund" rather than leaving a blank, and show what *is* known (manager,
size, cost, holdings, how it behaved since launch from its NAV).

Print the as-of date on every data scene: `returns_date` / `risk_date` /
`factsheet_date` from `get_fund`, the common end date from `analyse.py`, and
`get_freshness` for anything else. Collect them for the sources block on the
closing scene.
