# Fund report: question set

A deep look at one fund (or two or three side by side), for a client deciding
whether to invest or to keep holding it.

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| 1 | Which fund(s)? Regular or direct, growth or IDCW? | Every figure depends on the plan | Names + pick | Yes |
| 2 | Who is it for, and what decision is it helping with? (new investment, keep or switch, comparing two) | Sets the story and the comparisons | Pick or their words | Yes |
| 3 | Compare against: the market (Nifty 500 TRI), the fund's category, specific peers? | Picks the evidence pages | Pick, several allowed | Yes |
| 4 | Client's horizon and experience | Sets language and which risks to stress | Pick | Yes |
| 5 | Advisor's view of the fund, if any | Only the advisor's view goes in the document | Their words | No |

Confirm the matched fund name and plan with the advisor before fetching.

## Fund data to fetch (v3, CSV where possible)

- `get_fund(scheme_id, include=["profile", "returns", "risk", "factsheet", "allocation", "portfolio", "calendar_returns", "rolling_summary"])`
- `get_fund_history(type="nav", interval="month", from_date=<10 years ago or launch>)`, plus Nifty 500 TRI month-ends
- `get_fund_history(type="rolling", window=3)` for the rolling-return chart; `type="capture", window=3` for up and down capture
- `summarize_funds(filters={"category": ..., "plan": ...}, stats=["return_1y", "return_3y", "return_5y", "expense_ratio", "std_dev", "sharpe"])` for category context
- `find_funds(filters={"ranking_category": ..., "plan": ...}, sort="rank_in_category", limit=10)` for where it ranks

Run `scripts/analyse.py` for returns vs the market on one common date and the
growth chart. Then `design/DESIGN.md` (fund report arc).
