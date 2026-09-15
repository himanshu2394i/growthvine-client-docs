# C split (Mint Billboard)

The approved first-page language from Growthvine's Split board / C prototype.
Print and slides copy the *grammar*, not browser tricks (sticky rails, scroll spy,
magnetic buttons).

## Two worlds

| | Mint outdoor board | White brief |
|---|---|---|
| Job | First impression. Name + three facts + as-of. | The research letter. |
| Ground | Mint `#B1F0DB` | Clarity White |
| Ink | Foundation Grey | Foundation Grey |
| Graphic | Fingerprint arcs, one crop, ~10–20% opacity, bleeding off a corner | One fingerprint or mint orb in the background, ~5–10% opacity, not a tile |
| Type | Huge scheme name, Poppins 600, about 18ch, tight leading | Chapter title 28–36pt; body 10–11pt |
| Data | Stair bars (3Y / 5Y / AUM or the three they chose), exit-load line | Hairline tables, one lead donut + ledger, paired bars |

Never invert mid-document (a warm paper band between white pages, a purple hero
after the mint board). Section tints inside the same world are fine (white next to
a 14% grey hairline). A second full theme switch is not.

## Mint board (cover)

Split: copy on the left (max ~42rem worth of column), fingerprint on the right.
The name is the poster. Subtext stays under ~20 words. CTA, if any, is one pill
in Foundation Grey on mint (white/inverse type), label that fits one line.

Stairs: each row is a grey wash scaled to the value, label left, figure right.
They are *one* graphic field, not three colored tiles. Do not paint 3Y mint, 5Y
mustard, AUM peach.

Exit load sits as type + a small icon treatment, not a badge overlay on the
fingerprint.

Do not restyle this cover into a centered SaaS hero, a photo, or Vine Indigo
unless the user explicitly asked to drop C split.

## White brief

Reads like a printed letter, not a dashboard of cards.

- Hairline rules (Foundation Grey at ~12–15% opacity), 0.5–1pt. No drop shadows,
  no 22px card radii.
- Left chapter index on the web becomes a page title + number on paper
  (`Fund information`, not `08 · INDEX`).
- Metrics: small label, large value, hairline under the row. Group related facts
  (NAV / AUM / TER vs dates). Do not nth-child rainbow fills.
- Composition: **one lead figure** (usually asset allocation) at readable scale
  beside a ledger. Remaining splits are stacked ledgers or small multiples, never
  five equal donuts.
- Quartile: donut or tower **beside** a real Q1–Q4 table, not a legend-only ring.
- Names (AMC, manager): large Poppins, not a mint highlighter behind the words.
- FAQ: plus in a mint disc that can rotate to ×. Open answer is type, not a
  mustard block.

Background graphic (fingerprint or one mint orb) stays behind type, pointer-free,
and is one object. If the brief is long, pin that object as a repeating corner
mark at low opacity rather than tiling the SVG.

## Print / slide translation

| Web | PDF / PPTX |
|---|---|
| Sticky chapter rail | One chapter per page/slide. Title is the rail. |
| Full-viewport mint board | Full-bleed mint page or the first slide. |
| Scroll-linked fingerprint | Static crop, same corner, same opacity band. |
| Hover scale on donuts | Still donut. No hover. |

Full-bleed colored panels need `@page { margin: 0 }` (PDF) or a rectangle that
reaches the slide edge (PPTX). Without that, mint becomes a sad inset box.

## What C split is not

- Not Ionic Wealth (no cobalt, Geist, or their logo)
- Not the live fund-detail admin cards (those stay on the product site)
- Not "use all five brand colors on every page"
