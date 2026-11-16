# Category report: question set

A view of one fund category (or a few side by side): how it behaves, what it
costs, and which funds lead it. Nothing here is a fixed template: you offer a
deep menu, the advisor picks what goes in and where to stop. **Always suggest
more**; never trim on your own.

## Step 1: the basics

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| 1 | Which category, or which categories to compare? | Use the exact category name from the fund data | Pick from `summarize_funds(group_by=["category"])` | Yes |
| 2 | Regular or direct plans? | Averages differ a lot | Pick | Yes |
| 3 | Who is it for? (clients choosing a category, internal research, a market note) | Sets depth and language | Pick | Yes |
| 4 | Show leading funds by Growthvine's ranking? How many? | Ranking is Growthvine's composite score, not a single return sort | Yes/no, number | Yes |
| 5 | Include index-style funds and funds of funds, or active funds only? | They change the averages and the cheapest end | Pick | Yes |
| 6 | Advisor's view of the category, if any | Only their view goes in the document | Their words | No |

## Step 2: pick sections, then subsections

Same flow as the fund report: sections first, then subsections pre-ticked,
"Go deeper here?" after each section.

**1. What the category is**
- In plain words: what these funds buy, from their stated objectives
- Typical mix: average large / mid / small split
- Size of the category: number of funds, total and median fund size

**2. How it has done**
- Average, median and range of returns over 1, 3 and 5 years
- Best against worst fund in each period
- Category average against the market
- Monthly investing: average SIP returns
- *Go deeper:* how many funds beat the market; spread between top and bottom quartile

**3. Risk and cost**
- Typical swing, worst falls and return for risk across the category
- Share of market rises and falls captured, on average
- Charges: range, median, and what index-style funds charge
- Risk against return: every fund as a dot (scatter), leaders highlighted
- Biggest and smallest funds

**4. The leaders**
- Growthvine's top funds with key figures
- What puts them on top: score parts for each
- Consistency: quartile over 1, 3 and 5 years for the leaders
- Leaders against the category average, side by side

**5. Every fund** (offer for internal or detailed reports)
- The full table: rank, stars, returns, charge, swing, size, over one or two pages

**6. Extras to suggest**
- Newer funds without a 3-year record, listed separately
- The most concentrated portfolios
- How this category compares with a neighbouring one (e.g. Flexi Cap)
- The advisor's view

## Fund data to fetch

- `summarize_funds(filters={"category": ..., "plan": ..., "option": "growth", "status": "active", "scheme_type": "open_ended"}, stats=[...])`
  for averages, medians and ranges (returns, SIP returns, charge, swing, Sharpe,
  worst fall, capture, size, large / mid / small split)
- `find_funds(filters={"ranking_category": ..., "plan": ..., "option": "growth"}, sort="rank_in_category", include=["returns", "risk", "factsheet", "ranking", "allocation"], format="csv")`
  for every fund in one call
- Nifty 500 TRI month-ends for the market comparison

Use the fund data's own ranking; never re-rank by a single return. Print the
ranking date. Offer the analyses for this type in `content/ANALYSES.md` (rupee translations, same-basis comparisons, what the data does not show). Then `design/DESIGN.md`.
