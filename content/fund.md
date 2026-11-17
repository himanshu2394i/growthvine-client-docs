# Fund film

A briefing on one fund: can be general (brand version: "A Growthvine fund
briefing", end card "For information only") or personal for one client. First
test: Invesco India Large & Mid Cap (16 Nov 2026), 2:41, 13 scenes, MP4 with
music, no costs.

## Default question chain (offer it, the advisor edits)

| # | Question | Answered with |
|---|---|---|
| 1 | Should this fund be in my portfolio? (cold open) | Its headline return counting up, and where it stands in its category |
| 2 | First, what is this fund, in plain words? | Company-size split; size, number of holdings, top-ten share against the category median, % in shares; manager and benchmark |
| 3 | Has it done better than similar funds? | Return against the category average, 1 to 10 years; its rank on 3-year return; the gap in points |
| 4 | Was that one lucky stretch? | Calendar-year returns with its rank among peers each year; the 3-year return measured every quarter (low and high) |
| 5 | How long should I plan to hold it? | Worst, average and best return for every 1, 3, 5, 10-year holding period: the range narrows |
| 6 | What happens when markets fall? | Share of rises and falls captured against the category; worst falls with dates and recovery time |
| 7 | Is the extra swing worth it? | Scatter of every peer (swing against return), this fund highlighted, any fund the text mentions named; Sharpe, Sortino, alpha, beta against the median |
| 8 | What does it own? | Largest holdings and industries; overlap with the index |
| 9 | Has the manager been changing things? | New holdings, biggest moves, full exits, industry shift |
| 10 | Are the companies it owns expensive? | P/E and P/B against the category median, and the gap in % |
| 11 | If it returned the most, why is it ranked Nth? | Growthvine's score part by part; overall rank against return rank |

Costs (charge, regular vs direct, the "Cost" part of the score) only if the
advisor says yes.

Go deeper (offer): head-to-head with named peers, growth of ₹1 lakh against
the market, SIP returns, quartile consistency, its own benchmark.

## Notes from the test

- Words must match the data: check every "adding X, trimming Y" against the
  actual weights (retail rose overall even though Trent was trimmed).
- A number shown on a chart and in a sentence must be rounded the same way.
- Chart labels near the right edge or beside a table: put them on the side
  with room (scatter labels to the left near a table).
- Bar heights: scale so the tallest bar and its label stay below the panel
  heading.
- Small negatives keep two decimals (-0.03%, not -0.0%).

## Notes from test 2 (HyperFrames, 17 Nov 2026)

Rebuilt fresh after the gate (general brand briefing, new investment, no costs):
13 scenes, 3:54. Order: cold open, what it is, against similar funds, calendar
years, holding period, falls, swing against return, holdings, manager's changes,
the score, what to weigh, end card.

- **Calculate returns from NAVs, all on one date.** The ranking snapshot's
  1-year return (1.8%) did not match the NAVs (+12.9% to 13 Nov 2026): the fund
  rose 11% in two weeks, so the end date changed the story. Fetch the fund's,
  every peer's and the index's NAV on the same dates and compute the returns.
- **Similar funds** = the active funds in the category with a 5-year record
  (26 here); leave out index funds and fund-of-funds, and say so on screen.
- **Check every absolute claim against the data.** The worst 5-year stretch lost
  0.03% a year, so "never lost money over five years" would have been false;
  say what ₹1 lakh became instead.
- A general briefing has no client amounts: show ₹1 lakh as the example.
- Questions in the client's voice still pass the wording check: no "just",
  "really" or "actually".

## Notes from test 3 (the full section menu, 17 Nov 2026)

Built after the required steps: the advisor picked every section and
subsection, story order, a head-to-head with the next three funds on 3-year
return, and a closing one-page summary. 21 scenes, 6:51.

- The one-page summary is a still scene (`data-hold`, no voice) with every key
  number in eight cards; save its last frame as a PNG for the advisor to share.
- Medians for peers (Sortino, alpha, beta, P/E, P/B, worst falls) come from one
  `find_funds(ids=[...], include=["risk", "factsheet"], format="csv")` call.
- Daily TRI over ten years is too long for one call; take yearly points by date
  for growth charts, and month-end NAVs for SIP returns.
- Write numbers on screen in full words, not "typ.": an abbreviation's full
  stop splits the sentence for the wording check.
- In scene markup written with Python f-strings, compute positions in Python
  (`{484 * 35 / 50:.0f}`); a JavaScript `${...}` there turns into "$325px" and
  the browser drops it.
