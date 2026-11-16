# Analyses: what to show, how to show it, what it means

A film answers the client's questions with analysis an investment professional
would run, not just with the figures in the document. For every number, ask
three things: what is it compared with, what does it mean in rupees on this
client's money, and what does it not tell us. Offer these in the question menu
(`CONTENT.md`); compute every figure in code from the confirmed inputs and fund
data; never estimate one.

Sources of these practices: Anthropic's financial-services and
claude-for-financial-advisors skills (proposals, client reviews), JoelLewis
finance_skills (historical risk, diversification, liquidity, performance
metrics, finance psychology, advertising compliance), and the equity-research
skills read for source discipline. Ideas only; the wording here is ours.

## Translate every important percentage

Framing changes decisions, so show the percentage and its meaning on the
client's own amount, side by side:

| Measure | On screen | Spoken or written meaning |
|---|---|---|
| Worst fall (drawdown) | −12.6% | "₹40 L in these three funds was ₹5.0 L lower at the worst point." |
| Concentration | 0.88% | "₹2.7 L of the ₹3 crore is in ICICI Bank." |
| Overlap | 28% | "₹28 of every ₹100 in HDFC Value sits in stocks Nippon Multi Asset also holds." |
| Modified duration | 1.35 years | "If bond yields rise by one percentage point, these bonds fall in price by about 1.35%." |
| Standard deviation | 16.8% a year | "A typical year's return has differed from the average by about 17 points." |
| Up / down capture | 134% / 108% | "When the market rose ₹100, the fund rose ₹134; when it fell ₹100, the fund fell ₹108." |
| Expected return (advisor's) | 13.5% a year | "At that rate the money roughly doubles in about five and a half years." (rule of 72, labelled an estimate) |
| Lock-in | ₹1.30 Cr, 3+ years | "₹1.30 Cr cannot be withdrawn for at least three years from investment." |

"About" is right here only because the translation itself is an
approximation (duration, standard deviation, doubling time); say so once.

## Analyses by film type

### Proposal
| Question | Analysis | How to show |
|---|---|---|
| Is the money spread sensibly? | Split by bucket, product type and asset class | One bar that splits; product strip under the holdings |
| How have the funds done? | Growth of ₹1 lakh against the client's benchmark; 3- and 5-year annualised returns; which products have no comparable record | Line chart drawing left to right, end labels, table |
| How bad can a fall get, in rupees? | Worst fall of each fund and of the proposed mix, on the same data and period; rupee loss at the low on the client's amounts; the benchmark's fall for comparison | Bars for each fund, the mix and the index; the rupee figure beside the mix |
| Do the funds diversify each other? | Holdings overlap, and return correlation from monthly NAVs; the mix's volatility against the weighted average of the funds' volatilities | Overlap web; a small correlation grid; two numbers (the mix and the average) |
| What can I withdraw, and when? | Liquidity ladder from each product's terms | Bars by time to redeem; the share reachable in a week |
| How do the options differ? | Bucket amounts, holdings, liquidity, lock-in, the advisor's expected return | Paired bars; a short comparison table |
| What could it become? | The advisor's expected rates compounded, with the caution on screen throughout | Counters running year by year |

### Portfolio review
Add: contribution to return by holding (what drove the result); allocation
against the client's target with drift; worst fall of the whole portfolio in
rupees; overlap and correlation; concentration in rupees; what changed since the
last review.

### Fund
Add: rolling returns (worst, average, best for each holding period); calendar
years with peer rank; capture ratios in rupees per ₹100; drawdown depth, length
and recovery time; return for risk against the category median; valuation of
holdings against the category; what the manager changed.

### Category
Add: spread between best and worst fund (why the choice of fund matters);
median against average (and why they differ: a few new funds); how many funds
beat the benchmark over the period; risk against return scatter; leaders'
score parts.

### Market
Add: index returns by period and company size; valuation against its own
history (percentile, not just the level); bond yields and duration translated
into price moves; what a fall of the recent size means in rupees on a typical
holding.

## What the analysis must not do

- **No forecasts and no invented scenarios.** Projections use only the
  advisor's stated rates. Historical figures are labelled historical, with the
  period.
- **Same data, same period, same basis** for everything compared on one screen
  (do not mix a 3-year daily drawdown with a 5-year monthly one).
- **State the limits** on screen: "Monthly data, so falls within a month are not
  captured"; "Covers the ₹40 L in mutual funds; other products publish no
  comparable data".
- **Report what the analysis shows, even when it is unflattering.** Example from
  a test film: the three equity-heavy funds had return correlations of 0.79 to
  0.94, so holding all three lowered the mix's volatility only from 12.6% to
  12.0%. That is a finding to show, not to hide.
- **Explanations, not cute analogies.** Translate a measure into rupees or a
  plain consequence ("a one-point rise in yields lowers the price by about
  1.35%"). No seesaws, journeys or rollercoasters.

## Voice and highlight timing

When the voice names an item, that item lights at that moment and the rest dim
(`GV.spotlight` with voice cue times). Mark the cue in the voice line:
`"one crore each in {core}Core Growth and {hga}High Growth Alternatives"`.
`film/vo_tts.py` measures each cue's time. Never walk a highlight on a timer
the voice does not follow.
