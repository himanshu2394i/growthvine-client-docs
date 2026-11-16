# Proposal: question set

Work through these in order, 2-3 at a time. Skip anything the advisor's files
already answer, but **confirm** what you read ("I see ₹3,00,00,000, long-term,
low liquidity needs. Right?"). Never skip a required item.

If the advisor prefers filling a sheet to answering one by one, offer an input
sheet made for **this** proposal: columns from the items below that are still
open, and anything already known filled in. Not a fixed template.

## A. Client

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| A1 | Total amount to invest | Everything is measured against it | Number (₹) | Yes |
| A2 | Investment horizon | Frames what to expect | Pick: short (<3y) / medium (3-5y) / long-term (5y+) / their words | Yes |
| A3 | Liquidity needs | Decides how much lock-in is acceptable | Pick: low / medium / high / their words | Yes |
| A4 | Risk appetite or profile label | Shown on cover; checked against the plan | Their label (e.g. "Moderate to High", "Growth Oriented") | Yes |
| A5 | Anything else about the client worth saying (goal, existing holdings, constraints) | Only if it should shape the document | Free text | No |
| A6 | How experienced is the client with investing? | Sets how simple the language is | Pick: first-time / some experience / experienced | Yes |

## B. Structure

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| B1 | Is the money organised in buckets? If yes, their names | Buckets are the story spine | List, or "no buckets" | Yes |
| B2 | For each bucket: why it exists, vehicles used, horizon / liquidity | The document explains buckets only in the advisor's words | Short text per bucket | Yes, per bucket |
| B3 | How many options are we proposing? | One plan, or a choice | Number | Yes |
| B4 | If 2+ options: one document comparing them, or separate documents? | Advisor picks each time | Pick: compare in one (default) / separate | If B3 ≥ 2 |
| B5 | What depth: buckets only, generic strategies, or named funds? | Decides which pages are possible | Pick: bucket / sleeve / fund level | Yes |

Inputs often mix levels: options name funds while a master table names generic
strategies ("Flexi Cap PMS"). Then the named funds are the detail and the
strategy table is the summary. Say so and confirm.

## C. Holdings (per option)

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| C1 | Each holding: name (or strategy), type (MF / SIF / PMS / AIF / MLD / other), asset class, amount, bucket | The core table | Table / file | Yes |
| C2 | Liquidity and lock-in / exit notes per holding or sleeve | Feeds "getting your money out" | Table / file | No, but ask |
| C3 | Role of each holding in the plan, in a few words | Only if the advisor wants per-holding explanation | Short text | No |
| C4 | Regular or direct plans? | Costs and returns differ a lot between the two; files rarely say | Pick: regular / direct / per holding | Yes, if any fund data is shown |

**C2 when liquidity sits in a strategy table:** match each holding to its
strategy row (bucket + asset class + vehicle) and take that row's liquidity and
lock-in/exit notes. Show the matches in one short list. Holdings with no matching
row (often in a second option) must be asked about; never guess their liquidity.

After C1: write `inputs.json` and run the reconcile check (`check/CHECK.md`,
part A). Resolve every issue with the advisor before going on. Summary tables
(bucket views, master tables) usually describe **one** option: work out which by
matching their totals to each option's holdings, and ask if it isn't clear.

Then, for fund-level proposals, look up each holding in the fund data (MCP,
`shared/data.md`):

1. Search by the distinctive words, including the fund house's full name
   (advisors write "Nippon Multi Asset"; the fund is "Nippon India Multi Asset
   Allocation Fund").
2. Show every match as *advisor's name → official name, plan* and ask the
   advisor to confirm. Point out near-twins (e.g. a fund-of-funds with a
   similar name) and anything that contradicts the advisor's labels (e.g. the
   advisor says "Large Cap" but the fund is "Ex-Top 100"). That last kind also
   belongs in the second opinion (E).
3. List holdings with **no data** (usually AIF, PMS, MLD, and SIFs too new for a
   track record). For each, the advisor picks: provide figures / empty "to be
   added" table / leave out of data pages with a one-line note.
4. **Fetch the full fund data and run the calculations** (`shared/data.md`,
   "Calculations"): `get_fund` for every matched fund, monthly NAV for all of them
   in one call, Nifty 500 TRI, then `scripts/analyse.py`. This gives the fund
   pages, look-through, overlap, returns vs the market, growth charts and
   projections.
5. Record every figure you will show in `inputs.json` under `fund_data` (the
   `fund_data` block from `analyse.py`, plus any figure taken straight from
   `get_fund`), with source and as-of date (see `shared/inputs.md`).
6. If look-through covers less than about half the money because PMS/AIF
   portfolios aren't published, ask whether the advisor has those portfolios
   (often in their Excel) to include.

## D. Advisor views

| # | Ask | Why | Format | Required |
|---|---|---|---|---|
| D1 | Any expected return figures to show? | Only advisor figures are allowed | Number(s) + basis | No |
| D2 | Comments or reasoning you want in the document | Their words, used as given | Free text | No |
| D3 | Anything the client must not see or that must be worded carefully | Avoids surprises | Free text | No |

If D1 has figures: they go inside the document with a "not a guarantee" note,
never on the cover. If the advisor asks for them on the cover, explain that and
offer an inside page.

## E. Second opinion (in chat only)

Once A-D are clear, give a short, honest view: overlap or concentration,
liquidity vs A3, fit with A4, cost, anything that looks off. Mark it clearly as
your view. The advisor decides; their data in the document doesn't change unless
they change it.

## Done when

All required items are answered, the reconcile check is clean or every issue is
resolved, and missing-data choices are made. Then go to design.
