---
version: 1
slug: "web-src-app-tsx"
primary_target: "web/src/App.tsx"
related_targets: []
---

# Surface: Texas county results map (web/)

Mode: Operate. Audience: general public, often on phone. Job: pick an election, see who won each county, read winner, party and exact counts.
Data scope: 2008–2024, all certified (2026 removed by owner as inaccurate).

## Direction contract

THESIS: A quiet pastel map: Texas in soft rose and powder blue on a pale lilac field, with nothing on screen but the map, the result, and one slim timeline. It replaces the earlier "county quilt" world (binding, stitches, weave), which the owner asked to simplify. It refuses dashboard chrome and dense election-night panels.

OWN-WORLD: Owner-pinned: all pastel, modern, sleek, minimal. Pale lilac-mist ground; white panel; party fabric in three pastel steps by margin (rose for Republican, powder blue for Democrat); lavender for selection and the active year; mint/butter/haze for minor parties. Dark plum ink for all text (AA). Geist variable: light weights for big numbers, medium for names, tabular figures for counts. Hairline borders, soft wide shadows, generous radii.

STORY: Visitor sees 2024 President colored in, reads the statewide winner, taps a county to read its winner, party and votes, and drags the timeline to watch Texas change.

FIRST VIEWPORT: Desktop: thin top row (title + subtitle left, President/Senate/Governor segmented control right); map fills the left; white results panel right (statewide headline, candidate rows, counties-won bar); a floating pill timeline slider centered along the bottom of the map with 9 year ticks. Mobile: title, segmented control, map with the slider at its bottom edge, results below, fixed peek bar when a county is selected. Signature move: dragging the slider re-colors counties in a soft west-to-east wave.

FORM: Owner-pinned direction (pastel minimal); concept-seed f438c94b ran and assigned candidate 3, overridden by the pinned brief in palette, type, density and composition.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

Removed by owner: "through the years" strip, county search box. Kept: margin shading (3 pastel steps), counties-won bar.
