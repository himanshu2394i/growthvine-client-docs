# Fund report: question set

A look at one fund or several, for a client deciding whether to invest, keep
holding, or choose between funds. Nothing here is a fixed template: you offer a
deep menu, the advisor picks what goes in and where to stop. **Always suggest
more** (another section, another comparison, a deeper subsection); never trim on
your own.

## Step 1: the basics

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| 1 | How many funds? | One fund = a deep dive. Two or three = each fund plus a side-by-side section. Four or more = suggest a shortlist table first, then deep dives on the ones they pick | Number | Yes |
| 2 | Which fund(s)? Regular or direct, growth or IDCW? | Every figure depends on the plan | Names + pick | Yes |
| 3 | Who is it for, and what decision is it helping with? (new investment, keep or switch, choosing between funds) | Sets the story and the comparisons | Pick or their words | Yes |
| 4 | Compare against: the market (Nifty 500 TRI), the fund's category, its own benchmark, specific peers? | Picks the evidence pages | Pick, several allowed | Yes |
| 5 | Client's horizon and experience | Sets language and which risks to stress | Pick | Yes |
| 6 | Advisor's view of the fund, if any | Only the advisor's view goes in the document | Their words | No |

Confirm the matched fund name and plan with the advisor before fetching.

## Step 2: pick sections, then subsections

Show the sections as a numbered list. For each section the advisor keeps, show
its subsections with the rich default pre-ticked (most of them). Let them tick,
untick, rename, reorder. After each section ask "Go deeper here?" and offer the
extras. Every subsection becomes one page or one panel; the advisor can merge
two small ones onto a page.

**1. The fund at a glance**
- Key numbers strip: 3- and 5-year return, size, charge, holdings count
- What it does: objective in plain words, how the manager picks companies
- Who runs it: manager, fund house, benchmark the fund chose
- What it costs to hold and leave: charge, exit load in plain words
- Company size mix (large / mid / small) or asset mix for hybrids

**2. How it has done**
- Returns against the category average and the market, 1 month to 10 years
- Growth of ₹1 lakh against the market index
- Calendar-year returns, with its rank among peers each year
- Monthly investing: SIP returns over 1, 3, 5, 10 years
- Rolling returns: average, worst and best for every 1, 3, 5, 10-year window
- 3-year rolling return over time (line): how steady the record is
- Long record: 7, 10, 15 years and since launch
- *Go deeper:* against its own benchmark; against named peers; best and worst year

**3. How it behaves**
- Share of market rises and falls captured, against the category average
- Worst falls: last 3 years, last 5 years, ever, with dates and time to recover
- Typical yearly swing against the category
- Return for the risk taken (Sharpe, Sortino), extra return over the market
  (alpha) and how much it moves with the market (beta), against the category
- Risk against return: this fund among its peers (scatter)

**4. What it owns**
- Largest holdings
- Largest industries
- Concentration: top 5, top 10, number of holdings, overlap with the index
- Valuation of what it owns (P/E, P/B) against the category
- What changed recently: new buys, full exits, biggest increases and cuts
  (`get_fund_history(type="holdings")`)
- How the industry mix moved over recent months (`type="sectors"`)
- How often it trades (portfolio turnover)

**5. Where it ranks**
- Growthvine's leaderboard with this fund highlighted
- Its score, part by part, and what pulls it up or down
- Head-to-head with its closest peers (returns, risk, cost, size)
- Consistency: quartile over 1, 3 and 5 years

**6. Extras to suggest** (offer them every time)
- Side by side (2+ funds): returns, risk, cost, growth chart of all, and how much
  their portfolios overlap
- Regular against direct plan cost, in rupees a year on the client's amount
- Who this fund suits, and who it doesn't (only from the advisor's view)
- What to watch from here (holdings changes, manager change, size)
- The advisor's view

## Fund data to fetch (v3, CSV where possible)

- `get_fund(scheme_id, include=["profile", "returns", "risk", "factsheet", "allocation", "ranking", "portfolio", "calendar_returns", "rolling_summary"])`
- `get_fund_history(type="nav", interval="month", from_date=<10 years ago or launch>)`, plus Nifty 500 TRI month-ends
- `get_fund_history(type="rolling", window=3, format="csv")` (monthly points) for the rolling-return line
- `get_fund_history(type="holdings", from_date=<3 months ago>, format="csv")` and `type="sectors"` for what changed
- `find_funds(filters={"ranking_category": ..., "plan": ..., "option": "growth"}, sort="rank_in_category", include=["returns", "risk", "factsheet", "ranking"], format="csv")`:
  the whole category in one call, for peers, the leaderboard and the scatter
- `summarize_funds(filters={...}, stats=["return_1y", "return_3y", "return_5y", "expense_ratio", "std_dev", "sharpe", "max_drawdown_3y_pct", "up_capture_3y", "down_capture_3y"])`
  for category averages

Run `scripts/analyse.py` for returns vs the market on one common date and the
growth chart. Offer the analyses for this type in `content/ANALYSES.md` (rupee translations, same-basis comparisons, what the data does not show). Then `design/DESIGN.md`.
