"""Export data/mi_senate_2026_finance/ to web/public/data/mi-finance.json for the Michigan tab.

Deterministic, no network. Run after build.py:  python3 -I finance_mi/export_web.py
"""
from __future__ import annotations

import csv
import json
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "mi_senate_2026_finance"
WEB = ROOT / "web" / "public" / "data"

# USPS -> 2-digit FIPS for the 50 states + DC (us-atlas ids are FIPS).
FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08", "CT": "09", "DE": "10", "DC": "11",
    "FL": "12", "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21",
    "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29", "MT": "30",
    "NE": "31", "NV": "32", "NH": "33", "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49",
    "VT": "50", "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
}

CANDS = [
    {"key": "el_sayed", "cand_id": "S6MI00418", "name": "Abdul El-Sayed", "short": "El-Sayed", "party": "DEM",
     "committee": "Abdul for US Senate"},
    {"key": "rogers", "cand_id": "S4MI00595", "name": "Mike Rogers", "short": "Rogers", "party": "REP",
     "committee": "Mike Rogers for Senate"},
]


# Display names for outside groups, from the FEC's own committee names (cleaned of filing suffixes).
DISPLAY = {
    "UNITED DEMOCRACY PROJECT (UDP)": "United Democracy Project (AIPAC’s super PAC)",
    "Americans for Prosperity Action, Inc. (AFP Action) DBA CVA Action and DBA LIBRE Action": "Americans for Prosperity Action",
    "NO GOING BACK PAC INC.": "No Going Back PAC",
    "GLCF, INC.": "GLCF, Inc.",
    "TOGETHER FOR MICHIGAN": "Together for Michigan",
    "FIGHTING FOR MICHIGAN PAC": "Fighting for Michigan PAC",
    "TFM": "Together for Michigan",
    "CFFE PAC": "CFFE PAC",
    "AB PAC": "AB PAC",
}


def display(n: str) -> str:
    if n in DISPLAY:
        return DISPLAY[n]
    return nice(n)


SMALL = {"of", "for", "and", "the", "to", "in", "on", "a", "an", "by"}
ACRONYMS = {"NORPAC", "(RJC-PAC)", "RJC-PAC", "US", "USA", "AIPAC", "DSCC", "NRSC", "LLC", "II", "III", "SEIU", "UAW", "AFL-CIO", "AFSCME", "IBEW", "NEA"}


def nice(n: str) -> str:
    """FEC names arrive in capitals; lower them for reading, keeping acronyms and small words."""
    if not n.isupper():
        return n
    out = []
    for i, w in enumerate(n.split()):
        bare = w.strip(",.")
        if bare.strip("()") in ACRONYMS or bare.split("-")[-1] == "PAC":
            out.append(w); continue
        bare = bare.strip("()")
        if bare in ACRONYMS:
            out.append(w)
        elif i and bare.lower() in SMALL:
            out.append(w.lower())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def rows(name):
    with (SRC / name).open() as f:
        return list(csv.DictReader(f))


def f(x) -> float:
    return round(float(x), 2)


