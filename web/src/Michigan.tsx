import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "motion/react";
import { AlertTriangle, ChevronDown } from "lucide-react";
import { geoPath } from "d3-geo";
import { feature, mesh } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";
import "./michigan.css";

type Party = "DEM" | "REP";
interface Source { id: string; label: string; amount: number; note: string }
interface Group { name: string; primary: number; general: number; amount: number }
interface Side { primary: number; general: number; groups: Group[]; groupCount: number }
interface Cand {
  key: string; name: string; short: string; party: Party; committee: string; candId: string;
  coverageEnd: string; total: number; cashOnHand: number; sources: Source[];
  individualsTotal: number; itemized: number; donors: number; otherReceipts: number;
  states: Record<string, { st: string; amount: number }>; elsewhere: number;
  outside: { support: Side; oppose: Side };
  proIsrael: { kind: "given" | "help" | "against"; name: string; how: string; amount: number }[];
}
interface Finance { race: string; outsideThrough: string; candidates: Cand[]; notes: { dsccAgainstRogers: number } }
type StateProps = { name: string };
type Atlas = Topology<{ states: GeometryCollection<StateProps>; nation: GeometryCollection }>;

const PARTY_NAME: Record<Party, string> = { DEM: "Democrat", REP: "Republican" };
/** Five pastel steps per party, lightest to darkest; steps 3–5 are the Texas fabric. */
const STEPS: Record<Party, string[]> = {
  DEM: ["#e3ecfa", "#c2d4f4", "#97b8ee", "#3f75d4", "#1a4aa3"],
  REP: ["#fae3e5", "#f5c4c8", "#f2a0a6", "#dc4a55", "#b01e2c"],
};
const BREAKS = [0.005, 0.01, 0.03, 0.1]; // share of itemized dollars
const BAND_LABELS = ["under 0.5%", "0.5–1%", "1–3%", "3–10%", "10% or more"];
const NONE = "#e8e6ee";

const usd = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
/** 30%, 6.8%, 0.4%: whole points from 10% up, one decimal below. */
const pct = (x: number) => `${(x * 100).toFixed(x >= 0.1 ? 0 : 1)}%`;
function short(n: number): string {
  if (n === 0) return "$0";
  if (n >= 1e6) return `$${(n / 1e6).toFixed(n >= 1e8 ? 0 : 1)}M`;
  if (n >= 1e3) return `$${Math.round(n / 1e3)}k`;
  return usd.format(n);
}
function date(mdy: string) {
  const [m, d, y] = mdy.split("/").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}
const band = (share: number) => BREAKS.filter((b) => share >= b).length;

