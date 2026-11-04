"""Shared helpers: paths, name normalization, county crosswalk, raw-file manifest."""
from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
REF = ROOT / "reference"
DATA = ROOT / "data"
MANIFEST = RAW / "manifest.csv"
MANIFEST_FIELDS = ["path", "source_url", "fetched_at", "sha256", "status"]

OFFICES = {"PRES", "SEN", "GOV"}


@dataclass(frozen=True)
class Row:
    """One candidate's votes in one county for one race, as the source reported it."""
    year: int
    office: str
    county_raw: str
    candidate_raw: str
    party_raw: str  # "" when the source has no party (sos_xlsx)
    votes: int


def norm_ws(s: str | None) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def parse_int(s) -> int:
    if isinstance(s, int):
        return s
    t = norm_ws(str(s)).replace(",", "")
    if not re.fullmatch(r"\d+", t):
        raise ValueError(f"not a vote count: {s!r}")
    return int(t)


def county_key(name: str) -> str:
    """'DE WITT' / 'DeWitt County' / 'La Salle' -> 'DEWITT' / 'LASALLE'."""
    n = norm_ws(name).upper()
    n = re.sub(r"\s+COUNTY$", "", n)
    return re.sub(r"[^A-Z]", "", n)


def load_counties() -> dict[str, tuple[str, str]]:
    """county_key -> (fips, census name). Source: Census 2020 county codes for Texas."""
    out = {}
    path = RAW / "census" / "st48_tx_cou2020.txt"
    with path.open() as f:
        for r in csv.DictReader(f, delimiter="|"):
            name = re.sub(r"\s+County$", "", r["COUNTYNAME"])
            out[county_key(name)] = (r["STATEFP"] + r["COUNTYFP"], name)
    if len(out) != 254:
        raise RuntimeError(f"expected 254 Texas counties in {path}, got {len(out)}")
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def record(path: Path, source_url: str, status: str = "ok") -> None:
    """Append (or refresh) a manifest row for a raw file."""
    rel = str(path.relative_to(ROOT))
    rows = []
    if MANIFEST.exists():
        with MANIFEST.open() as f:
            rows = [r for r in csv.DictReader(f) if r["path"] != rel]
    rows.append({
        "path": rel,
        "source_url": source_url,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": sha256(path),
        "status": status,
    })
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["path"]))
