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

Also record:

- **`profiles`**: the client profile as *each* document states it (total,
  horizon, liquidity needs, risk), one entry per source. Documents often word
  these differently ("Moderate to High" vs "Growth Oriented"); the check flags
  differences so the advisor picks one.
- **Tables keyed by several columns** (a master table's bucket + asset class +
  vehicle): use a list, `"rows": {"field": ["bucket", "asset_class", "vehicle"]}`.
  Labels then read "Core Growth | Equity | MF".
- **Extra fields on each holding** the document may group by, e.g.
  `"liquidity": "Within 1 week"`.
- **`advisor_figures`**: every figure the advisor gave that isn't a sum of
  holdings (e.g. expected returns), exactly as written.
- **`fund_data`**: every figure you'll show from Growthvine fund data:
  `[{"name": "<official name and plan>", "source": "Growthvine fund data",
  "as_of": "15 Nov 2026", "figures": {"1 year": "12.74%"}}]`.

The final number check (`scripts/verify.py`) relies on the last three.

**Recording the advisor's answers to mismatches:** change `inputs.json` to the
version the advisor confirmed (e.g. correct the outdated table's cells, or fix a
holding's label), and add `"note": "Corrected per advisor <date>: <what>"` to
whatever you changed. Never delete a table just to silence the check; delete it
only if the advisor says the document should ignore it.

Then run:

```
python scripts/reconcile.py inputs.json
```

and go through every issue with the advisor (see `check/CHECK.md`, part A).
