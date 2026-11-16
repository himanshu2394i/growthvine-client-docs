# Category report: question set

A view of one fund category (for example Flexi Cap, Multi Asset, Hybrid
long-short SIFs): how it behaves, what it costs, and which funds lead it.

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| 1 | Which category? | Use the exact category name from the fund data | Pick from `summarize_funds(group_by=["category"])` | Yes |
| 2 | Regular or direct plans? | Averages differ a lot | Pick | Yes |
| 3 | Who is it for? (clients choosing a category, internal research, a market note) | Sets depth and language | Pick | Yes |
| 4 | Show leading funds by Growthvine's ranking? How many? | Ranking is Growthvine's composite score, not a single return sort | Yes/no, number | Yes |
| 5 | Compare with another category or the market? | Picks the comparison pages | Pick | No |
| 6 | Advisor's view of the category, if any | Only their view goes in the document | Their words | No |

## Fund data to fetch

- `summarize_funds(filters={"category": ..., "plan": ...}, stats=["return_1y", "return_3y", "return_5y", "expense_ratio", "std_dev", "sharpe", "aum_cr", "max_drawdown_3y_pct"])`
  for the averages, medians and ranges
- `find_funds(filters={"ranking_category": ..., "plan": ...}, sort="rank_in_category", include=["returns", "risk", "factsheet"], format="csv", limit=...)`
  for the leaders
- Nifty 500 TRI month-ends for the market comparison

Use the fund data's own ranking; never re-rank by a single return. Print the
ranking date (`computed_date` or the freshness date). Then `design/DESIGN.md`
(category report arc).
