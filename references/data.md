# Data

Two honest sources. Never a third invented one.

## Dump in the conversation

Treat pasted text, CSV, Excel, PDF, and screenshots as canonical when the user
says so (the default after a dump). Read every figure off the dump. Do not round
a 12.73% into 13% to "look cleaner." Carry their as-of date; if the dump has none,
ask.

If the dump is a factsheet for fund A and they also mention fund B with no numbers,
ask whether to pull B from the connector or drop B.

## Growthvine connector

Use when they named a scheme, category, or peer set and did not dump the figures,
or when they asked to fill holes.

Call **`get_analysis_guide`** once before any derived math (CAGR, rolling returns,
drawdown, plan resolution). Do not reconstruct Growthvine's composite rank from
raw returns.

Resolve the plan before pulling:

- Direct vs regular: `dirPlan` `"1"` / `"0"`. Never parse it from the marketing name.
- Growth vs IDCW: `schemePlanName` plan qualifier (`(G)`, trailing Growth, vs IDCW /
  Dividend / `(D)`). Do not treat the word "Growth" inside a base name as the option.

Tell the user which scheme you resolved (name + plan) before you build.

### Which tool

| They asked | Call |
|---|---|
| Deep single-fund pack | `get_fund_deep_analysis(scheme_code)` |
| Rank / "best in category" | `get_category_leaderboard` or `get_category_funds` (composite score, not a 1Y sort) |
| Compare 2–10 named funds | `compare_funds` |
| Filter many funds by one metric | `search_schemes` |
| Whole-category context | `get_category_stats` |
| Raw NAV curve shape | `get_nav_history` / `get_nav_history_compare` |
| How fresh is this? | `get_data_freshness` |

Do not loop `get_fund_details` per fund. Do not substitute `search_schemes(sortBy=1Year)`
when they asked for a rank.

`scheme_code` (string, AMFI) is what `get_fund_deep_analysis` wants. Other tools
often want numeric `scheme_id`. Read the tool schema. Get `schemeCode` from a
leaderboard or search row.

Nulls on category-dependent scores are expected (valuation is equity-only; credit
and YTM are debt/hybrid). Do not treat those nulls as missing data or invent a
substitute score.

Every ranking payload has `computed_date` / `as_of` / `data_as_of`. Print one on
the page. They can differ; if the user asks "as of when," prefer `data_as_of` for
freshness and keep `as_of` for the snapshot.

## Conflicts

Dump vs live pull: **dump wins**, unless they asked to refresh.

Two connector calls that disagree: trust the later payload's own as-of, and do not
average them.

## What you may compute

Only after `get_analysis_guide`, and only when the connector did not already
return the figure:

- Point-to-point return for ≤1 year from NAV
- CAGR for >1 year
- Rolling returns from a full NAV series (need N+M years of history)
- Max drawdown from NAV if no endpoint provided it

Prefer Investwell Sharpe / stdev on the payload over a homemade Sharpe with a
guessed risk-free rate.

## Empty and honest

No numbers → no chart. Ask or skip. "N/A" inside a donut is a lie. A one-line
"this scheme has no holdings breakdown (debt)" is honest.