def main():
    summary = json.loads((SRC / "summary.json").read_text())
    totals = {r["cand_id"]: r for r in rows("totals.csv")}
    states = rows("individuals_by_state.csv")
    outside = rows("outside_spending.csv")
    cmte = rows("committee_money.csv")
    out = []
    for c in CANDS:
        t = totals[c["cand_id"]]
        s = summary["candidates"][c["key"]]
        itemized = s["individuals"]["itemized_gross"]
        indiv = f(t["individual_contributions"])
        unitemized = round(indiv - itemized, 2)
        by_state, elsewhere = {}, 0.0
        for r in states:
            if r["candidate"] != c["name"]:
                continue
            if r["state"] in FIPS:
                by_state[FIPS[r["state"]]] = {"st": r["state"], "amount": f(r["amount"])}
            else:
                elsewhere += float(r["amount"])
        pacs = sorted([r for r in cmte if r["cand_id"] == c["cand_id"] and r["line"] == "PAC / other committee"],
                      key=lambda r: -float(r["amount"]))
        jfc = sorted([r for r in cmte if r["cand_id"] == c["cand_id"] and r["line"].startswith("transfer")],
                     key=lambda r: -float(r["amount"]))
        o = defaultdict(lambda: {"primary": 0.0, "general": 0.0, "groups": {}})
        for r in outside:
            if r["cand_id"] != c["cand_id"]:
                continue
            side = o[r["support_oppose"]]
            side[r["election"]] += float(r["amount"])
            g = side["groups"].setdefault(display(r["spender"]), {"primary": 0.0, "general": 0.0})
            g[r["election"]] += float(r["amount"])
        out.append({
            **{k: c[k] for k in ("key", "name", "short", "party", "committee")},
            "candId": c["cand_id"],
            "coverageEnd": t["coverage_end"],
            "total": f(t["total_receipts"]),
            "cashOnHand": f(t["cash_on_hand_end"]),
            "sources": [
                {"id": "small", "label": "Individuals, $200 or less", "amount": unitemized,
                 "note": "Small gifts. Campaigns report only the total, with no names or addresses."},
                {"id": "large", "label": "Individuals, over $200", "amount": f(itemized),
                 "note": "Itemized: every donor named, with city and state."},
                {"id": "jfc", "label": "Joint fundraising transfers", "amount": f(t["transfers_from_joint_fundraising_and_other_authorized"]),
                 "note": f"Raised by shared committees and passed on. Largest: {nice(jfc[0]['from'])}." if jfc else ""},
                {"id": "pac", "label": "PACs and other committees", "amount": f(t["pac_and_other_committee_contributions"]),
                 "note": f"{len(pacs)} committees. Largest: {nice(pacs[0]['from'])} (${float(pacs[0]['amount']):,.0f})." if pacs else ""},
                {"id": "party", "label": "Party committees", "amount": f(t["party_committee_contributions"]), "note": ""},
                {"id": "self", "label": "The candidate’s own money", "amount": f(t["candidate_self_funding"]), "note": ""},
            ],
            "individualsTotal": indiv,
            "otherReceipts": 0.0,
            "itemized": f(itemized),
            "donors": s["individuals"]["unique_donors_name_zip"],
            "states": by_state,
            "elsewhere": round(elsewhere, 2),
            "outside": {
                side: {
                    "primary": round(o[side]["primary"], 2), "general": round(o[side]["general"], 2),
                    "groups": [{"name": n, "primary": round(v["primary"], 2), "general": round(v["general"], 2),
                                "amount": round(v["primary"] + v["general"], 2)}
                               for n, v in sorted(o[side]["groups"].items(), key=lambda x: -(x[1]["primary"] + x[1]["general"]))[:5]],
                    "groupCount": len(o[side]["groups"]),
                } for side in ("support", "oppose")
            },
        })
    # Pro-Israel committees: the 44 tracked by Who Funded Genocide's US board, matched by name.
    PRO = ("UNITED DEMOCRACY PROJECT", "AIPAC", "AMERICAN ISRAEL PUBLIC", "DMFI", "DEMOCRATIC MAJORITY FOR ISRAEL",
           "REPUBLICAN JEWISH COALITION", "RJC", "NORPAC", "GRAND CANYON STATE CAUCUS", "PRO-ISRAEL AMERICA",
           "JOINT ACTION COMMITTEE", "PRESERVE AMERICA", "U.S. ISRAEL PAC", "ZIONESS", "DESERT CAUCUS")
    pro = lambda n: any(k in n.upper() and "AGAINST AIPAC" not in n.upper() for k in PRO)
    for c in out:
        cid, items = c["candId"], []
        for r in cmte:
            if r["cand_id"] == cid and pro(r["from"]):
                items.append({"kind": "given", "name": nice(r["from"]), "how": "direct", "amount": f(r["amount"])})
        for k, v in summary["candidates"][c["key"]]["individuals"]["earmarked_by_conduit"].items():
            if pro(k):
                items.append({"kind": "given", "name": nice(k), "how": "passed on from its donors", "amount": round(v, 2)})
        for r in outside:
            if r["cand_id"] == cid and pro(r["spender"]):
                items.append({"kind": "help" if r["support_oppose"] == "support" else "against",
                              "name": display(r["spender"]), "how": r["election"], "amount": f(r["amount"])})
        for it in items:
            if "REPUBLICAN JEWISH COALITION" in it["name"].upper() and it["kind"] == "given":
                it["name"] = "Republican Jewish Coalition PAC"
        c["proIsrael"] = sorted(items, key=lambda x: -x["amount"])
    for c in out:  # whatever the line items don't explain: refunds, interest, offsets (F3 lines 15-17)
        rest = round(c["total"] - sum(x["amount"] for x in c["sources"]), 2)
        c["sources"].append({"id": "other", "label": "Other receipts", "amount": rest,
                             "note": "Refunds, offsets and interest the campaign reported as receipts."})
        c["otherReceipts"] = rest
    WEB.mkdir(parents=True, exist_ok=True)
    doc = {
        "race": "U.S. Senate · Michigan · 2026",
        "outsideThrough": "2026-11-02",
        "candidates": out,
        "notes": {
            "dsccAgainstRogers": 12332947.0,
        },
    }
    (WEB / "mi-finance.json").write_text(json.dumps(doc, separators=(",", ":")))
    shutil.copy(ROOT / "web" / "node_modules" / "us-atlas" / "states-albers-10m.json", WEB / "us-states-albers.json")
    for c in out:
        print(c["short"], c["total"], [(s["id"], s["amount"]) for s in c["sources"]], "states", len(c["states"]), "elsewhere", c["elsewhere"])


if __name__ == "__main__":
    main()
