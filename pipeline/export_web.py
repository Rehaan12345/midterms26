"""Export data/texas.sqlite to static JSON for the web map.

  python -m pipeline.export_web

Writes web/public/data/races.json (index + statewide summaries) and
web/public/data/results/{race_id}.json (per-county results).
"""
from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter

from pipeline.adapters import sos_civix
from pipeline.common import DATA, RAW, REF, ROOT

OUT = ROOT / "web" / "public" / "data"
OFFICE_LABEL = {"PRES": "President", "SEN": "U.S. Senate", "GOV": "Governor"}
SOURCE_LABEL = {"sos_legacy": "Texas Secretary of State", "sos_xlsx": "Texas Secretary of State",
                "sos_civix": "Texas Secretary of State", "ddhq_csv": "Decision Desk HQ"}


def civix_meta(locator: str) -> dict:
    eid = locator.split(":")[0]
    snap = sos_civix.latest_snapshot(RAW, eid)
    home = sos_civix.load_election(snap / "election.json")["Home"]
    return {
        "sosUpdated": home["LastUpdatedTime"],  # SOS timestamp, appears to be UTC
        "countiesReporting": home["CountiesReporting"]["CR"],
        "countiesTotal": home["CountiesReporting"]["CT"],
        "snapshot": snap.name,
    }


def main() -> None:
    db = sqlite3.connect(DATA / "texas.sqlite")
    db.row_factory = sqlite3.Row
    (OUT / "results").mkdir(parents=True, exist_ok=True)
    with (REF / "races.csv").open() as f:
        locators = {f"{r['year']}-{r['office']}": r["locator"] for r in csv.DictReader(f)}

    index = []
    races = db.execute("""SELECT r.race_id, r.office, r.source, e.date, e.status
                          FROM races r JOIN elections e USING (election_id) ORDER BY r.race_id""").fetchall()
    for race in races:
        rid = race["race_id"]
        rows = db.execute("""SELECT county_fips, candidate_id, votes FROM county_results
                             WHERE race_id = ? ORDER BY county_fips, votes DESC""", (rid,)).fetchall()
        cand_ids = sorted({r["candidate_id"] for r in rows})
        cands = {r["candidate_id"]: {"name": r["name"], "party": r["party"]} for r in db.execute(
            f"SELECT * FROM candidates WHERE candidate_id IN ({','.join('?' * len(cand_ids))})", cand_ids)}

        counties: dict[str, dict] = {}
        statewide = Counter()
        for r in rows:
            c = counties.setdefault(r["county_fips"], {"total": 0, "results": []})
            c["total"] += r["votes"]
            c["results"].append([r["candidate_id"], r["votes"]])
            statewide[r["candidate_id"]] += r["votes"]

        won = Counter()
        for c in counties.values():
            if c["total"] > 0:
                won[cands[c["results"][0][0]]["party"]] += 1
        total = sum(statewide.values())
        entry = {
            "id": rid,
            "year": int(rid[:4]),
            "office": race["office"],
            "officeLabel": OFFICE_LABEL[race["office"]],
            "date": race["date"],
            "status": race["status"],
            "source": race["source"],
            "sourceLabel": SOURCE_LABEL[race["source"]],
            "countiesReported": sum(1 for c in counties.values() if c["total"] > 0),
            "total": total,
            "countiesWon": dict(won),
            "statewide": [
                {"id": cid, **cands[cid], "votes": v, "pct": round(100 * v / total, 2) if total else 0}
                for cid, v in statewide.most_common()
            ],
        }
        if race["source"] == "sos_civix":
            entry["live"] = civix_meta(locators[rid])
        index.append(entry)
        (OUT / "results" / f"{rid}.json").write_text(
            json.dumps({"id": rid, "candidates": cands, "counties": counties}, separators=(",", ":")))

    (OUT / "races.json").write_text(json.dumps(index, indent=1))
    print(f"wrote {len(index)} races to {OUT}")


if __name__ == "__main__":
    main()
