"""OpenElections TX precinct CSVs, rolled up to county. CROSS-CHECK ONLY, never the primary source.

Used for (a) independent county-total cross-checks for 2020/2022 and (b) a party label
for each candidate in the SOS Excel years, which have no party column.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from pipeline.common import norm_ws

REPO = "https://raw.githubusercontent.com/openelections/openelections-data-tx/master"
FILES = {
    2020: "2020/20201103__tx__general__precinct.csv",
    2022: "2022/20221108__tx__general__precinct.csv",
    2024: "2024/counties/20241105__tx__general__harris__precinct.csv",  # party labels only
}
CROSSCHECK_YEARS = {2020, 2022}  # statewide files; 2024 here is Harris County only
# OpenElections office labels vary by county (2020 alone has 8 spellings of
# President/Senate: "President / Vice-President", "US Senator", "Governor ( 1)", ...).
OFFICE_PATTERNS = [
    (re.compile(r"^president\b"), "PRES"),
    (re.compile(r"^u\.?\s?s\.?\s?senat"), "SEN"),
    (re.compile(r"^governor\b"), "GOV"),
]


def classify_office(label: str) -> str | None:
    s = norm_ws(label).lower()
    for pat, office in OFFICE_PATTERNS:
        if pat.search(s):
            return office
    return None


def raw_path(raw_dir: Path, year: int) -> Path:
    return raw_dir / "openelections" / Path(FILES[year]).name


@lru_cache(maxsize=None)
def county_candidate_totals(path: Path) -> dict[tuple[str, str, str], tuple[str, int]]:
    """(office, county, candidate) -> (party, votes), for PRES/SEN/GOV only."""
    acc: dict[tuple[str, str, str], list] = defaultdict(lambda: ["", 0])
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            office = classify_office(r["office"])
            if not office:
                continue
            cand = norm_ws(r["candidate"])
            if not cand or cand.upper() in {"NA", "OVER VOTES", "UNDER VOTES"}:
                continue
            v = norm_ws(r.get("votes")).replace(",", "")
            if not re.fullmatch(r"\d+", v):
                continue
            k = (office, norm_ws(r["county"]), cand)
            acc[k][0] = acc[k][0] or norm_ws(r["party"])
            acc[k][1] += int(v)
    return {k: (p, v) for k, (p, v) in acc.items()}
