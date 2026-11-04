# Michigan US Senate 2026: campaign finance sources (collected 2026-11-04)

This is separate from the Texas results pipeline. Build it with `python3 -I finance_mi/build.py`. It reads only from `raw/` and writes to `data/mi_senate_2026_finance/`.

| Candidate | FEC candidate | Principal committee | Other authorized | JFC feeding it |
|---|---|---|---|---|
| Abdul El-Sayed (D) | S6MI00418 | C00902668 Abdul for US Senate | C00961805 | C00958066 Abdul for Michigan Victory Fund |
| Mike Rogers (R) | S4MI00595 | C00849810 | C00892026 | C00884296 Team Rogers, plus ~15 smaller JFCs |

## 1. Who Funded Genocide, "The Entire Network", Edition 1 (`raw/whofundedgenocide/`)
- CC BY 4.0. Credit: "The Entire Network." Who Funded Genocide. https://whofundedgenocide.com/map/ Research in collaboration with Wallface.
- All 10 files verified against `SHA256SUMS.txt`.
- **El-Sayed is not in it.** Rogers appears only as two "spent for" lines (UDP $64,393, RJC Victory Fund $16,128), with 2024 and 2026 combined.
- **Known gap:** its candidate-level "spent against" lines cover about 1% of the against-spending its own totals report. It misses UDP's $20.1M against El-Sayed (FEC Schedule E). Never use it as evidence that money was *not* spent.

## 2. Campaign e-filings: authoritative for receipts (`raw/fec_mi_sen_2026/efile/`)
- These are the most recent version of every 2026-cycle F3 report, from `https://docquery.fec.gov/dcdev/posted/{n}.fec` (format 8.5). The list is in `EFILINGS` in build.py.
- Coverage ends **2026-10-14 (El-Sayed, 12G)** and **2026-10-22 (Rogers, 12G)**. The post-general report isn't due until 2026-12-03, so the last ~3 weeks are not here.
- **Reconciliation against FEC processed totals:**
  - El-Sayed: itemized individuals $27,959,392.14, matching to the cent. PAC $404,657.71, party $65,850 and transfers $6,030,960.32 also match exactly.
  - Rogers: itemized is $5,586 short (0.05%), PAC is $5,000 short, transfers are $27k short. These are likely from the small second committee C00892026, which isn't parsed.
- Memo lines are excluded. For El-Sayed they're ActBlue earmark notes (122k lines); for Rogers they're primary-to-general redesignations (~9.5k lines). They duplicate money already counted.
- Unitemized (≤$200 aggregate) is not in any filing. It's derived as total individual minus itemized: El-Sayed $19.24M, Rogers $3.72M.
- Street addresses are read but never written to `data/`.

## 3. FEC bulk files (`raw/fec_mi_sen_2026/bulk/`)
- `weball26` (candidate totals), `cm26` and `ccl26` (committee names and links), and `independent_expenditure_2026.csv` (24/48-hour IE reports, last receipt 2026-11-02). These are the sources for **outside spending**.
- IE dedup: rows in files superseded by an amendment (`prev_file_num`) are dropped, then each (spender, tran_id) keeps its latest filing.
- `indiv26` and `oth26` were streamed and filtered but **are not used**. They stop at the 12P report (2026-07-15).
- **Outside-spending caveats:**
  1. Per-spender support/oppose splits differ between 24/48-hour reports and processed Schedule E (e.g. GLCF). Compare **sides**, not individual lines.
  2. Party IEs are missing from the bulk file. The DSCC's $12.3M against Rogers appears only in the API's processed data.
  3. Some "primary" coding looks like early general-election spending.

## 4. FEC API cross-checks (`raw/fec_mi_sen_2026/api_*.json`)
- DEMO_KEY is limited to 10 requests per hour. The API data is used only to reconcile: totals, Schedule E by candidate, and the filings list.
- Don't use `by_state`/`by_size` from the API. They cover only $10.0M of El-Sayed's $28.0M itemized.

## Matching to the site's donor list (`wfg_donor_overlap.csv`)
- Matches on normalized "LAST, FIRST" + city + state, against the site's ~6,200 named donors to 44 pro-Israel committees.
- 1,031 matches. **70% also agree on employer or on being retired**; most of the rest are spelling variants. Treat it as a strong name match, not proof of identity.
- The site only names its larger donors, so this is a lower bound.
