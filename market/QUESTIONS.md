# Market report: question set

A periodic note on markets for clients: what happened, how different parts of
the market did, and what it means for their plans. It describes and explains;
it never forecasts.

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| 1 | Period covered (month, quarter, year to date) and the end date | Every figure is "to" a date | Pick + date | Yes |
| 2 | Which markets? (broad Indian equity, large / mid / small, sectors, debt yields, gold) | Picks the pages | Pick, several allowed | Yes |
| 3 | Who is it for? (all clients, a segment, internal) | Sets depth and language | Pick | Yes |
| 4 | Advisor's commentary or themes to include (flows, policy, events) | Market events and flows come only from the advisor | Their words, with sources | No |
| 5 | Include how fund categories did over the period? | Adds the category pages | Yes/no | No |

## Data to fetch

- `list_benchmark_series(kind=["tri", "equity", "fixed_income"])`, then
  `get_benchmark_series(...)` for each index chosen: TRI levels for returns,
  NSE equity factsheets for P/E and volatility, fixed-income factsheets for
  yields and duration
- `summarize_funds(group_by=["category"], filters={"plan": "regular"}, stats=["return_1m", "return_3m", "return_1y"])`
  for category returns, if asked

Compute index returns over the period with `scripts/analyse.py` (index files
as `index`, no funds needed, or as several labelled series). No forecasts, no
"markets will". Then `design/DESIGN.md` (market report arc).
