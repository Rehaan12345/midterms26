"""Decision Desk HQ county CSV export (votes.decisiondeskhq.com). UNOFFICIAL results.

Wide format, one row per county: county_name, <candidate>, <candidate>, ...
No party column (party comes from reference/candidates.csv), no write-ins, no
statewide row, no timestamp. A county with every cell 0 has not reported.
"""
from __future__ import annotations

import csv
from pathlib import Path

from pipeline.common import Row, norm_ws, parse_int

SITE = "https://votes.decisiondeskhq.com/ (user-provided CSV export, unofficial)"
RAW_SUBDIR = "ddhq"


def parse(path: Path, year: int, office: str):
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or reader.fieldnames[0] != "county_name":
            raise ValueError(f"{path}: expected first column county_name, got {reader.fieldnames}")
        cands = [norm_ws(c) for c in reader.fieldnames[1:]]
        out = []
        for r in reader:
            for raw_name, cand in zip(reader.fieldnames[1:], cands):
                out.append(Row(year, office, norm_ws(r["county_name"]), cand, "", parse_int(r[raw_name])))
    return out, None
