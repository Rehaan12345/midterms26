"""Download raw source files and record them in raw/manifest.csv. Raw files are never edited.

  python -m pipeline.fetch legacy     # SOS legacy HTML pages for 2008-2018 races (skips existing)
  python -m pipeline.fetch civix      # snapshot Civix ENR JSON for any races.csv rows with source sos_civix (none currently; 2026 removed)
  python -m pipeline.fetch register   # add manually placed files (Excel, Census, OpenElections) to manifest
"""
from __future__ import annotations

import csv
import sys
import time
import urllib.request
from datetime import datetime, timezone

from pipeline.adapters import ddhq_csv, mit, openelections, sos_civix, sos_legacy, sos_xlsx
from pipeline.common import RAW, REF, record

UA = {"User-Agent": "tx-county-results research pipeline (contact: anjaria@usc.edu)"}
CENSUS_URL = "https://www2.census.gov/geo/docs/reference/codes2020/cou/st48_tx_cou2020.txt"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 200:
            raise RuntimeError(f"{url}: HTTP {r.status}")
        return r.read()


def races(source: str):
    with (REF / "races.csv").open() as f:
        return [r for r in csv.DictReader(f) if r["source"] == source]


def fetch_legacy() -> None:
    for r in races("sos_legacy"):
        eid, rid = r["locator"].split(":")
        path = sos_legacy.raw_path(RAW, eid, rid)
        if path.exists():
            print(f"exists {path.name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(_get(sos_legacy.url(eid, rid)))
            print(f"fetched {path.name}")
            time.sleep(1)
        record(path, sos_legacy.url(eid, rid))


def fetch_civix() -> None:
    eids = sorted({r["locator"].split(":")[0] for r in races("sos_civix")})
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for eid in eids:
        snap = RAW / "sos_civix" / eid / stamp
        snap.mkdir(parents=True)
        for name, url in sos_civix.urls(eid).items():
            path = snap / f"{name}.json"
            path.write_bytes(_get(url))
            record(path, url, status="unofficial")
            time.sleep(1)
        home = sos_civix.load_election(snap / "election.json")["Home"]
        print(f"snapshot {snap.relative_to(RAW)}: counties {home['CountiesReporting']}, "
              f"polling places {home['PollingReporting']}, updated {home['LastUpdatedTime']}")


def register() -> None:
    for p in sorted((RAW / sos_xlsx.RAW_SUBDIR).glob("*.xlsx")):
        record(p, sos_xlsx.SITE)
    record(RAW / "census" / "st48_tx_cou2020.txt", CENSUS_URL)
    for p in sorted((RAW / ddhq_csv.RAW_SUBDIR).glob("*.csv")):
        record(p, ddhq_csv.SITE, status="unofficial")
    if mit.raw_path(RAW).exists():
        record(mit.raw_path(RAW), f"{mit.DOI} (manual download, Dataverse guestbook)", status="cross-check")
    for year, rel in openelections.FILES.items():
        p = openelections.raw_path(RAW, year)
        if p.exists():
            record(p, f"{openelections.REPO}/{rel}", status="cross-check")
    print("manifest updated")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"legacy": fetch_legacy, "civix": fetch_civix, "register": register}.get(
        cmd, lambda: sys.exit(__doc__))()