export default function Michigan() {
  const [data, setData] = useState<Finance | null>(null);
  const [atlas, setAtlas] = useState<Atlas | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("data/mi-finance.json").then((r) => (r.ok ? r.json() : Promise.reject())),
      fetch("data/us-states-albers.json").then((r) => (r.ok ? r.json() : Promise.reject())),
    ])
      .then(([d, a]) => { setData(d); setAtlas(a); })
      .catch(() => setError("We couldn’t load the campaign finance data. Check your connection, then reload the page."));
  }, []);

  if (error) return <div className="fatal" role="alert"><AlertTriangle size={18} aria-hidden="true" /> {error}</div>;
  if (!data || !atlas) return <main className="mi"><p className="mi-loading" role="status">Loading the campaign money…</p></main>;

  const [a, b] = data.candidates;
  // One scale per section, shared by both candidates, so bar lengths compare across columns.
  const sourceMax = Math.max(...data.candidates.flatMap((c) => c.sources.map((s) => s.amount)));
  const outsideMax = Math.max(...data.candidates.flatMap((c) => [sideTotal(c.outside.support), sideTotal(c.outside.oppose)]));

  return (
    <main className="mi">
      <section className="mi-sheet" aria-labelledby="mi-raised">
        <h2 id="mi-raised" className="visually-hidden">What each campaign raised</h2>
        <div className="mi-pair">
          {data.candidates.map((c) => <Raised key={c.key} c={c} max={sourceMax} />)}
        </div>
      </section>

      <section className="mi-sheet" aria-labelledby="mi-where">
        <header className="mi-sec-head">
          <h2 id="mi-where">Where the donors live</h2>
          <p>
            Each state is shaded by its share of the candidate’s itemized donations: gifts from people who gave
            more than $200, the only donors campaigns report by name and address. Smaller gifts aren’t on the map.
          </p>
        </header>
        <div className="mi-pair">
          {data.candidates.map((c) => <Where key={c.key} c={c} atlas={atlas} />)}
        </div>
        <MapKey />
      </section>

      <section className="mi-sheet" aria-labelledby="mi-outside">
        <header className="mi-sec-head">
          <h2 id="mi-outside">Outside spending</h2>
          <p>
            Not campaign money. Super PACs and other groups spent this on their own ads, mail and canvassing, for or
            against each candidate. By law they can’t coordinate with the campaigns, so none of it is in the totals above.
          </p>
        </header>
        <div className="mi-pair">
          {data.candidates.map((c) => (
            <Outside key={c.key} c={c} max={outsideMax} dscc={c.key === "rogers" ? data.notes.dsccAgainstRogers : 0} />
          ))}
        </div>
      </section>

      <section className="mi-sheet" aria-labelledby="mi-israel">
        <header className="mi-sec-head">
          <h2 id="mi-israel">Pro-Israel committees, including AIPAC</h2>
          <p>
            Money from the pro-Israel committees tracked by Who Funded Genocide, including AIPAC’s super PAC, United
            Democracy Project. “Given to the campaign” is money the campaign received. The rest is outside spending.
          </p>
        </header>
        <div className="mi-pair">
          {data.candidates.map((c) => <ProIsrael key={c.key} c={c} />)}
        </div>
      </section>

      <footer className="mi-source">
        Campaign money: each campaign’s own reports to the Federal Election Commission (latest amended versions),
        through {date(a.coverageEnd)} for {a.short} and {date(b.coverageEnd)} for {b.short}. Reports covering the last
        weeks of the race are due December 3. Outside spending: FEC 24- and 48-hour independent expenditure reports
        filed through {new Date(data.outsideThrough + "T12:00").toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })},
        with amendments applied. Groups sometimes report the same ad as support for one candidate in one filing and
        opposition to the other in another, so compare the totals rather than single lines. Pro-Israel committee list:
        “The Entire Network,” Who Funded Genocide (whofundedgenocide.com/map), CC BY 4.0, research with Wallface. State shapes: U.S. Census Bureau, via us-atlas.
      </footer>
    </main>
  );
}

function sideTotal(s: Side) { return s.primary + s.general; }

/* ---------------------------------------------------------------- raised */

function Raised({ c, max }: { c: Cand; max: number }) {
  const indivShare = c.individualsTotal / c.total;
  const pac = c.sources.find((s) => s.id === "pac")!;
  return (
    <article className={`mi-col mi-col--${c.party}`} aria-labelledby={`${c.key}-name`}>
      <div className="race-head">
        <h3 id={`${c.key}-name`} className="mi-name">{c.name}</h3>
        <p className="race-sub">
          <i className={`swatch swatch--${c.party}`} aria-hidden="true" /> {PARTY_NAME[c.party]} · reports through {date(c.coverageEnd)}
        </p>
      </div>
      <p className="headline">
        Raised {short(c.total)}. {pct(indivShare)} came from individual donors and {pct(pac.amount / c.total)} from PACs.
      </p>
      <p className="mi-total" title={usd.format(c.total)}>
        <span className="mi-figure">{usd.format(c.total)}</span>
        <span>raised · {usd.format(c.cashOnHand)} cash on hand</span>
      </p>
      <ul className="mi-rows" aria-label={`Where ${c.short}’s money came from`}>
        {c.sources.map((s, i) => (
          <li key={s.id} className={`mi-row${s.amount === 0 ? " is-zero" : ""}`}>
            <div>
              <span className="mi-row-label">{s.label}</span>
              {s.note && <span className="mi-row-note">{s.note}</span>}
            </div>
            <div className="mi-row-nums">
              <span className="mi-row-fig">{short(s.amount)}</span>
              <span className="mi-row-pct">{s.amount ? `${pct(s.amount / c.total)} · ${usd.format(s.amount)}` : "none reported"}</span>
            </div>
            <Bar value={s.amount} max={max} party={c.party} delay={i * 0.04} />
          </li>
        ))}
      </ul>
    </article>
  );
}

function Bar({ value, max, party, delay = 0, tone = "solid" }: { value: number; max: number; party: Party; delay?: number; tone?: "solid" | "soft" }) {
  return (
    <span className="mi-bar" aria-hidden="true">
      <motion.span
        className="mi-bar-fill"
        style={{ width: `${Math.max(0, (value / max) * 100)}%`, background: tone === "solid" ? STEPS[party][4] : STEPS[party][2] }}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      />
    </span>
  );
}

/* ---------------------------------------------------------------- map */

