"""Texas SOS Civix ENR (2025-): JSON API behind goelect.txelections.civixapps.com.

  /electionConstants                 {"upload": base64(JSON)}: election list
  /election/{id}                     every top-level value is base64(JSON); has StateWide/Federal races
  /election/countyInfo/{id}          {"upload": base64(JSON)}: {"1".."254": {N, Races: {...}}}

County ids are the alphabetical index 1..254. The adapter returns the county name;
build.py separately checks that 48 + (id*2-1) equals the Census FIPS for that name.
"""
from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path

from pipeline.common import Row, norm_ws

BASE = "https://goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr"


def urls(election_id: str) -> dict[str, str]:
    return {
        "election": f"{BASE}/election/{election_id}",
        "countyInfo": f"{BASE}/election/countyInfo/{election_id}",
    }


def _b64json(v):
    """Most values are base64(JSON); a few (e.g. Version 'enr/53815/58/') are plain strings."""
    if not isinstance(v, str):
        return v
    try:
        return json.loads(base64.b64decode(v, validate=True))
    except (binascii.Error, ValueError):
        return v


def load_election(path: Path) -> dict:
    return {k: _b64json(v) for k, v in json.loads(path.read_text()).items()}


def load_county_info(path: Path) -> dict:
    return _b64json(json.loads(path.read_text())["upload"])


def latest_snapshot(raw_dir: Path, election_id: str) -> Path:
    snaps = sorted((raw_dir / "sos_civix" / election_id).glob("*/"))
    if not snaps:
        raise FileNotFoundError(f"no Civix snapshots for {election_id}; run fetch civix")
    return snaps[-1]


def parse(snapshot: Path, year: int, office: str, race_name: str):
    want = norm_ws(race_name).upper()
    election = load_election(snapshot / "election.json")
    counties = load_county_info(snapshot / "countyInfo.json")

    statewide = None
    for section in ("StateWide", "Federal"):
        for race in election[section]["Races"]:
            if norm_ws(race["N"]).upper() == want:
                statewide = {norm_ws(c["N"]): c["V"] for c in race["Candidates"]}
    if statewide is None:
        raise ValueError(f"{snapshot}: race {race_name!r} not in statewide/federal sections")

    out, county_ids = [], {}
    for cid, county in counties.items():
        county_ids[county["N"]] = int(cid)
        races = [r for r in county["Races"].values() if norm_ws(r["N"]).upper() == want]
        if len(races) != 1:
            raise ValueError(f"{snapshot}: county {county['N']} has {len(races)} {race_name!r} races")
        for c in races[0]["C"].values():
            out.append(Row(year, office, county["N"], norm_ws(c["N"]), c["P"], int(c["V"])))
    meta = {"home": election["Home"], "version": election["Version"], "county_ids": county_ids}
    return out, statewide, meta
