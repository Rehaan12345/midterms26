import { useState } from "react";
import { AnimatePresence, LayoutGroup, motion } from "motion/react";
import { ChevronDown } from "lucide-react";
import { PARTY_NAME, fmt, fmtPct, type Party } from "./data";

export interface Row {
  id: string;
  name: string;
  party: Party;
  votes: number;
  pct: number;
}

const ease = [0.22, 1, 0.36, 1] as const;
const votesLabel = (n: number) => `${fmt.format(n)} vote${n === 1 ? "" : "s"}`;

/** Stable key so rows keep identity across elections and re-rank in place. */
const rowKey = (r: Row) => (r.party === "WRI" ? r.id : r.party);

export default function CandidateList({ rows, winnerId, official }: { rows: Row[]; winnerId: string | null; official: boolean }) {
  const [showAll, setShowAll] = useState(false);
  const main = rows.filter((r) => r.party !== "WRI" || r.pct >= 1);
  const minor = rows.filter((r) => !main.includes(r));
  const minorVotes = minor.reduce((s, r) => s + r.votes, 0);
  const minorTotal = minor.reduce((s, r) => s + r.pct, 0);
  const visible = showAll ? rows : main;

  return (
    <div className="cands">
      <LayoutGroup>
        <ol className="cands-list">
          <AnimatePresence initial={false}>
            {visible.map((r) => (
              <motion.li
                key={rowKey(r)}
                layout="position"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease }}
                className={`cand cand--${r.party}${r.id === winnerId ? " cand--won" : ""}`}
              >
                <div className="cand-who">
                  <span className="cand-name">{r.name}</span>
                  <span className="cand-party">
                    <i className={`swatch swatch--${r.party}`} aria-hidden="true" />
                    {PARTY_NAME[r.party]}
                    {r.id === winnerId && <span className="cand-won">{official ? "Won" : "Leading"}</span>}
                  </span>
                </div>
                <div className="cand-nums">
                  <span className="cand-pct">{fmtPct(r.pct)}</span>
                  <span className="cand-votes">{votesLabel(r.votes)}</span>
                </div>
                <div className="cand-bar" aria-hidden="true">
                  <motion.span
                    className="cand-bar-fill"
                    initial={false}
                    animate={{ scaleX: Math.max(r.pct, 0.4) / 100 }}
                    transition={{ duration: 0.6, ease }}
                  />
                </div>
              </motion.li>
            ))}
          </AnimatePresence>
        </ol>
      </LayoutGroup>
      {minor.length > 0 && (
        <button type="button" className="cands-more" aria-expanded={showAll} onClick={() => setShowAll((s) => !s)}>
          <ChevronDown size={16} aria-hidden="true" className={showAll ? "flip" : ""} />
          {showAll
            ? "Hide write-in candidates"
            : `${minor.length} write-in candidate${minor.length > 1 ? "s" : ""} · ${votesLabel(minorVotes)}${minorVotes ? ` (${fmtPct(minorTotal)})` : ""}`}
        </button>
      )}
    </div>
  );
}
