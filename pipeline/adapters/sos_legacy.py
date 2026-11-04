"""Texas SOS legacy archive (1992-2019): static HTML county-by-county tables.

URL: https://elections.sos.state.tx.us/elchist{election_id}_race{race_id}.htm
Table layout (verified on all 10 race pages, 2008-2018):
  row 0: candidate name, first line ('...' in non-candidate columns)
  row 1: candidate name, second line (blank when it fit on one line)
  row 2: 'County' | party per candidate (REP/DEM/LIB/GRN/W-I) | 'Votes' | 'Voters' | 'TurnOut'
  row 3: 'ALL COUNTIES' statewide totals
  rows 4..257: one row per county
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from pipeline.common import Row, norm_ws, parse_int

BASE = "https://elections.sos.state.tx.us"
TRAILING = {"Votes", "Voters", "TurnOut"}


def url(election_id: str, race_id: str) -> str:
    return f"{BASE}/elchist{election_id}_race{race_id}.htm"


def raw_path(raw_dir: Path, election_id: str, race_id: str) -> Path:
    return raw_dir / "sos_legacy" / f"elchist{election_id}_race{race_id}.htm"


def _cells(tr: str) -> list[str]:
    return [norm_ws(html.unescape(re.sub(r"<[^>]+>", " ", c)))
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]


def parse(path: Path, year: int, office: str):
    text = path.read_text(encoding="latin-1")
    rows = [_cells(tr) for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S | re.I)]
    name1, name2, parties = rows[0], rows[1], rows[2]
    if parties[0] != "County":
        raise ValueError(f"{path}: unexpected header {parties[:3]}")
    cand_cols = [i for i in range(1, len(parties)) if parties[i] not in TRAILING]
    if not cand_cols or cand_cols != list(range(1, len(cand_cols) + 1)):
        raise ValueError(f"{path}: candidate columns not contiguous: {parties}")
    votes_col = parties.index("Votes")

    cands = []
    for i in cand_cols:
        name = norm_ws(f"{name1[i]} {name2[i] if i < len(name2) else ''}")
        name = re.sub(r"\s*/\s*", " / ", name).strip(" /")
        cands.append((name, parties[i]))

    out, statewide, county_totals = [], None, {}
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        values = [parse_int(r[i]) for i in cand_cols]
        total = parse_int(r[votes_col])
        if sum(values) != total:
            raise ValueError(f"{path}: {r[0]} candidates sum {sum(values)} != Total Votes {total}")
        if r[0] == "ALL COUNTIES":
            statewide = {c[0]: v for c, v in zip(cands, values)}
            continue
        county_totals[r[0]] = total
        for (name, party), v in zip(cands, values):
            out.append(Row(year, office, r[0], name, party, v))
    if statewide is None:
        raise ValueError(f"{path}: no ALL COUNTIES row")
    return out, statewide
