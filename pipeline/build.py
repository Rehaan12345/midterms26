"""Build data/texas.sqlite from raw sources and run the verification checks.

  python -m pipeline.build --draft-candidates   # write reference/candidates.draft.csv for human review
  python -m pipeline.build                      # build DB + data/checks.md; exit 1 if any FAIL

Deterministic only: no fuzzy matching in the build. Candidate names resolve through the
hand-reviewed reference/candidates.csv; county names resolve through the Census list.
"""
from __future__ import annotations

import csv
import re
import sqlite3
import sys
from collections import Counter, defaultdict

from pipeline.adapters import ddhq_csv, mit, openelections, sos_civix, sos_legacy, sos_xlsx
from pipeline.common import DATA, RAW, REF, county_key, load_counties, norm_ws

PARTY_MAP = {"REP": "REP", "DEM": "DEM", "LIB": "LIB", "L": "LIB", "LBT": "LIB",
             "GRN": "GRN", "G": "GRN", "GRE": "GRN",
             "W-I": "WRI", "W": "WRI", "W/I": "WRI", "IND": "IND"}
NO_LABEL = {"", "NA", "ONA"}  # OpenElections placeholders meaning "no party recorded"
DOMINANT_SHARE = 0.95
CANDIDATE_FIELDS = ["year", "office", "source_name", "candidate_id", "name", "party", "party_source"]
CROSSCHECK_TOLERANCE = 0.001  # 0.1% of a county's race total


# ---------------------------------------------------------------- extraction

def load_races():
    with (REF / "races.csv").open() as f:
        return [dict(r, year=int(r["year"])) for r in csv.DictReader(f)]


def extract(race):
    """-> (rows, statewide_reported | None, meta)"""
    src, loc, year, office = race["source"], race["locator"], race["year"], race["office"]
    if src == "sos_legacy":
        eid, rid = loc.split(":")
        rows, sw = sos_legacy.parse(sos_legacy.raw_path(RAW, eid, rid), year, office)
        return rows, sw, {"raw": f"elchist{eid}_race{rid}.htm"}
    if src == "sos_xlsx":
        fname, office_name = loc.split(":", 1)
        rows, sw = sos_xlsx.parse(RAW / sos_xlsx.RAW_SUBDIR / fname, year, office, office_name)
        return rows, sw, {"raw": fname}
    if src == "sos_civix":
        eid, name = loc.split(":", 1)
        snap = sos_civix.latest_snapshot(RAW, eid)
        rows, sw, meta = sos_civix.parse(snap, year, office, name)
        meta["raw"] = str(snap.relative_to(RAW))
        return rows, sw, meta
    if src == "ddhq_csv":
        rows, sw = ddhq_csv.parse(RAW / ddhq_csv.RAW_SUBDIR / loc, year, office)
        return rows, sw, {"raw": f"{ddhq_csv.RAW_SUBDIR}/{loc}"}
    raise ValueError(f"unknown source {src}")


# ---------------------------------------------------------------- candidates

def surname(name: str) -> str:
    first_person = re.split(r"\s*/\s*", norm_ws(name))[0]
    first_person = re.sub(r"\(.*?\)|\".*?\"|\b(JR|SR|II|III)\b\.?", " ", first_person, flags=re.I)
    tokens = re.findall(r"[A-Za-z'\-]+", first_person)
    return tokens[-1].upper().replace("'", "") if tokens else ""


def display(name: str) -> str:
    n = norm_ws(name)
    if n.isupper():
        n = n.title()
        n = re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), n)
        n = re.sub(r"\b(Jd|Ii|Iii)\b", lambda m: m.group(1).upper(), n)
    return re.sub(r"\s*/\s*", " / ", n)


def oe_party_index():
    """(year, office) -> {surname: [(oe_name, party, statewide_votes)]} from OpenElections."""
    idx = {}
    for year in openelections.FILES:
        path = openelections.raw_path(RAW, year)
        if not path.exists():
            continue
        tot = defaultdict(lambda: ["", 0])
        for (office, _county, cand), (party, v) in openelections.county_candidate_totals(path).items():
            tot[(office, cand)][0] = tot[(office, cand)][0] or party
            tot[(office, cand)][1] += v
        for (office, cand), (party, v) in tot.items():
            idx.setdefault((year, office), defaultdict(list))[surname(cand)].append((cand, party, v))
    return idx


