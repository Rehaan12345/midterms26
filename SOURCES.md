# Data source probe results (2026-11-03, election night)

Raw probe responses are in `raw/probe/`. Treat them as untrusted downloads.

## ✅ 2008–2018: SOS legacy archive (official, static HTML)
- Election list: `https://elections.sos.state.tx.us/index.htm`
- Race list: `elchist{ELECTION_ID}_raceselect.htm`
- County-by-county table: `elchist{ELECTION_ID}_race{RACE_ID}.htm`
- General election IDs: 2008=141, 2010=154, 2012=164, 2014=175, 2016=319, 2018=331
- Table columns: County | one column per candidate (header row gives name, then party) | Total Votes | Total Voters (registered) | TurnOut %. The first data row is `ALL COUNTIES`.
- Checked: 2018 US Senate (race 832). Cruz + O'Rourke + Dikeman = 8,371,655, which matches the Total Votes column. Bonus: registered voters and turnout for each county.
- Not yet checked: race IDs for the other 8 races (look them up in each `_raceselect.htm`).

## ⛔ 2020–2024: `results.texas-election.com` is blocked to scripts
- Returns `403` with `cf-mitigated: challenge` (a Cloudflare bot check). Not getting around it.
- Affects 5 races: 2020 Pres, 2020 Sen, 2022 Gov, 2024 Pres, 2024 Sen.
- Options:
  1. **Manual official download**: open the site in a browser and save the county-by-county canvass report (Excel/PDF) for each of the 5 races into `raw/sos_tx_election/`. About 10 minutes of clicking, and it keeps the "official source" claim.
  2. Fallback: OpenElections (2020/2022 precinct files rolled up to county; 2024 `counties/`) and MIT county presidential data (2020/2024). These are independent compilations, not official.

### ✅ Manual downloads received (checked 2026-11-03)
- Each file is a **whole-election** export (sheet "Voter Turnout Report"), not a single race. It's in long format: `ELECTION DATE-NAME | OFFICE NAME | CANDIDATE NAME | COUNTY NAME | TOTAL VOTES PER OFFICE PER COUNTY`. Vote counts are strings with commas.
- `2020_pres.xlsx` and `2020_sen.xlsx` are the same file (sha256 `5bae9479…`), as are `2024_pres.xlsx` and `2024_sen.xlsx` (`7b1e1a75…`). `2022_gov.xlsx` is `7ceb970c…`.
- All 5 races have 254 counties and 0 unparseable vote cells. Statewide sums: 2020 Pres Trump 5,890,347 / Biden 5,259,126; 2020 Sen Cornyn 5,962,983 / Hegar 4,888,764; 2022 Gov Abbott 4,437,099 / O'Rourke 3,553,656; 2024 Pres Trump 6,393,597 / Harris 4,835,250; 2024 Sen Cruz 5,990,741 / Allred 5,031,249.
- Gotchas: 2020 Senate is `"U. S.  SENATOR"` (double space), so collapse whitespace before matching. There's **no party column**, so party has to come from `candidates.csv`. Presidential candidates appear as "PRES/VP" pairs.

### Parties for the Excel years
The Excel exports have no party column. Party labels come from OpenElections, taking the party with ≥95% of the labeled votes for that surname. Candidates with no OE label at all are marked `WRI` and tagged "inferred write-in". One manual override: Jacqueline Abernathy (2022 Gov). OE labels her ASP, but she was a declared write-in. Each candidate's provenance is in the `party_source` column of `reference/candidates.csv`.

### Cross-checks
- **OpenElections is information only, never a gate.** Against the official SOS county totals, OE is higher in 100+ counties (likely duplicated subtotal rows) and has no data for 153 counties in 2022 Governor.
- **MIT county presidential 2000–2024** (Dataverse DOI 10.7910/DVN/VOQCHQ, CC0, version 20260225) is downloaded by hand (guestbook) to `raw/mit/countypres_2000-2024.csv`, sha256 `92995831…`. It's a **build gate**: comparing `mode == TOTAL` rows by party bucket (MIT folds minor candidates into OTHER), **all 254 counties match exactly for every President race 2008–2024**.
- Still no independent check: 2020 Senate, 2022 Governor, 2024 Senate. These rely on the official SOS Excel exports alone.

## ⚠️ 2026 Senate: Decision Desk HQ CSV (unofficial), added 2026-11-04
- File: `raw/ddhq/race_294702_2026-texas-us-senate.csv` (copy of the user-provided export from https://votes.decisiondeskhq.com/). Adapter: `pipeline/adapters/ddhq_csv.py`.
- Wide format: `county_name, James Talarico, Ken Paxton, Ted Brown`. No party column, write-ins, statewide row or timestamp. Parties were added by hand in `reference/candidates.csv`.
- Checked: all 254 counties are present and every name matches Census. All cells are integers. Totals: Talarico 5,259,847 (54.21%), Paxton 4,260,640 (43.91%), Brown 181,886 (1.87%), 9,702,373 total.
- **Lubbock = 0 for every candidate**, so it's treated as not reported (253/254).
- There's no independent check: no statewide total from DDHQ, and nothing certified yet. DDHQ's terms may restrict republishing its data.

## ⛔ 2026 SOS election-night snapshots: removed (2026-11-04)
The owner removed all 2026 data as inaccurate. Raw snapshots were deleted and the 2026 rows dropped from `reference/races.csv`. The API notes below are kept only for re-adding certified results later.

### SOS Civix ENR (reference only)
- Base: `https://goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr`
  - `/electionConstants`: election list. The body is `{"upload": base64(JSON)}`.
  - `/election/53815`: 2026 November General. Each top-level field is base64(JSON). `StateWide.Races`, `Federal.Races`, `Home` (counties reporting, last updated).
  - `/election/countyInfo/53815`: `{"upload": base64}` → keys `"1".."254"` → `{N: county name, Races: {officeId: {N, T, C: {candId: {N, P, V, PE}}}}}`
  - `/electionReports/{id}/{report}/{pdf|xlsx}`: includes `CountybyCountyCanvassReport` (not tried yet)
- ~~County id → FIPS: `48` + (id*2-1)~~. **Wrong for 9 counties** (Madison through McMullen): SOS sorts "Mc" literally, while Census FIPS sorts it as "Mac". The pipeline matches counties **by name** against the Census list only.
- Gotchas: the race name is `"U. S. SENATOR "` (trailing space), so strip names. `O` on the election is `"N"` for this election and `"Y"` for the canvassed primaries, so it likely means "official".
- Checked at snapshot `enr/53815/58/` (Home.LastUpdatedTime `Nov 04, 2026 06:18:50`, which looks like UTC; 247/254 counties, 2732/5302 polling places reporting): county sums **exactly match** statewide totals for Governor and US Senate.
- **Status: UNOFFICIAL and incomplete.** Re-pull after the county canvass and again after the state canvass.
