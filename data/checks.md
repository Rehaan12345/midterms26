# Verification report

| status | check | race | detail |
|---|---|---|---|
| PASS | completeness | 2008-PRES | 254 counties x 10 candidates |
| PASS | cross-check MIT | 2008-PRES | all 254 counties match exactly by party bucket ['DEM', 'OTHER', 'REP'] |
| PASS | statewide reconciliation | 2008-PRES | county sums == source statewide total for all 10 candidates (exact) |
| PASS | completeness | 2008-SEN | 254 counties x 3 candidates |
| PASS | statewide reconciliation | 2008-SEN | county sums == source statewide total for all 3 candidates (exact) |
| PASS | completeness | 2010-GOV | 254 counties x 5 candidates |
| PASS | statewide reconciliation | 2010-GOV | county sums == source statewide total for all 5 candidates (exact) |
| PASS | completeness | 2012-PRES | 254 counties x 11 candidates |
| PASS | cross-check MIT | 2012-PRES | all 254 counties match exactly by party bucket ['DEM', 'OTHER', 'REP'] |
| PASS | statewide reconciliation | 2012-PRES | county sums == source statewide total for all 11 candidates (exact) |
| PASS | completeness | 2012-SEN | 254 counties x 4 candidates |
| PASS | statewide reconciliation | 2012-SEN | county sums == source statewide total for all 4 candidates (exact) |
| PASS | completeness | 2014-GOV | 254 counties x 5 candidates |
| PASS | statewide reconciliation | 2014-GOV | county sums == source statewide total for all 5 candidates (exact) |
| PASS | completeness | 2014-SEN | 254 counties x 5 candidates |
| PASS | statewide reconciliation | 2014-SEN | county sums == source statewide total for all 5 candidates (exact) |
| PASS | completeness | 2016-PRES | 254 counties x 17 candidates |
| PASS | cross-check MIT | 2016-PRES | all 254 counties match exactly by party bucket ['DEM', 'OTHER', 'REP'] |
| PASS | statewide reconciliation | 2016-PRES | county sums == source statewide total for all 17 candidates (exact) |
| PASS | completeness | 2018-GOV | 254 counties x 3 candidates |
| PASS | statewide reconciliation | 2018-GOV | county sums == source statewide total for all 3 candidates (exact) |
| PASS | completeness | 2018-SEN | 254 counties x 3 candidates |
| PASS | statewide reconciliation | 2018-SEN | county sums == source statewide total for all 3 candidates (exact) |
| WARN | statewide reconciliation | 2020-PRES | source (sos_xlsx) has no statewide row; relies on independent cross-check |
| INFO | compare OpenElections | 2020-PRES | county totals: 82 exact, 118 within 0.1%, 8 missing in OE, 128 differ (OE quality issue, not used as a gate) |
| PASS | completeness | 2020-PRES | 254 counties x 13 candidates |
| PASS | cross-check MIT | 2020-PRES | all 254 counties match exactly by party bucket ['DEM', 'GRN', 'LIB', 'OTHER', 'REP'] |
| WARN | statewide reconciliation | 2020-SEN | source (sos_xlsx) has no statewide row; relies on independent cross-check |
| INFO | compare OpenElections | 2020-SEN | county totals: 103 exact, 176 within 0.1%, 9 missing in OE, 69 differ (OE quality issue, not used as a gate) |
| PASS | completeness | 2020-SEN | 254 counties x 5 candidates |
| WARN | statewide reconciliation | 2022-GOV | source (sos_xlsx) has no statewide row; relies on independent cross-check |
| INFO | compare OpenElections | 2022-GOV | county totals: 32 exact, 96 within 0.1%, 153 missing in OE, 5 differ (OE quality issue, not used as a gate) |
| PASS | completeness | 2022-GOV | 254 counties x 6 candidates |
| WARN | statewide reconciliation | 2024-PRES | source (sos_xlsx) has no statewide row; relies on independent cross-check |
| PASS | completeness | 2024-PRES | 254 counties x 10 candidates |
| PASS | cross-check MIT | 2024-PRES | all 254 counties match exactly by party bucket ['DEM', 'LIB', 'OTHER', 'REP'] |
| WARN | statewide reconciliation | 2024-SEN | source (sos_xlsx) has no statewide row; relies on independent cross-check |
| PASS | completeness | 2024-SEN | 254 counties x 5 candidates |
| WARN | statewide reconciliation | 2026-SEN | source (ddhq_csv) has no statewide row; relies on independent cross-check |
| WARN | status | 2026-SEN | UNOFFICIAL (ddhq_csv, ddhq/race_294702_2026-texas-us-senate.csv) |
| WARN | zero-vote counties | 2026-SEN | 1 counties with 0 votes (not yet reporting?): ['Lubbock'] |
| PASS | completeness | 2026-SEN | 254 counties x 3 candidates |
