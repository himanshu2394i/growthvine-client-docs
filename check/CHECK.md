# Check

## A. Before the brief: reconcile the inputs

1. Make sure `inputs.json` exists (see `shared/inputs.md`). Every table is written
   as the document states it, with its `source`.
2. Run `python scripts/reconcile.py inputs.json`.
3. **No issues:** tell the advisor in one line ("Your files agree with each other")
   and continue.
4. **Issues:** show them as a short numbered list, grouped where several lines
   come from one cause. Explain the likely cause in plain words when it's clear
   (e.g. "₹10 L of ISIF looks counted as MF in the plan tables but as SIF in
   Option 1"). Ask which version is right. Never choose yourself.
5. Update `inputs.json` with the advisor's answers (how: `shared/inputs.md`,
   "Recording the advisor's answers") and run it again. Repeat until clean, or
   until the advisor explicitly says to go ahead with a known difference. In that
   case, note it in the brief.

`map` rules in `inputs.json` are only for translating labels when a table groups
differently (e.g. the plan puts every AIF under "Alternatives"). Never write a map
rule to make a mismatch disappear.

## B. After building: verify the document

1. Make sure `inputs.json` holds the **confirmed** inputs (after part A), with:
   - any field the document groups by (e.g. `liquidity` on each holding, if the
     document shows "₹1.20 Cr within a week"),
   - `advisor_figures`: every figure the advisor gave that isn't a sum of
     holdings, exactly as written (e.g. `["13.5%", "14.8%"]`).
2. Run `python scripts/verify.py inputs.json <document>.pdf` (or `.pptx`).
3. **Every figure matches:** go to C.
4. **Figures to check:** each line names the figure and page. Find where it came
   from. A typo or a wrong sum → fix `scenes.json`, render again, verify again.
   A real advisor figure missing from `advisor_figures` → add it only if the
   advisor actually gave it. A real fund-data figure missing from `fund_data` →
   add the source value from the saved fund file. A number you made up to
   explain something (a "rule of thumb" threshold) → reword without it. Never add
   a figure just to make the check pass.
   Stop after 3 rounds and tell the advisor what's still unresolved.
5. The script can't tell if a wrong figure happens to equal another valid sum,
   and it doesn't check wording. So also re-read every scene against
   `inputs.json` yourself: right numbers in the right places, headlines that are
   true ("most of your money" must really be most), as-of dates on data scenes,
   and every chart readable on its own: a title with the measure and unit, and
   every colour named (look at the rendered pages, not just the JSON).
6. When you render the PDF, `render.py` lists any page with too much empty
   space. Fill each one (see "No page may be half empty" in
   `design/DESIGN.md`), render again, and verify again. Don't send a document
   that still has empty-space lines.

## C. Deliver

Short note: what's in it, data as-of dates, anything left blank or marked "to be
added", and any differences the advisor chose to keep. End with:
"Anything about how I did this? Say *feedback* and I'll note it for the team."