function Where({ c, atlas }: { c: Cand; atlas: Atlas }) {
  const [open, setOpen] = useState(false);
  const [tip, setTip] = useState<{ x: number; y: number; id: string } | null>(null);
  const wrap = useRef<HTMLDivElement>(null);
  const path = useMemo(() => geoPath(), []);
  const states = useMemo(() => feature(atlas, atlas.objects.states).features, [atlas]);
  const borders = useMemo(() => path(mesh(atlas, atlas.objects.states, (x, y) => x !== y)) ?? "", [atlas, path]);
  const itemized = c.itemized;
  const ranked = useMemo(
    () => Object.entries(c.states).map(([id, v]) => ({ id, ...v, share: v.amount / itemized, name: states.find((s) => s.id === id)?.properties.name ?? v.st }))
      .sort((x, y) => y.amount - x.amount),
    [c.states, itemized, states],
  );
  const mi = c.states["26"];
  const outOfState = 1 - (mi?.amount ?? 0) / itemized;
  const top = ranked.filter((r) => r.id !== "26")[0];
  const small = c.sources.find((s) => s.id === "small")!;
  const move = (e: React.PointerEvent, id: string) => {
    const r = wrap.current!.getBoundingClientRect();
    setTip({ x: e.clientX - r.left, y: e.clientY - r.top, id });
  };
  const tipRow = tip ? ranked.find((r) => r.id === tip.id) : null;

  return (
    <article className="mi-col" aria-label={`${c.short}: donors by state`}>
      <p className="mi-lede">
        <b>{c.short}</b>: {pct(1 - outOfState)} of itemized money came from Michigan; {pct(outOfState)} from out of
        state, led by {top.name} ({pct(top.share)}).
      </p>
      <div className="mi-map" ref={wrap} onPointerLeave={() => setTip(null)}>
        <svg viewBox="0 0 975 610" role="img"
          aria-label={`Map of ${c.short}’s itemized donations by state. Largest: ${ranked.slice(0, 3).map((r) => `${r.name} ${pct(r.share)}`).join(", ")}. The full list is below the map.`}>
          <g>
            {states.map((s) => {
              const v = c.states[s.id as string];
              const fill = v ? STEPS[c.party][band(v.amount / itemized)] : NONE;
              return (
                <path key={s.id} d={path(s) ?? ""} fill={fill}
                  className={tip?.id === s.id ? "is-hover" : undefined}
                  onPointerMove={(e) => move(e, s.id as string)} />
              );
            })}
          </g>
          <path d={borders} className="mi-seams" />
          {states.filter((s) => s.id === "26").map((s) => <path key="mi" d={path(s) ?? ""} className="mi-home" />)}
          {tip && <path d={path(states.find((s) => s.id === tip.id)!) ?? ""} className="mi-hover" />}
        </svg>
        {tip && tipRow && (
          <div className="map-tip mi-tip" style={{ transform: `translate(${Math.min(tip.x + 14, (wrap.current?.clientWidth ?? 300) - 200)}px, ${tip.y + 14}px)` }}>
            <strong>{tipRow.name}</strong>
            <span>{usd.format(tipRow.amount)}</span>
            <em>{pct(tipRow.share)} of {c.short}’s itemized money</em>
          </div>
        )}
      </div>

      <ol className="mi-states" aria-label={`${c.short}: itemized donations by state, largest first`}>
        {(open ? ranked : ranked.slice(0, 5)).map((r) => (
          <li key={r.id}>
            <span className="mi-state-name">{r.name}</span>
            <span className="mi-state-bar" aria-hidden="true">
              <span style={{ width: `${(r.share / ranked[0].share) * 100}%`, background: STEPS[c.party][band(r.share)] }} />
            </span>
            <span className="mi-state-pct">{pct(r.share)}</span>
            <span className="mi-state-usd">{short(r.amount)}</span>
          </li>
        ))}
      </ol>
      <button type="button" className="cands-more" aria-expanded={open} onClick={() => setOpen(!open)}>
        {open ? "Show the top five" : `Show all ${ranked.length} (50 states and D.C.)`}
        <ChevronDown size={15} className={open ? "flip" : ""} aria-hidden="true" />
      </button>
      <p className="mi-note">
        Mapped: {usd.format(itemized)} in itemized gifts from {c.donors.toLocaleString("en-US")} donors.
        Not mapped: {usd.format(small.amount)} in gifts of $200 or less
        {c.elsewhere > 0 ? `, and ${usd.format(c.elsewhere)} from overseas military and territory addresses` : ""}.
      </p>
    </article>
  );
}