def party_from_oe(matches):
    """Vote-weighted party label across OpenElections rows sharing this surname.

    -> (party, provenance). Candidates with no party label anywhere in OpenElections are
    marked WRI as an *inference* (TX ballot-listed parties for these races are REP/DEM/LIB/GRN),
    and the provenance says so.
    """
    if not matches:
        return "", "UNRESOLVED (no OpenElections match)"
    weights = Counter()
    for _name, p, v in matches:
        label = p.upper().strip()
        if label not in NO_LABEL:
            weights[PARTY_MAP.get(label, label)] += v
    labeled = sum(weights.values())
    if not labeled:
        return "WRI", "inferred write-in: no party label in OpenElections"
    party, v = weights.most_common(1)[0]
    if v / labeled >= DOMINANT_SHARE:
        return party, f"openelections ({v / labeled:.1%} of labeled votes)"
    return "", f"UNRESOLVED (conflicting OE labels {dict(weights)})"


def draft_candidates(extracted):
    oe = oe_party_index()
    out, used_ids = [], set()
    for race, (rows, _sw, _meta) in extracted:
        y, o = race["year"], race["office"]
        votes = Counter()
        party_raw = {}
        for r in rows:
            votes[r.candidate_raw] += r.votes
            party_raw.setdefault(r.candidate_raw, r.party_raw)
        for name, v in votes.most_common():
            sn = surname(name)
            cid = f"{y}-{o}-{sn.lower()}"
            if cid in used_ids:
                cid = f"{cid}-{len([u for u in used_ids if u.startswith(cid)]) + 1}"
            used_ids.add(cid)
            if party_raw[name]:
                party = PARTY_MAP.get(party_raw[name].upper(), "")
                psrc = "source" if party else f"UNMAPPED:{party_raw[name]}"
            else:
                party, psrc = party_from_oe(oe.get((y, o), {}).get(sn, []))
            out.append({"year": y, "office": o, "source_name": name, "candidate_id": cid,
                        "name": display(name), "party": party, "party_source": psrc})
    path = REF / "candidates.draft.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CANDIDATE_FIELDS)
        w.writeheader()
        w.writerows(out)
    unresolved = [c for c in out if not c["party"]]
    print(f"wrote {path} ({len(out)} candidates, {len(unresolved)} without a party)")
    for c in unresolved:
        print(f"  UNRESOLVED {c['year']} {c['office']} {c['source_name']!r} [{c['party_source']}]")


def load_candidates():
    path = REF / "candidates.csv"
    if not path.exists():
        sys.exit(f"{path} missing: run --draft-candidates, review, and save as candidates.csv")
    with path.open() as f:
        rows = list(csv.DictReader(f))
    bad = [r for r in rows if not r["party"]]
    if bad:
        sys.exit(f"{path}: {len(bad)} candidates have no party, e.g. {bad[0]['source_name']}")
    return {(int(r["year"]), r["office"], r["source_name"]): r for r in rows}


# ---------------------------------------------------------------- checks

class Checks:
    def __init__(self):
        self.items = []

    def add(self, status, check, race, detail):
        self.items.append((status, check, race, detail))

    @property
    def failed(self):
        return [i for i in self.items if i[0] == "FAIL"]


def oe_county_totals(year, office, fips_of):
    if year not in openelections.CROSSCHECK_YEARS:
        return None
    path = openelections.raw_path(RAW, year)
    if not path.exists():
        return None
    tot = Counter()
    for (o, county, _cand), (_p, v) in openelections.county_candidate_totals(path).items():
        if o == office:
            k = county_key(county)
            if k in fips_of:
                tot[fips_of[k][0]] += v
    return tot


def mit_check(year, rid, resolved, cands_by_id, checks: Checks):
    """Gate: every county's votes per party bucket must equal MIT's exactly."""
    path = mit.raw_path(RAW)
    if not path.exists():
        checks.add("WARN", "cross-check MIT", rid, f"{path.name} not downloaded; President unchecked")
        return
    mit_votes, named = mit.texas_buckets(path)
    if year not in named:
        checks.add("WARN", "cross-check MIT", rid, f"MIT has no {year} data")
        return
    ours = defaultdict(Counter)
    for r_id, fips, cid, v in resolved:
        if r_id == rid:
            ours[fips][mit.bucket(cands_by_id[cid]["party"], named[year])] += v
    bad = []
    for fips in set(ours) | {f for (y, f) in mit_votes if y == year}:
        theirs = mit_votes.get((year, fips), Counter())
        if ours[fips] != theirs:
            bad.append((fips, {b: (ours[fips][b], theirs[b]) for b in set(ours[fips]) | set(theirs)
                               if ours[fips][b] != theirs[b]}))
    if bad:
        checks.add("FAIL", "cross-check MIT", rid,
                   f"{len(bad)} counties differ (fips, {{bucket: (ours, MIT)}}): {sorted(bad)[:5]}")
    else:
        checks.add("PASS", "cross-check MIT", rid,
                   f"all 254 counties match exactly by party bucket {sorted(named[year])}")


