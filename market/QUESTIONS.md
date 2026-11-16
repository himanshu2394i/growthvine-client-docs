# Market report: question set

A periodic note on markets for clients: what happened, how different parts of
the market did, what things cost now, and what it means for their plans. It
describes and explains; it never forecasts. Nothing here is a fixed template:
offer a deep menu, the advisor picks. **Always suggest more**.

**Required steps** (`SKILL.md`): basics, then the full section and subsection menu, then the storyboard, then build; each waits for the advisor.

## Step 1: the basics

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| 1 | Period covered (month, quarter, year to date) and the end date | Every figure is "to" a date | Pick + date | Yes |
| 2 | Who is it for? (all clients, a segment, internal) | Sets depth and language | Pick | Yes |
| 3 | Advisor's commentary or themes to include (flows, policy, events) | Market events and flows come only from the advisor | Their words, with sources | No |

## Step 2: pick sections, then subsections

**1. What happened**
- Headline indices over 1 month, 3 months, 1 year, 3 and 5 years
- Growth of ₹1 lakh in the broad market over 5 years
- *Go deeper:* month-by-month returns for the year

**2. Large, mid and small companies**
- Returns by company size, over 1 and 3 years
- How much each segment swings (yearly volatility)

**3. Sectors**
- Sector returns over 1 year, best to worst
- Sector returns over 3 and 5 years: this year's laggards in context
- What each sector costs (P/E)

**4. What things cost now**
- P/E, P/B and dividend yield by index
- P/E over 5 years for large, mid and small companies (line): cheap or dear
  against their own history
- *Go deeper:* the gap between small and large company valuations over time

**5. Bonds**
- 10-year government bond yield over the year
- Yields by bond length today (91-day T-bill to 15 years and above)
- Returns by bond length over the year: why longer bonds moved more
- Duration in plain words

**6. Fund categories** (optional)
- How fund categories did over the period (`summarize_funds(group_by=["category"])`)

**7. What it means for you**
- Practical notes for share and bond investors; the advisor's themes
- What we're watching (describe, never predict)

## Data to fetch

- `get_benchmark_series(name, kind="equity", from_date=<5 years ago>, format="csv")`
  for each index chosen (NIFTY 50, NIFTY 500, NIFTY Midcap 150, NIFTY Smallcap
  250, sector indices): monthly returns, volatility, P/E, P/B, dividend yield
- `get_benchmark_series(name, kind="fixed_income", format="csv")` for "NIFTY 10
  yr Benchmark G-Sec", "NIFTY 91 Day T-Bill Index", "NIFTY 4-8 yr G-Sec Index",
  "NIFTY 15 yr and above G-Sec Index" (yield, duration, returns). The full list
  is long: use `list_benchmark_series(kind=["fixed_income"], q="G-Sec")`
- Nifty 500 TRI month-ends (`kind="tri"`) for the growth chart
- `summarize_funds(group_by=["category"], filters={"plan": "regular"}, stats=["return_1m", "return_3m", "return_1y"])` if fund categories are in

Compute index growth with `scripts/analyse.py`. No forecasts, no "markets
will". Offer the analyses for this type in `content/ANALYSES.md` (rupee translations, same-basis comparisons, what the data does not show). Then `design/DESIGN.md`.