function MapKey() {
  return (
    <figure className="mi-key" aria-label="Map key: darker means a larger share of the candidate's itemized money">
      <div className="mi-key-grid">
        <span>Dem.</span>{STEPS.DEM.map((c) => <i key={c} style={{ background: c }} />)}
        <span>Rep.</span>{STEPS.REP.map((c) => <i key={c} style={{ background: c }} />)}
        <span />{BAND_LABELS.map((l) => <small key={l}>{l}</small>)}
      </div>
      <figcaption>Share of that candidate’s itemized money. Michigan is outlined.</figcaption>
    </figure>
  );
}

/* ---------------------------------------------------------------- outside */

function Outside({ c, max, dscc }: { c: Cand; max: number; dscc: number }) {
  const rows: { id: "support" | "oppose"; label: string; tone: "solid" | "soft" }[] = [
    { id: "support", label: `Spent to help ${c.short}`, tone: "solid" },
    { id: "oppose", label: `Spent against ${c.short}`, tone: "soft" },
  ];
  return (
    <article className={`mi-col mi-col--${c.party}`} aria-label={`Outside spending for and against ${c.short}`}>
      <h3 className="mi-col-title">{c.name}</h3>
      {rows.map((r, i) => {
        const s = c.outside[r.id];
        const total = sideTotal(s);
        return (
          <div key={r.id} className="mi-out">
            <div className="mi-row">
              <div>
                <span className="mi-row-label">{r.label}</span>
                <span className="mi-row-note">
                  Primary {short(s.primary)} · general {short(s.general)} · {s.groupCount} groups
                </span>
              </div>
              <div className="mi-row-nums">
                <span className="mi-row-fig">{short(total)}</span>
                <span className="mi-row-pct">{usd.format(total)}</span>
              </div>
              <Bar value={total} max={max} party={c.party} tone={r.tone} delay={i * 0.06} />
            </div>
            <ol className="mi-groups" aria-label={`Largest groups that ${r.id === "support" ? "helped" : "opposed"} ${c.short}`}>
              {s.groups.slice(0, 4).map((g) => (
                <li key={g.name}>
                  <span>{g.name}</span>
                  <span className="mi-groups-usd">
                    {short(g.amount)}
                    {g.primary > 0 && g.general > 0 ? "" : <em>{g.primary > 0 ? " primary" : ""}</em>}
                  </span>
                </li>
              ))}
            </ol>
          </div>
        );
      })}
      {dscc > 0 && (
        <p className="mi-note">
          Not included: {usd.format(dscc)} the Democratic Senatorial Campaign Committee reported spending against
          Rogers. Party committees’ spending appears in the FEC’s processed data but not in the 24- and 48-hour reports used here.
        </p>
      )}
      {c.key === "el_sayed" && (
        <p className="mi-note">
          In the August primary, United Democracy Project, AIPAC’s super PAC, spent {short(c.outside.oppose.groups.find((g) => g.name.startsWith("United Democracy"))?.primary ?? 0)} against El-Sayed.
        </p>
      )}
    </article>
  );
}

/* ---------------------------------------------------------------- pro-Israel committees */

const PRO_KINDS = [
  { id: "given", label: (n: string) => `Given to ${n}’s campaign` },
  { id: "help", label: (n: string) => `Spent to help ${n}` },
  { id: "against", label: (n: string) => `Spent against ${n}` },
] as const;

function ProIsrael({ c }: { c: Cand }) {
  return (
    <article className="mi-col" aria-label={`Pro-Israel committee money and ${c.short}`}>
      <h3 className="mi-col-title">{c.name}</h3>
      {PRO_KINDS.map((k) => {
        const items = c.proIsrael.filter((x) => x.kind === k.id);
        const total = items.reduce((a, x) => a + x.amount, 0);
        return (
          <div key={k.id} className="mi-out">
            <div className="mi-row">
              <span className="mi-row-label">{k.label(c.short)}</span>
              <div className="mi-row-nums">
                <span className={`mi-row-fig${total ? "" : " is-none"}`}>{short(total)}</span>
                <span className="mi-row-pct">{total ? usd.format(total) : "none reported"}</span>
              </div>
            </div>
            {items.length > 0 && (
              <ol className="mi-groups">
                {items.map((x) => (
                  <li key={x.name + x.how}>
                    <span>{x.name} <em className="mi-how">· {x.how}</em></span>
                    <span className="mi-groups-usd">{usd.format(x.amount)}</span>
                  </li>
                ))}
              </ol>
            )}
          </div>
        );
      })}
    </article>
  );
}