# ---------------------------------------------------------------- build

def build(extracted, cands, counties, checks: Checks):
    resolved = []  # (race_id, fips, candidate_id, votes)
    counties_by_fips = dict(counties.values())
    cands_by_id = {c["candidate_id"]: c for c in cands.values()}
    for race, (rows, sw, meta) in extracted:
        rid = f"{race['year']}-{race['office']}"
        # county + candidate resolution: fail loudly on anything unknown
        seen = Counter()
        sums = Counter()
        unknown_c, unknown_k = set(), set()
        for r in rows:
            k = county_key(r.county_raw)
            if k not in counties:
                unknown_c.add(r.county_raw)
                continue
            ck = (r.year, r.office, r.candidate_raw)
            if ck not in cands:
                unknown_k.add(r.candidate_raw)
                continue
            fips = counties[k][0]
            cid = cands[ck]["candidate_id"]
            seen[(fips, cid)] += 1
            sums[r.candidate_raw] += r.votes
            resolved.append((rid, fips, cid, r.votes))
        if unknown_c:
            checks.add("FAIL", "county names", rid, f"unknown counties: {sorted(unknown_c)}")
        if unknown_k:
            checks.add("FAIL", "candidate names", rid, f"not in candidates.csv: {sorted(unknown_k)}")

        fips_set = {f for f, _ in seen}
        n_cands = len({c for _, c in seen})
        dups = [k for k, n in seen.items() if n > 1]
        if len(fips_set) == 254 and not dups and len(seen) == 254 * n_cands:
            checks.add("PASS", "completeness", rid, f"254 counties x {n_cands} candidates")
        else:
            checks.add("FAIL", "completeness", rid,
                       f"{len(fips_set)} counties, {len(seen)} cells (expected {254 * n_cands}), "
                       f"{len(dups)} duplicate cells")

        county_votes = Counter()
        for r_id, fips, _c, v in resolved:
            if r_id == rid:
                county_votes[fips] += v
        zero = sorted(counties_by_fips[f] for f in fips_set if county_votes[f] == 0)
        if zero:
            checks.add("FAIL" if race["status"] == "canvassed" else "WARN", "zero-vote counties", rid,
                       f"{len(zero)} counties with 0 votes (not yet reporting?): {zero}")

        if sw is not None:
            diffs = {c: (sw.get(c, 0), sums[c]) for c in set(sw) | set(sums) if sw.get(c, 0) != sums[c]}
            if diffs:
                checks.add("FAIL", "statewide reconciliation", rid, f"source statewide vs county sum: {diffs}")
            else:
                checks.add("PASS", "statewide reconciliation", rid,
                           f"county sums == source statewide total for all {len(sw)} candidates (exact)")
        else:
            checks.add("WARN", "statewide reconciliation", rid,
                       f"source ({race['source']}) has no statewide row; relies on independent cross-check")

        # Civix county ids are NOT usable as a FIPS formula: SOS sorts "Mc" literally while
        # Census FIPS sorts it as "Mac" (9 counties differ). Counties resolve by name only.

        if race["status"] != "canvassed":
            home = meta.get("home", {})
            checks.add("WARN", "status", rid,
                       f"UNOFFICIAL ({race['source']}, {meta['raw']})"
                       + (f", SOS updated {home.get('LastUpdatedTime')}, counties {home.get('CountiesReporting')}" if home else ""))

        if race["office"] == "PRES":
            mit_check(race["year"], rid, resolved, cands_by_id, checks)

        oe = oe_county_totals(race["year"], race["office"], counties)
        if oe is not None:
            ours = Counter()
            for r_id, fips, _c, v in resolved:
                if r_id == rid:
                    ours[fips] += v
            # INFO only: OpenElections has missing counties and apparent double-counting
            # (higher than the official canvass in 100+ counties), so it can't fail a build.
            exact = sum(1 for f, v in ours.items() if oe.get(f) == v)
            within = sum(1 for f, v in ours.items() if oe.get(f) and abs(oe[f] - v) / v <= CROSSCHECK_TOLERANCE)
            missing = sum(1 for f in ours if not oe.get(f))
            checks.add("INFO", "compare OpenElections", rid,
                       f"county totals: {exact} exact, {within} within 0.1%, {missing} missing in OE, "
                       f"{254 - within - missing} differ (OE quality issue, not used as a gate)")
    return resolved


