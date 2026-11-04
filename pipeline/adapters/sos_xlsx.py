"""Texas SOS results.texas-election.com (2019-2024) whole-election Excel exports.

These were downloaded by hand: the site is behind a Cloudflare bot challenge.
Sheet 'Voter Turnout Report', long format:
  ELECTION DATE-NAME | OFFICE NAME | CANDIDATE NAME | COUNTY NAME | TOTAL VOTES PER OFFICE PER COUNTY
No party column, so party comes from reference/candidates.csv. The export has no
statewide totals row either, so reconciliation is against independent sources only.
"""
from __future__ import annotations

import warnings
from functools import lru_cache
from pathlib import Path

import openpyxl

from pipeline.common import Row, norm_ws, parse_int

HEADER = ["ELECTION DATE-NAME", "OFFICE NAME", "CANDIDATE NAME", "COUNTY NAME",
          "TOTAL VOTES PER OFFICE PER COUNTY"]
SITE = "https://results.texas-election.com/races (manual download, Cloudflare-gated)"
RAW_SUBDIR = "sos_tx_election"


@lru_cache(maxsize=None)
def _load(path: Path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # "Workbook contains no default style"
        ws = openpyxl.load_workbook(path, read_only=False, data_only=True).active
    rows = [tuple(norm_ws(str(c)) if c is not None else "" for c in r)
            for r in ws.iter_rows(values_only=True)]
    if list(rows[0][:5]) != HEADER:
        raise ValueError(f"{path}: unexpected header {rows[0]}")
    return rows[1:]


def parse(path: Path, year: int, office: str, office_name: str):
    want = norm_ws(office_name).upper()
    out = []
    for r in _load(path):
        if r[1].upper() != want:
            continue
        out.append(Row(year, office, r[3], r[2], "", parse_int(r[4])))
    if not out:
        raise ValueError(f"{path}: no rows for office {office_name!r}")
    return out, None
