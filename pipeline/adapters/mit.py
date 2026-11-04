"""MIT Election Data + Science Lab, County Presidential Returns 2000-2024. CROSS-CHECK ONLY.

Harvard Dataverse doi:10.7910/DVN/VOQCHQ (CC0), file countypres_2000-2024 (v20260225).
Downloaded by hand: Dataverse requires a guestbook form.

Uses mode == 'TOTAL' rows only (2024 also has 'EARLY VOTING' rows and a blank-mode
'TOTAL VOTES CAST' row). MIT groups minor candidates into party 'OTHER', and the set of
named parties varies by year (e.g. 2024 has no GREEN, so Stein is in OTHER), so the
comparison is per party bucket per county, not per candidate.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

DOI = "https://doi.org/10.7910/DVN/VOQCHQ"
PARTY = {"REPUBLICAN": "REP", "DEMOCRAT": "DEM", "LIBERTARIAN": "LIB", "GREEN": "GRN", "OTHER": "OTHER"}


def raw_path(raw_dir: Path) -> Path:
    return raw_dir / "mit" / "countypres_2000-2024.csv"


@lru_cache(maxsize=None)
def texas_buckets(path: Path):
    """-> ({(year, fips): Counter(bucket -> votes)}, {year: set(named buckets)})"""
    votes, buckets = defaultdict(Counter), defaultdict(set)
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["state_po"] != "TX" or r["mode"] != "TOTAL":
                continue
            b = PARTY[r["party"]]
            y = int(r["year"])
            votes[(y, r["county_fips"].zfill(5))][b] += int(r["candidatevotes"])
            buckets[y].add(b)
    return dict(votes), dict(buckets)


def bucket(party: str, named: set[str]) -> str:
    return party if party in named and party != "OTHER" else "OTHER"
