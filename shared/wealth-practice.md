# Wealth practice: how a careful advisor builds a proposal, review or report

The methods below come from wealth-management and financial-analysis skills
on GitHub, rewritten for Growthvine and Indian advisors (AMFI-registered
distribution, rupees, Indian products). Use them in every proposal,
portfolio review, fund, category and market document or film. Sources are at
the end; no text was copied from repos without a licence.

## 1. Interview in the order a planner thinks

Ask in this order, and do not discuss products until the money's role is clear:

1. **Goals:** what is this money for, by when, and in what order of priority?
2. **Fixed commitments in the next 1 to 5 years:** education, a home, medical
   costs, taxes due. Amounts and dates if known.
3. **Income:** how steady it is, and whether it depends on the same sector as
   the portfolio (a banker holding bank stocks).
4. **Emergency money:** how many months are set aside, and whether it is truly
   available.
5. **Risk, asked two ways** (see 2).
6. **The role of each holding:** emergency, short-term, long-term, income.
7. **Products**, only after the above.

**The advisor may not know these.** Offer goals, commitments, income and
emergency money as an optional section of the question menu; when they are
unknown, build a general review or report from the portfolio and the data
alone, and never invent them.

**Ask only questions that could change the plan.** Stop when the answer would
not move the direction, size or timing. Record a refusal or gap as *unknown*;
never fill it in.

## 2. Risk: willingness and capacity

Ask both:
- **Willingness:** "If this portfolio showed a paper loss of ₹X, would you want
  to sell?" (use rupees on their amount, not only %).
- **Capacity:** how long until the money is needed, how steady income is,
  whether there are six months of emergency money elsewhere, and what share of
  total wealth this money is.

**When they conflict, use the lower one, and say in the document which one and
why.** Someone willing to take a 30% fall who needs the money for a house in
three years has a much lower real limit.

## 3. Analysis that separates fact from judgement

In the advisor's second opinion (chat, never the document unless adopted):
- Label every point **fact** (from the data), **inference** (reasoned from
  facts), **assumption** (stated, could be wrong) or **unknown**.
- **Structural risks first:** concentration, liquidity against upcoming
  commitments, money needed sooner than it can be redeemed, income tied to the
  same sector as the holdings.
- **Check both directions:** is the plan taking too much risk for the client's
  capacity, or too little for their goals? Never default to caution.
- **Say what is calculated and what is a judgement.**

## 4. Order of action (proposals and reviews)

End with: **what to do now**, **what to leave for now**, **what would trigger
the next step** (a date, a level, a life event), **which unknowns could still
change the conclusion**, and **when to review next**. Only the advisor's own
decisions go in the document.

## 5. Portfolio review routine

- **Start with the last review's action items:** done, pending, dropped.
- **Allocation against the client's target**, with the drift for each bucket
  and the tolerance band the advisor uses (for example ±5 percentage points).
- **Performance:** standard periods (since the last review, 1, 3, 5 years,
  since investment), against the benchmark agreed with the client, never the
  one that flatters. Name the top contributors and detractors.
- **Concentration threshold:** flag any single holding or company above the
  advisor's threshold (commonly 10 to 15% of the portfolio) for discussion.
- **Proactive flags:** cash beyond the client's stated needs; a risk profile or
  KYC due for re-confirmation (typically every 12 months); nominations not
  reviewed after a life event; money needed in the next 12 months still in
  equity.
- **A life event triggers a full review**, not a routine one: a large inflow,
  a job change, marriage, a birth, retirement. Capacity for risk may have
  changed.

## 6. Fund analysis depends on the fund type

| Type | What to examine, in order |
|---|---|
| Index fund or ETF | Tracking difference against the index, then cost, size, liquidity |
| Active equity fund | The manager and tenure, holdings and concentration, return over the benchmark, style drift (has it moved away from its stated style?) |
| Hybrid or multi-asset | Asset mix and how it has changed, fall in bad periods against pure equity, return for the risk taken |
| Debt fund | Yield, credit quality, duration (translated into a price move), size, cost |

Also flag: a fund shrinking fast (closure or concentration risk), a manager
change, a change in what the fund holds. Missing data is written as "not
available", never estimated.

## 7. A gate before any writing

Before drafting a document or film, show the advisor in chat: the assumptions,
any conflicts between inputs, the gaps, at most three clarifying questions, and the
verified key numbers. Write only after they confirm. The limit is for clarifying questions only: the section and
subsection menu in the question set is always shown in full, after the gate
and before any writing. (This is the visible brief
in `design/DESIGN.md`, made stricter.)

## 8. Reporting falls honestly

A single historical worst fall is one sample. Always state the period and the
data (monthly or daily). Where the data allows, give the worst fall over the
longest history available as well as the recent one, and say what the history
does not include (for example, a fund launched after 2020 has not been through
a major fall).

## Sources (ideas; wording here is ours)

- fancy0121/investment-portfolio-review-skill (MIT): interview order,
  decision-changing questions, fact/inference/assumption/unknown, order of
  action, checking for too much and too little risk.
- henrywen98/asset-allocation (MIT): willingness and capacity, take the lower;
  honest reporting of worst falls.
- LucianBuddy/etf-fund-analysis (Apache-2.0): fund analysis by type; flags for
  shrinking funds and style drift.
- JoelLewis/finance_skills (MIT): client review preparation, client reporting,
  performance reporting, drift bands, concentration thresholds, life-event
  reviews.
- anthropics/financial-services and claude-for-financial-advisors (Apache-2.0):
  client review and proposal structure, the advisor's rationale only in their
  words.
- prashant-pilla/citework (MIT): the gate before writing.
- Read, not used: Underbite-Capital/za-financial-advisor-skills (no licence,
  South African rules), himself65/finance-skills and star23/Day1Global-Skills
  (trading and US stocks), GAJETOso/financeskills (accounting-focused).
