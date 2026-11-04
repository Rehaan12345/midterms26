"""Michigan US Senate 2026: campaign finance for El-Sayed (D) and Rogers (R).

Deterministic: reads only files already in raw/ and writes CSVs + summary.json to
data/mi_senate_2026_finance/. No network calls. Run: python -I finance_mi/build.py

Sources, in order of priority (see finance_mi/SOURCES.md):
  1. raw/whofundedgenocide/   Who Funded Genocide "The Entire Network", Edition 1 (CC BY 4.0)
  2. raw/fec_mi_sen_2026/efile/ the campaigns' own e-filed F3 reports (most recent version of each),
     raw/fec_mi_sen_2026/bulk/ FEC bulk files (weball, cm, ccl, independent_expenditure)
  3. raw/fec_mi_sen_2026/api_*.json  FEC API aggregates, used only as cross-checks
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
FEC = RAW / "fec_mi_sen_2026"
BULK = FEC / "bulk"
WFG = RAW / "whofundedgenocide"
OUT = ROOT / "data" / "mi_senate_2026_finance"

CANDS = {
    "S6MI00418": {"key": "el_sayed", "name": "Abdul El-Sayed", "party": "DEM"},
    "S4MI00595": {"key": "rogers", "name": "Mike Rogers", "party": "REP"},
}

WEBALL = ("CAND_ID CAND_NAME CAND_ICI PTY_CD CAND_PTY_AFFILIATION TTL_RECEIPTS TRANS_FROM_AUTH "
          "TTL_DISB TRANS_TO_AUTH COH_BOP COH_COP CAND_CONTRIB CAND_LOANS OTHER_LOANS CAND_LOAN_REPAY "
          "OTHER_LOAN_REPAY DEBTS_OWED_BY TTL_INDIV_CONTRIB CAND_OFFICE_ST CAND_OFFICE_DISTRICT "
          "SPEC_ELECTION PRIM_ELECTION RUN_ELECTION GEN_ELECTION GEN_ELECTION_PRECENT "
          "OTHER_POL_CMTE_CONTRIB POL_PTY_CONTRIB CVG_END_DT INDIV_REFUNDS CMTE_REFUNDS").split()
CM = ("CMTE_ID CMTE_NM TRES_NM CMTE_ST1 CMTE_ST2 CMTE_CITY CMTE_ST CMTE_ZIP CMTE_DSGN CMTE_TP "
      "CMTE_PTY_AFFILIATION CMTE_FILING_FREQ ORG_TP CONNECTED_ORG_NM CAND_ID").split()
CCL = "CAND_ID CAND_ELECTION_YR FEC_ELECTION_YR CMTE_ID CMTE_TP CMTE_DSGN LINKAGE_ID".split()
PAS2 = ("CMTE_ID AMNDT_IND RPT_TP TRANSACTION_PGI IMAGE_NUM TRANSACTION_TP ENTITY_TP NAME CITY STATE "
        "ZIP_CODE EMPLOYER OCCUPATION TRANSACTION_DT TRANSACTION_AMT OTHER_ID CAND_ID TRAN_ID FILE_NUM "
        "MEMO_CD MEMO_TEXT SUB_ID").split()
ITCONT = ("CMTE_ID AMNDT_IND RPT_TP TRANSACTION_PGI IMAGE_NUM TRANSACTION_TP ENTITY_TP NAME CITY STATE "
          "ZIP_CODE EMPLOYER OCCUPATION TRANSACTION_DT TRANSACTION_AMT OTHER_ID TRAN_ID FILE_NUM "
          "MEMO_CD MEMO_TEXT SUB_ID").split()

ORG_TP = {"C": "Corporate PAC", "L": "Labor PAC", "M": "Membership PAC", "T": "Trade association PAC",
          "V": "Cooperative PAC", "W": "Corporation without stock PAC"}
PARTY_TP = {"X", "Y", "Z"}  # party committees (non-qualified, qualified, national non-federal)


def pipe_rows(path: Path, header: list[str]):
    with path.open(encoding="latin-1") as f:
        for line in f:
            parts = line.rstrip("\n").split("|")
            if len(parts) == len(header):
                yield dict(zip(header, parts))


def money(s) -> float:
    return float(s) if s not in ("", None) else 0.0


def write_csv(name: str, rows: list[dict], fields: list[str]):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})


# ---------------------------------------------------------------- committees
def load_committees():
    cm = {r["CMTE_ID"]: r for r in pipe_rows(BULK / "cm26" / "cm.txt", CM)}
    own = defaultdict(list)  # cand_id -> [(cmte_id, designation)]
    for r in pipe_rows(BULK / "ccl26" / "ccl.txt", CCL):
        if r["CAND_ID"] in CANDS:
            own[r["CAND_ID"]].append((r["CMTE_ID"], r["CMTE_DSGN"]))
    return cm, own


def committee_kind(c: dict | None) -> str:
    if not c:
        return "Unknown committee"
    if c["CMTE_TP"] in PARTY_TP:
        return "Party committee"
    if c["CMTE_DSGN"] == "D":
        return "Leadership PAC"
    if c["CMTE_DSGN"] in ("P", "A"):
        return "Candidate committee"
    if c["ORG_TP"] in ORG_TP:
        return ORG_TP[c["ORG_TP"]]
    if c["CMTE_TP"] in ("O", "U"):
        return "Super PAC"
    return "Unconnected PAC"


# ---------------------------------------------------------------- 1. totals
def totals():
    rows = []
    for r in pipe_rows(BULK / "weball26" / "weball26.txt", WEBALL):
        if r["CAND_ID"] not in CANDS:
            continue
        c = CANDS[r["CAND_ID"]]
        rows.append({
            "candidate": c["name"], "cand_id": r["CAND_ID"], "party": c["party"],
            "coverage_end": r["CVG_END_DT"],
            "total_receipts": money(r["TTL_RECEIPTS"]),
            "individual_contributions": money(r["TTL_INDIV_CONTRIB"]),
            "pac_and_other_committee_contributions": money(r["OTHER_POL_CMTE_CONTRIB"]),
            "party_committee_contributions": money(r["POL_PTY_CONTRIB"]),
            "transfers_from_joint_fundraising_and_other_authorized": money(r["TRANS_FROM_AUTH"]),
            "candidate_self_funding": money(r["CAND_CONTRIB"]) + money(r["CAND_LOANS"]),
            "other_loans": money(r["OTHER_LOANS"]),
            "total_disbursements": money(r["TTL_DISB"]),
            "cash_on_hand_start": money(r["COH_BOP"]),
            "cash_on_hand_end": money(r["COH_COP"]),
            "individual_refunds": money(r["INDIV_REFUNDS"]),
        })
    api = {r["candidate_id"]: r for r in json.loads((FEC / "api_cand_totals.json").read_text())["results"]}
    for r in rows:
        a = api.get(r["cand_id"], {})
        r["individual_itemized_api"] = a.get("individual_itemized_contributions") or 0.0
        r["individual_unitemized_derived"] = r["individual_contributions"] - r["individual_itemized_api"]
        r["check_api_receipts_match"] = abs((a.get("receipts") or 0) - r["total_receipts"]) < 1
    write_csv("totals.csv", rows, list(rows[0].keys()))
    return rows


# ---------------------------------------------------------------- 2. outside spending
def outside_spending():
    raw = [r for r in csv.DictReader((BULK / "independent_expenditure_2026.csv").open(encoding="latin-1"))]
    superseded = {r["prev_file_num"] for r in raw if r["prev_file_num"]}
    best = {}
    for r in raw:
        if r["cand_id"] not in CANDS or r["file_num"] in superseded:
            continue
        k = (r["spe_id"], r["tran_id"])
        if k not in best or int(r["file_num"] or 0) > int(best[k]["file_num"] or 0):
            best[k] = r
    agg = defaultdict(lambda: {"amount": 0.0, "n": 0, "last_dissem": ""})
    names = {}
    for r in best.values():
        k = (r["cand_id"], r["sup_opp"], r["ele_type"], r["spe_id"])
        agg[k]["amount"] += money(r["exp_amo"])
        agg[k]["n"] += 1
        names[r["spe_id"]] = r["spe_nam"]
    api = defaultdict(float)
    for r in json.loads((FEC / "api_se_by_candidate.json").read_text())["results"]:
        api[(r["candidate_id"], r["support_oppose_indicator"], r["committee_id"])] += r["total"]
        names.setdefault(r["committee_id"], r["committee_name"])
    rows = []
    for (cid, so, el, spe), v in agg.items():
        rows.append({
            "candidate": CANDS[cid]["name"], "cand_id": cid,
            "support_oppose": {"S": "support", "O": "oppose"}.get(so, so),
            "election": {"P": "primary", "G": "general"}.get(el, el),
            "spender": names[spe], "spender_id": spe, "amount": v["amount"], "expenditures": v["n"],
        })
    rows.sort(key=lambda r: -r["amount"])
    write_csv("outside_spending.csv", rows, list(rows[0].keys()))

    # per-spender cross-check (all elections) against API processed totals
    chk = defaultdict(float)
    for r in rows:
        chk[(r["cand_id"], r["support_oppose"][0].upper(), r["spender_id"])] += r["amount"]
    cross = [{"candidate": CANDS[c]["name"], "support_oppose": so, "spender": names[s],
              "bulk_24_48hr": chk.get((c, so, s), 0.0), "api_processed": api.get((c, so, s), 0.0)}
             for (c, so, s) in set(chk) | set(api) if c in CANDS]
    cross.sort(key=lambda r: -max(r["bulk_24_48hr"], r["api_processed"]))
    write_csv("outside_spending_crosscheck.csv", cross, list(cross[0].keys()))
    return rows


# ---------------------------------------------------------------- 3. PAC/party contributions


# ---------------------------------------------------------------- 4. raw e-filings (Schedule A)
# Most recent version of every 2026-cycle F3 report, per FEC /committee/{id}/filings (most_recent=True).
# Downloaded from https://docquery.fec.gov/dcdev/posted/{file_number}.fec  (format 8.5, FS = 0x1c).
EFILINGS = {
    "S6MI00418": ["2005714", "2005716", "2005717", "2005719", "2026985", "2027035", "2039704", "2039805"],
    "S4MI00595": ["1897146", "1902545", "1921332", "1942675", "1965896", "1995168", "2001576", "2024876", "2037587"],
}
SA = {"form": 0, "tran_id": 2, "back_ref": 3, "entity": 5, "org": 6, "last": 7, "first": 8, "city": 14,
      "state": 15, "zip": 16, "election": 17, "date": 19, "amount": 20, "employer": 23, "occupation": 24,
      "donor_cmte_id": 25, "donor_cmte_name": 26, "conduit": 36, "memo": 42, "memo_text": 43}


def efile_lines(cid):
    for n in EFILINGS[cid]:
        with (FEC / "efile" / f"{n}.fec").open(encoding="latin-1") as f:
            for line in f:
                parts = [x.strip().strip('"').strip() for x in line.rstrip("\r\n").split("\x1c")]
                if parts[0].startswith(("SA", "SB28")):
                    parts += [""] * (50 - len(parts))
                    rec = {k: parts[i] for k, i in SA.items()}
                    rec["file_num"] = n
                    rec["cand_id"] = cid
                    yield rec


def load_efile():
    """All Schedule A lines plus SB28A refunds, for both campaigns."""
    return [r for cid in CANDS for r in efile_lines(cid)]


SIZE_BUCKETS = [(0, "under $200"), (200, "$200-$499"), (500, "$500-$999"), (1000, "$1,000-$1,999"),
                (2000, "$2,000-$3,499"), (3500, "$3,500+ (max for primary + general is $7,000)")]


def size_bucket(total: float) -> str:
    label = SIZE_BUCKETS[0][1]
    for floor, name in SIZE_BUCKETS:
        if total >= floor:
            label = name
    return label


def norm_name(s: str) -> str:
    s = s.upper().replace(".", " ")
    s = re.sub(r"\b(MR|MRS|MS|DR|JR|SR|II|III|IV|MD|PHD|ESQ)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip(" ,")


def earmark_conduit(text: str) -> str:
    """'EARMARKED FROM NORPAC' -> NORPAC; NGP '* Earmarked Contribution: See Below' -> ACTBLUE (its memo line
    reads 'earmarked through ActBlue'); WinRed-style 'EARMARKED THROUGH WINRED' -> WINRED."""
    t = text.upper()
    m = re.search(r"EARMARKED (?:FROM|THROUGH|VIA) (?:THE )?([A-Z0-9][A-Z0-9 .&-]+)", t)
    if m:
        return m.group(1).split(";")[0].strip()
    if "EARMARKED CONTRIBUTION" in t:
        return "ACTBLUE"
    return ""


def individuals(sa):
    """Itemized individuals = SA11AI lines without memo X. Memo-X SA11AI lines are JFC attributions
    (money that arrives as an SA12 transfer), kept apart so nothing is counted twice. Refunds = SB28A."""
    direct, jfc = [], []
    for r in sa:
        if r["form"] != "SA11AI":
            continue
        rec = {"cand_id": r["cand_id"], "name": f"{r['last']}, {r['first']}".strip(", "), "city": r["city"],
               "state": r["state"], "zip5": r["zip"][:5], "employer": r["employer"], "occupation": r["occupation"],
               "date": r["date"], "amount": money(r["amount"]), "election": r["election"], "memo_text": r["memo_text"],
               "conduit": earmark_conduit(r["memo_text"])}
        (jfc if r["memo"] == "X" else direct).append(rec)
    return direct, jfc


def summarize_individuals(direct, jfc, sa, tot_rows):
    out = {}
    state_rows, size_rows, emp_rows, donor_rows, occ_rows = [], [], [], [], []
    for cid, c in CANDS.items():
        rs = [r for r in direct if r["cand_id"] == cid]
        total = sum(r["amount"] for r in rs)
        refunds = sum(money(r["amount"]) for r in sa if r["cand_id"] == cid and r["form"] == "SB28A")
        by_state = defaultdict(float)
        for r in rs:
            by_state[r["state"] or "(none)"] += r["amount"]
        for st, v in sorted(by_state.items(), key=lambda x: -x[1]):
            state_rows.append({"candidate": c["name"], "state": st, "amount": v, "share_of_itemized": v / total})
        donors = defaultdict(lambda: {"amount": 0.0, "n": 0})
        for r in rs:
            d = donors[(norm_name(r["name"]), r["zip5"])]
            d["amount"] += r["amount"]; d["n"] += 1
            d.update(name=r["name"], employer=r["employer"], occupation=r["occupation"], city=r["city"], state=r["state"])
        sizes = defaultdict(lambda: [0.0, 0])
        for d in donors.values():
            b = size_bucket(d["amount"]); sizes[b][0] += d["amount"]; sizes[b][1] += 1
        for _, b in SIZE_BUCKETS:
            if b in sizes:
                size_rows.append({"candidate": c["name"], "donor_cycle_total": b, "donors": sizes[b][1],
                                  "amount": sizes[b][0], "share_of_itemized": sizes[b][0] / total})
        for field, rows_out, label in (("employer", emp_rows, "employer_as_filed"), ("occupation", occ_rows, "occupation_as_filed")):
            agg = defaultdict(float)
            for r in rs:
                agg[re.sub(r"\s+", " ", (r[field] or "(blank)").upper()).strip()] += r["amount"]
            for e, v in sorted(agg.items(), key=lambda x: -x[1])[:50]:
                rows_out.append({"candidate": c["name"], label: e, "amount": v, "share_of_itemized": v / total})
        for d in sorted(donors.values(), key=lambda d: -d["amount"])[:100]:
            donor_rows.append({"candidate": c["name"], **{k: d[k] for k in ("name", "city", "state", "employer", "occupation", "n", "amount")}})
        t = next(x for x in tot_rows if x["cand_id"] == cid)
        j = [r for r in jfc if r["cand_id"] == cid]
        out[c["key"]] = {
            "itemized_lines": len(rs), "itemized_gross": total, "itemized_check_vs_fec": total - t["individual_itemized_api"],
            "refunds_sb28a": refunds, "unique_donors_name_zip": len(donors),
            "in_state_share": by_state.get("MI", 0) / total,
            "earmarked_share": sum(r["amount"] for r in rs if r["conduit"]) / total,
            "earmarked_by_conduit": dict(sorted(((k, sum(r["amount"] for r in rs if r["conduit"] == k)) for k in {r["conduit"] for r in rs if r["conduit"]}), key=lambda x: -x[1])[:5]),
            "memo_lines_not_counted": len(j), "memo_lines_top_text": Counter(r["memo_text"][:40] for r in j).most_common(2),
        }
    write_csv("individuals_by_state.csv", state_rows, list(state_rows[0].keys()))
    write_csv("individuals_by_donor_size.csv", size_rows, list(size_rows[0].keys()))
    write_csv("individuals_top_employers.csv", emp_rows, list(emp_rows[0].keys()))
    write_csv("individuals_top_occupations.csv", occ_rows, list(occ_rows[0].keys()))
    write_csv("individuals_top_donors.csv", donor_rows, list(donor_rows[0].keys()))
    return out


# ---------------------------------------------------------------- 5. committees: PACs, parties, JFC transfers
def committee_money(sa, cm):
    agg = defaultdict(float)
    for r in sa:
        if r["form"] in ("SA11B", "SA11C", "SA12") and r["memo"] != "X":
            name = (cm.get(r["donor_cmte_id"]) or {}).get("CMTE_NM") or r["org"] or r["donor_cmte_name"]
            agg[(r["cand_id"], r["form"], r["donor_cmte_id"], name)] += money(r["amount"])
    line = {"SA11B": "party committee", "SA11C": "PAC / other committee", "SA12": "transfer (JFC / authorized)"}
    rows = [{"candidate": CANDS[cid]["name"], "cand_id": cid, "line": line[f], "from": nm, "from_id": oid,
             "from_kind": committee_kind(cm.get(oid)), "connected_org": (cm.get(oid) or {}).get("CONNECTED_ORG_NM", ""),
             "amount": v} for (cid, f, oid, nm), v in agg.items()]
    rows.sort(key=lambda r: (r["candidate"], r["line"], -r["amount"]))
    write_csv("committee_money.csv", rows, list(rows[0].keys()))
    return rows


# ---------------------------------------------------------------- 6. Who Funded Genocide
def wfg(direct, pac_rows):
    def rd(n):
        return list(csv.DictReader((WFG / n).open(encoding="utf-8-sig")))
    E = {e["entity_id"]: e for e in rd("the-entire-network-entities.csv") if e["board"] == "us"}
    L = [l for l in rd("the-entire-network-links.csv") if l["board"] == "us"]
    wfg_ids = {"c-s6mi00418": "S6MI00418", "c-s4mi00595": "S4MI00595"}
    links = [{"candidate": CANDS[wfg_ids[l["to_entity_id"]]]["name"], "committee": l["from_name"],
              "measure": l["measure"], "amount": money(l["amount"]), "period": l["period"]}
             for l in L if l["to_entity_id"] in wfg_ids]
    # WFG-board committees that gave directly to either campaign (FEC pas2), by name
    wfg_cmte_names = {norm_name(re.sub(r"\(.*?\)", "", e["name"])) for e in E.values() if e["column"] == "The committees"}
    direct_from_wfg_cmtes = [r for r in pac_rows if norm_name(r["contributor"]).replace(" POLITICAL ACTION COMMITTEE", " PAC") in wfg_cmte_names
                             or any(n and n in norm_name(r["contributor"]) for n in ("NORPAC", "REPUBLICAN JEWISH COALITION", "DMFI", "AIPAC", "JOINT ACTION COMMITTEE", "PRO-ISRAEL AMERICA"))]
    # WFG named donors who also appear as itemized donors to either campaign
    # Match on normalized "LAST, FIRST" + state + city. A name match, not an identity proof.
    wfg_donors = {}
    for e in E.values():
        if e["column"] != "Who gives" or e["kind"] != "Named donor":
            continue
        m = re.match(r"(.+?), ([A-Z]{2}) ·", e["subtitle"])
        if m:
            wfg_donors[(norm_name(e["name"]), m.group(1).upper(), m.group(2))] = e
    overlap = defaultdict(lambda: {"amount": 0.0, "n": 0})
    for r in direct:
        k = (norm_name(r["name"]), r["city"].upper(), r["state"])
        if k in wfg_donors:
            o = overlap[(r["cand_id"], k)]
            o["amount"] += r["amount"]; o["n"] += 1
            o["wfg"] = wfg_donors[k]["what_the_record_says"]
    orow = [{"candidate": CANDS[cid]["name"], "donor": k[0], "city": k[1], "state": k[2],
             "to_campaign": v["amount"], "contributions": v["n"], "wfg_record": v["wfg"]}
            for (cid, k), v in sorted(overlap.items(), key=lambda x: -x[1]["amount"])]
    write_csv("wfg_links.csv", links, ["candidate", "committee", "measure", "amount", "period"])
    write_csv("wfg_donor_overlap.csv", orow, ["candidate", "donor", "city", "state", "to_campaign", "contributions", "wfg_record"])
    norpac = [r for r in direct if r["conduit"] == "NORPAC"]
    return {"links": links,
            "earmarked_through_norpac": {"candidate": "Mike Rogers" if norpac else None, "contributions": len(norpac),
                                         "amount": sum(r["amount"] for r in norpac)}, "direct_from_wfg_committees": [{k: r[k] for k in ("candidate", "contributor", "amount")} for r in direct_from_wfg_cmtes],
            "donor_overlap": {c["name"]: {"donors": sum(1 for r in orow if r["candidate"] == c["name"]),
                                          "amount": sum(r["to_campaign"] for r in orow if r["candidate"] == c["name"])}
                              for c in CANDS.values()}}


def main():
    cm, own = load_committees()
    tot = totals()
    ie = outside_spending()
    sa = load_efile()
    cmte = committee_money(sa, cm)
    direct, jfc = individuals(sa)
    indiv = summarize_individuals(direct, jfc, sa, tot)
    w = wfg(direct, [{"contributor": r["from"], **r} for r in cmte if r["line"] != "transfer (JFC / authorized)"])
    side = {}
    for cid, c in CANDS.items():
        side[c["key"]] = {
            "committees": own[cid],
            "totals": next(t for t in tot if t["cand_id"] == cid),
            "outside": {f"{so}_{el}": sum(r["amount"] for r in ie if r["cand_id"] == cid and r["support_oppose"] == so and r["election"] == el)
                        for so in ("support", "oppose") for el in ("primary", "general")},
            "committee_money_by_line": {ln: sum(r["amount"] for r in cmte if r["cand_id"] == cid and r["line"] == ln)
                                        for ln in ("party committee", "PAC / other committee", "transfer (JFC / authorized)")},
            "individuals": indiv[c["key"]],
            "top_transfers_in": [{k: r[k] for k in ("from", "amount")} for r in cmte if r["cand_id"] == cid and r["line"].startswith("transfer")][:6],
        }
    summary = {"race": "US Senate, Michigan, 2026", "candidates": side, "who_funded_genocide": w}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps(summary, indent=2, default=float)[:6000])


if __name__ == "__main__":
    main()
