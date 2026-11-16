# Portfolio assessment: question set

A review of a portfolio that already exists: a client's holdings, a prospect's
statement, or a model portfolio. Work through these in order, 2-3 at a time.
Confirm what the files already answer; never skip a required item.

**Required steps** (`SKILL.md`): basics, then the full section and subsection menu, then the storyboard, then build; each waits for the advisor.

## A. Whose portfolio, and why now

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| A1 | Whose portfolio is it: an existing client, a prospect, or a model? | Sets the tone and what "next steps" means | Pick | Yes |
| A2 | What prompted the review? (annual review, market fall, new money, life change, switching advisor) | The story starts here | Pick or their words | Yes |
| A3 | Horizon, liquidity needs, risk appetite, if the advisor knows them | The yardstick every observation is measured against; without it, make a general review | As in the proposal set, or "not known" | No |
| A4 | How experienced is the client with investing? | Sets how simple the language is | Pick | Yes |
| A5 | Any goal amounts or dates (retirement in 2035, ₹50 L for a house in 2028)? | Lets the review talk about progress, not just returns | Their words | No |

Section A is optional beyond A1 and A2: many advisors will not know the
client's goals, target or horizon. If A3 and A5 are unknown, make a general
review (see `content/assess.md`): no drift page, falls in rupees without a
horizon, concentration without a threshold.

## B. The holdings

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| B1 | Each holding: name, type, current value. Invested amount and date if known | The core table; invested amounts allow gain figures | Excel, statement (CAS) or table | Yes |
| B2 | As-of date of the values | Every figure needs it | Date | Yes |
| B3 | Regular or direct plans? | Costs and returns differ a lot | Pick, or per holding | Yes, if any fund data is shown |
| B4 | Holdings outside mutual funds (PMS, AIF, bonds, FDs, shares, insurance)? Include or leave out? | Advisor decides what the review covers | Pick per holding | Yes |

Then write `inputs.json` with one option named "Current portfolio" (values as
`amount`) and run `scripts/reconcile.py` if there are several input files.

Match every fund to the fund data (`shared/data.md`): confirm names and plans
with the advisor. For holdings with no fund data, the advisor picks: provide
figures, empty "to be added" table, or leave out of data pages.

## C. Fund data and calculations

Fetch, using the CSV exports (`shared/data.md`):
- `find_funds(ids=[...], include=["returns", "risk", "factsheet", "allocation", "ranking"], format="csv")`
- holdings history (latest portfolio), monthly NAV history, Nifty 500 TRI

Run `scripts/analyse.py`. Besides look-through, overlap and returns vs the
market, it gives the **asset mix** of the whole portfolio, the **blended annual
charge** (% and ₹ a year), **concentration** (largest holding and top three as
a share), and the **company-size split**.

## D. Advisor's view

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| D1 | What does the advisor want the client to take away? | The headline of the review | Their words | Yes |
| D2 | Any changes the advisor is recommending? | Only the advisor's recommendations go in the document | Their words or "none yet" | No |
| D3 | Anything to word carefully or leave out | Avoids surprises | Their words | No |

## E. Second opinion (in chat only)

Use `shared/wealth-practice.md` §3 and §5: label each point fact, inference,
assumption or unknown; structural risks first; check for too much and too
little risk; follow up the last review's action items, drift against target,
concentration above the advisor's threshold, proactive flags, life-event triggers.

Before designing, give the advisor your read of the portfolio: overlap or
concentration, cost drag, mismatch between the mix and the client's risk or
horizon, funds lagging their category for long stretches, liquidity. Mark it as
your view. Nothing from it goes in the document unless the advisor adopts it.

## Analyses to offer (from `content/ANALYSES.md`)

- **What drove the result:** each holding's contribution to the portfolio's return.
- **Against the plan:** current allocation against the client's target, with drift.
- **The whole portfolio's worst fall in rupees**, beside the benchmark's, on one basis.
- **Do the funds diversify each other?** Overlap per ₹100, return correlation,
  the portfolio's volatility against the weighted average of its funds'.
- **Concentration in rupees:** largest company and sector.
- **What changed since the last review**, if a previous review exists, starting with the last review's action items.
- **Proactive flags** (`shared/wealth-practice.md` §5): cash beyond needs, risk profile or KYC due, nominations after a life event, money needed within 12 months still in equity.

## Done when

Required items are answered, inputs reconciled, fund matches confirmed, the
analysis has run, and the advisor's take-away (D1) is clear. Then go to
`design/DESIGN.md` (assessment arc).