def write_db(races, cands, counties, resolved):
    DATA.mkdir(exist_ok=True)
    path = DATA / "texas.sqlite"
    path.unlink(missing_ok=True)
    db = sqlite3.connect(path)
    db.executescript("""
    CREATE TABLE elections (election_id TEXT PRIMARY KEY, date TEXT, type TEXT, status TEXT);
    CREATE TABLE races (race_id TEXT PRIMARY KEY, election_id TEXT REFERENCES elections,
                        office TEXT, source TEXT, source_locator TEXT);
    CREATE TABLE candidates (candidate_id TEXT PRIMARY KEY, name TEXT, party TEXT);
    CREATE TABLE counties (county_fips TEXT PRIMARY KEY, name TEXT);
    CREATE TABLE county_results (race_id TEXT REFERENCES races, county_fips TEXT REFERENCES counties,
                                 candidate_id TEXT REFERENCES candidates, votes INTEGER NOT NULL,
                                 PRIMARY KEY (race_id, county_fips, candidate_id));
    CREATE VIEW county_results_pct AS
      SELECT cr.*, c.name AS candidate, c.party,
             SUM(votes) OVER (PARTITION BY race_id, county_fips) AS county_total,
             ROUND(100.0 * votes / NULLIF(SUM(votes) OVER (PARTITION BY race_id, county_fips), 0), 2) AS pct,
             -- no winner in a county that has reported 0 votes (unofficial nights)
             CASE WHEN SUM(votes) OVER (PARTITION BY race_id, county_fips) > 0
                  THEN RANK() OVER (PARTITION BY race_id, county_fips ORDER BY votes DESC) END AS place
      FROM county_results cr JOIN candidates c USING (candidate_id);
    """)
    for r in races:
        eid = f"{r['year']}-GE"
        db.execute("INSERT OR IGNORE INTO elections VALUES (?,?,?,?)",
                   (eid, r["election_date"], "general", r["status"]))
        db.execute("INSERT INTO races VALUES (?,?,?,?,?)",
                   (f"{r['year']}-{r['office']}", eid, r["office"], r["source"], r["locator"]))
    db.executemany("INSERT INTO candidates VALUES (?,?,?)",
                   sorted({(c["candidate_id"], c["name"], c["party"]) for c in cands.values()}))
    db.executemany("INSERT INTO counties VALUES (?,?)", sorted(set(counties.values())))
    db.executemany("INSERT INTO county_results VALUES (?,?,?,?)", resolved)
    db.commit()
    return path


def write_report(checks: Checks):
    DATA.mkdir(exist_ok=True)
    path = DATA / "checks.md"
    lines = ["# Verification report", "", "| status | check | race | detail |", "|---|---|---|---|"]
    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}
    for s, c, r, d in sorted(checks.items, key=lambda i: (i[2], order[i[0]], i[1])):
        lines.append(f"| {s} | {c} | {r} | {d.replace('|', '/')} |")
    path.write_text("\n".join(lines) + "\n")
    return path


def main():
    races = load_races()
    extracted = [(r, extract(r)) for r in races]
    if "--draft-candidates" in sys.argv:
        draft_candidates(extracted)
        return
    counties = load_counties()
    cands = load_candidates()
    checks = Checks()
    resolved = build(extracted, cands, counties, checks)
    report = write_report(checks)
    tally = Counter(s for s, *_ in checks.items)
    print(f"checks: {dict(tally)} -> {report}")
    for s, c, r, d in checks.items:
        if s != "PASS":
            print(f"  {s} {r} {c}: {d[:220]}")
    if checks.failed:
        sys.exit("build FAILED: database not written")
    print(f"wrote {write_db(races, cands, counties, resolved)} ({len(resolved):,} county_results rows)")


if __name__ == "__main__":
    main()
