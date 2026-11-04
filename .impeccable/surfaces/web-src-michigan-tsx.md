---
version: 1
slug: "web-src-michigan-tsx"
primary_target: "web/src/Michigan.tsx"
related_targets: ["web/src/App.tsx","web/src/michigan.css"]
---

# Surface: Michigan Senate money tab (web/src/Michigan.tsx)

Mode: Operate (read-and-compare). Audience: the same general public, often on phone. Job: see, side by side, how much El-Sayed and Rogers raised, how much came from individual donors and how much from PACs, and where the itemized donors live. Outside spending is shown separately and never added to campaign totals (owner decision, 2026-11-04). Maps are shaded by each state's share of that candidate's itemized money (owner decision).

## Direction contract

THESIS: An extension of the Quiet Pastel Map, not a new world. It shows the same quiet comparison for money instead of votes: two candidates, read row by row, every figure exact. It refuses the campaign-finance dashboard of donut charts, stat tiles and stacked mixed-scale bars.

OWN-WORLD: Inherited unchanged: lilac ground, flat white sheets with hairlines, plum ink, Geist (light for figures). Texas-style rows for each money source, with 4px bars in the candidate's party colour on a scale shared by both candidates. US Albers state maps use five pastel steps of that candidate's party colour.

STORY: The visitor reads that El-Sayed raised 2.3× as much and almost all from individuals, compares the rows, sees Michigan dark on both maps with California next, and then reads the separate outside-money section, where nine-figure spending dwarfs both campaigns.

FIRST VIEWPORT: The header with Texas/Michigan tabs. A white sheet split by a centre hairline: candidate name in display size, a one-sentence answer, then source rows. Mobile stacks the candidates within each section.

FORM: Extension of the existing surface (new-work 3, "Extend an existing surface"). No concept roll; inherits seed f438c94b's world.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
