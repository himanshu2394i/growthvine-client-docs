# Reading what the advisor sends

Advisors send Excel, PDF, pasted tables or screenshots, often several at once.
Map whatever arrives onto the question set; ask only for what's still missing.

## Pieces you'll see

| Piece | Looks like |
|---|---|
| Client profile | Total amount, horizon, liquidity needs, risk appetite / profile |
| Buckets | Named groups (e.g. Core Growth, Stability, Diversifier, High Growth Alternatives) with why, vehicles, horizon / liquidity |
| Options | "Option 1", "Option 2 - Aggressive": separate holding lists for the same money |
| Holdings | Fund / product name, type (MF, SIF, PMS, AIF, MLD...), asset class, amount, bucket |
| Master allocation | Bucket x asset class x vehicle x strategy/sleeve x amount x % x role x liquidity x lock-in/exit |
| Allocation views | Cross-tabs: asset class x vehicle, bucket x vehicle, with totals and % of corpus |
| Advisor comments | Free text, sometimes with expected returns |

Bucket names are the advisor's. Use only what the inputs say about each bucket;
if its purpose is missing, ask.

## Proposal depth

Decide from the inputs, and confirm with the advisor:

- **Bucket level:** buckets and amounts only.
- **Sleeve level:** generic strategies ("Flexi Cap PMS"), no fund names. Supporting
  data from `get_category_stats`, labelled "typical for this category".
- **Fund level:** named holdings. Per-holding pages where the advisor wants them.

## Turning inputs into `inputs.json`

Before reconciling, write the inputs as `inputs.json` in the working folder
(format: `scripts/reconcile.py` docstring). Record each table **as the document
states it**, including stated totals and percentages; don't fix anything while
transcribing. Note which file each table came from (`source`), so the reconcile
report can say "the Investment Plan PDF says X, the Options PDF says Y".

Also record, when known: extra fields on each holding that the document may group
by (e.g. `"liquidity": "Within 1 week"`), and `"advisor_figures"` at the top
level, listing every figure the advisor gave that isn't a sum of holdings (e.g.
expected returns). The final number check (`scripts/verify.py`) relies on both.

Then run:

```
python scripts/reconcile.py inputs.json
```

and go through every issue with the advisor (see `check/CHECK.md`, part A).
