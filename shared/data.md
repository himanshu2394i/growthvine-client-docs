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

## Growthvine fund data (MCP)

If the MCP isn't connected, say so at the start and offer to continue with the
advisor's data only.

Call **`get_analysis_guide`** once before any derived maths (CAGR, rolling returns,
drawdown, plan resolution).

**Resolve the plan** before pulling a fund, and tell the advisor which one you
resolved:
- Direct vs regular: `dirPlan` `"1"` / `"0"`. Never parse it from the name.
- Growth vs IDCW: the plan qualifier in `schemePlanName` (`(G)`, trailing Growth vs
  IDCW / Dividend / `(D)`). The word "Growth" inside a base name is not the option.

| Need | Tool |
|---|---|
| Find a fund by name | `search_schemes` |
| Deep single-fund picture | `get_fund_deep_analysis(scheme_code)` |
| Compare 2-10 named funds | `compare_funds` (never loop per-fund calls) |
| "Typical for this category" (sleeve-level proposals) | `get_category_stats` |
| Rank / best in category | `get_category_leaderboard` / `get_category_funds` (composite score, not a 1Y sort) |
| Holdings, sectors (for look-through, overlap) | `get_fund_holdings`, `get_fund_sectors` |
| Raw NAV curve | `get_nav_history` / `get_nav_history_compare` |
| How fresh is this? | `get_data_freshness` |

`get_fund_deep_analysis` wants the AMFI `scheme_code` (string); other tools often
want a numeric `scheme_id`. Read the tool schema.

Nulls on category-dependent fields are expected (valuation is equity-only; credit
and YTM are debt/hybrid). Not missing data; don't substitute.

Every payload carries `as_of` / `data_as_of`. Print one on the page.
