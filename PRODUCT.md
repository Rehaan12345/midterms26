# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Vite + React + MapLibre GL JS (open-source map rendering). Data comes from `data/texas.sqlite` (built by `pipeline/`), exported to static JSON. No backend.

## Users

The general public: Texans curious how their county voted, many with little background in election data. Often on a phone. The job: pick an election, see who won where, and see the numbers for their own county.

## Product Purpose

An interactive map of Texas county results for the top-of-ticket races (President, US Senate, Governor) in the November general elections from 2008 to 2026. Each county is colored by its winner. Success means a first-time visitor can find their county and read the winner, party, and vote counts without help.

## Positioning

Every number comes from official Texas Secretary of State canvass data, checked against independent sources: county sums match the SOS statewide totals, and President 2008–2024 matches MIT Election Lab county data exactly. The map shows where each number comes from and does not round away the truth.

## Capabilities and Constraints

- 16 races: 2008 Pres/Sen, 2010 Gov, 2012 Pres/Sen, 2014 Sen/Gov, 2016 Pres, 2018 Sen/Gov, 2020 Pres/Sen, 2022 Gov, 2024 Pres/Sen. Not every year has every office. 2026 Sen is unofficial.
- 254 counties per race. Every candidate is shown, including Libertarian, Green and write-ins.
- **2026 Senate re-added (2026-11-04)** from a user-provided Decision Desk HQ county CSV (votes.decisiondeskhq.com). Unofficial and uncertified: the UI labels it "Unofficial · Decision Desk HQ" and says "leads" instead of "won". Lubbock is 0 in the file and is shown as not reported. The earlier SOS election-night 2026 data stays removed as inaccurate. Replace with certified SOS canvass results when they're available.
- Party codes: REP, DEM, LIB, GRN, WRI. Winners in every certified race are REP or DEM.
- County-level only. No precinct data, turnout modeling, or projections.

## Evidence on Hand

- `data/texas.sqlite`: county_results, candidates, races, elections, counties tables plus the `county_results_pct` view.
- `data/checks.md`: verification report. `SOURCES.md`: provenance for every source.
- County geometry: not yet in the repo (Census TIGER cartographic boundaries are planned).
- No testimonials, users, or press exist; don't fabricate any.

## Product Principles

1. Truth first: exact counts, a visible source, unofficial data labeled as such.
2. Answer the plain question fast: who won my county, by how much.
3. Low friction for people who aren't already engaged: readable on a phone, no jargon, no required interaction to see the main story.
4. Party color is data, not decoration. Pastel rose and powder blue mean Republican and Democratic winners and nothing else.

## Accessibility & Inclusion

The general-public audience means WCAG AA contrast, keyboard access to county selection, and not relying on color alone: winner name and party appear as text.
