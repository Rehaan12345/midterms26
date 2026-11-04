import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AlertTriangle, ArrowLeft, X } from "lucide-react";
import MapView from "./MapView";
import Michigan from "./Michigan";
import CandidateList, { type Row } from "./CandidateList";
import {
  FABRIC, MARGIN_BANDS, OFFICES, PARTY_NAME, countyOutcome, fmt, lastName,
  loadCounties, loadRace, loadRaces, type Office, type RaceResults, type RaceSummary,
} from "./data";

type Geo = Awaited<ReturnType<typeof loadCounties>>;

type View = "tx" | "mi";
const VIEWS: { id: View; label: string }[] = [{ id: "tx", label: "Texas" }, { id: "mi", label: "Michigan" }];

function readURL() {
  const p = new URLSearchParams(location.search);
  return {
    view: (p.get("view") === "mi" ? "mi" : "tx") as View,
    year: Number(p.get("year")) || null, office: (p.get("race") as Office) || null, county: p.get("county"),
  };
}

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export default function App() {
  const [races, setRaces] = useState<RaceSummary[] | null>(null);
  const [geo, setGeo] = useState<Geo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const initial = useMemo(readURL, []);
  const [view, setView] = useState<View>(initial.view);
  const [year, setYear] = useState<number | null>(initial.year);
  const [office, setOffice] = useState<Office | null>(initial.office);
  const [county, setCounty] = useState<string | null>(initial.county);
  const [race, setRace] = useState<RaceResults | null>(null);
  const [is3d, setIs3d] = useState(true);
  const panelRef = useRef<HTMLElement>(null);
  const [panelInView, setPanelInView] = useState(false);

  // Phones: hide the peek once the panel itself is on screen, so it never repeats it.
  useEffect(() => {
    const el = panelRef.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setPanelInView(e.isIntersecting), { rootMargin: "0px 0px -120px 0px" });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    Promise.all([loadRaces(), loadCounties()])
      .then(([r, g]) => { setRaces(r); setGeo(g); })
      .catch(() => setError("We couldn’t load the election results. Check your connection, then reload the page."));
  }, []);

  const years = useMemo(() => [...new Set((races ?? []).map((r) => r.year))].sort((a, b) => a - b), [races]);
  // With a race selected, only its election years can be chosen; with none, every year can.
  const allowed = useMemo(
    () => (office ? years.filter((y) => races?.some((r) => r.year === y && r.office === office)) : years),
    [races, years, office],
  );

  // Resolve year/office to a race that exists. A selected office always exists in an allowed year;
  // with no office selected, show that year's race (President, then Senate, then Governor).
  const summary = useMemo(() => {
    if (!races || !allowed.length) return null;
    const y = year && allowed.includes(year) ? year : nearestYear(allowed, year ?? allowed[allowed.length - 1]);
    const inYear = races.filter((r) => r.year === y);
    return inYear.find((r) => r.office === office) ?? OFFICES.map((o) => inYear.find((r) => r.office === o.id)).find(Boolean)!;
  }, [races, allowed, year, office]);

  useEffect(() => {
    if (!summary) return;
    let live = true;
    loadRace(summary.id).then((r) => live && setRace(r)).catch(() => live && setError("We couldn’t load this race. Reload the page to try again."));
    return () => { live = false; };
  }, [summary]);

  useEffect(() => {
    if (view === "mi") { history.replaceState(null, "", "?view=mi"); return; }
    if (!summary) return;
    const p = new URLSearchParams({ year: String(summary.year) });
    if (office) p.set("race", office);
    if (county) p.set("county", county);
    history.replaceState(null, "", `?${p}`);
  }, [view, summary, county, office]);

  useEffect(() => {
    document.title = view === "mi" ? "Michigan Senate, the money" : "Texas, county by county";
  }, [view]);

  const countyName = useMemo(
    () => (geo && county ? geo.features.find((f) => f.properties.fips === county)?.properties.name ?? null : null),
    [geo, county],
  );

  const pickCounty = useCallback((fips: string | null) => setCounty(fips), []);

  if (error && view === "tx") return <div className="fatal" role="alert"><AlertTriangle size={18} aria-hidden="true" /> {error}</div>;

  const loading = !races || !geo || !summary;
  const raceReady = race && summary && race.id === summary.id;

  return (
    <div className={`app${view === "tx" && county && !panelInView ? " has-peek" : ""}`}>
      <header className="top">
        <div className="brand">
          {view === "tx" ? (
            <><h1>Texas, county by county</h1><p>How all 254 counties voted, 2008–2026</p></>
          ) : (
            <><h1>Michigan Senate, the money</h1><p>Where El-Sayed’s and Rogers’s campaign money came from, 2025–2026</p></>
          )}
        </div>
        <div className="top-right">
        {view === "tx" && <div className="offices" role="radiogroup" aria-label="Race">
          {OFFICES.map((o) => (
            // Click the selected race again to deselect it (all years become available).
            <button key={o.id} type="button" role="radio" aria-checked={office === o.id}
              className={office === o.id ? "is-on" : !office && summary?.office === o.id ? "is-shown" : ""}
              onClick={() => {
                const next = office === o.id ? null : o.id;
                setOffice(next);
                // Keep the stored year in step, so deselecting later doesn't jump back to an old year.
                const ys = next ? years.filter((y) => races?.some((r) => r.year === y && r.office === next)) : years;
                if (summary && !ys.includes(summary.year)) setYear(nearestYear(ys, summary.year));
              }}>
              {o.short}
            </button>
          ))}
        </div>}
        <div className="views" role="tablist" aria-label="State">
          {VIEWS.map((v) => (
            <button key={v.id} type="button" role="tab" aria-selected={view === v.id} aria-controls="view"
              onClick={() => setView(v.id)}>
              {v.label}
            </button>
          ))}
        </div>
        </div>
      </header>

      {view === "mi" ? <div id="view" role="tabpanel" className="view-mi"><Michigan /></div> : <>
      <main className="body" id="view" role="tabpanel">
        <section className="stage" aria-label="Map">
          {geo ? (
            <MapView geo={geo} race={raceReady ? race : null} official={summary?.status !== "unofficial"} selected={county} onSelect={pickCounty} is3d={is3d} onIs3d={setIs3d} />
          ) : (
            <div className="stage-loading" role="status">Loading the map…</div>
          )}
          <Legend is3d={is3d} showNone={!!summary && summary.countiesReported < 254} />
          {!loading && <YearSlider years={years} allowed={allowed} year={summary.year} onChange={setYear} />}
        </section>

        <aside className="panel" ref={panelRef} aria-label="Results">
          {loading ? (
            <p className="panel-loading" role="status">Loading results…</p>
          ) : (
            <Panel summary={summary} race={raceReady ? race : null} county={county} countyName={countyName}
              onClearCounty={() => setCounty(null)} />
          )}
          <footer className="source">
            2008–2024: certified results from the Texas Secretary of State; presidential results match MIT
            Election Lab county data exactly. 2026: unofficial results from Decision Desk HQ.
          </footer>
        </aside>
      </main>

      {county && raceReady && !panelInView && (
        <Peek
          race={race}
          fips={county}
          countyName={countyName}
          official={summary?.status !== "unofficial"}
          onOpen={() => panelRef.current?.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" })}
          onClose={() => setCounty(null)}
        />
      )}
      </>}
    </div>
  );
}

/** Nearest allowed year to `target`; ties go to the later year. */
function nearestYear(allowed: number[], target: number): number {
  return allowed.reduce((best, y) => {
    const d = Math.abs(y - target), bd = Math.abs(best - target);
    return d < bd || (d === bd && y > best) ? y : best;
  }, allowed[0]);
}

/** Timeline over every election year; it only stops on `allowed` years (the selected race's). */
function YearSlider({ years, allowed, year, onChange }: {
  years: number[]; allowed: number[]; year: number; onChange: (y: number) => void;
}) {
  const i = years.indexOf(year);
  // Pointer drag: go to the allowed year nearest the pointer. On a tie (pointer over a skipped year,
  // halfway between two allowed ones) stay put, so the thumb never flips back and forth; it jumps
  // across once the pointer reaches the next allowed year.
  const onDrag = (e: React.ChangeEvent<HTMLInputElement>) => {
    const to = Number(e.target.value);
    const dist = (y: number) => Math.abs(years.indexOf(y) - to);
    const best = Math.min(...allowed.map(dist));
    const next = dist(year) === best ? year : allowed.find((y) => dist(y) === best)!;
    if (next === year) e.target.value = String(i); // snap the native thumb back off the skipped year
    else onChange(next);
  };
  // Keyboard: arrows/Home/End move to the next allowed year in that direction, skipping the rest.
  const onKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const later = allowed.filter((y) => y > year), earlier = allowed.filter((y) => y < year);
    const target = {
      ArrowRight: later[0], ArrowUp: later[0], PageUp: later[0],
      ArrowLeft: earlier[earlier.length - 1], ArrowDown: earlier[earlier.length - 1], PageDown: earlier[earlier.length - 1],
      Home: allowed[0], End: allowed[allowed.length - 1],
    }[e.key];
    if (!(e.key in { ArrowRight: 1, ArrowUp: 1, PageUp: 1, ArrowLeft: 1, ArrowDown: 1, PageDown: 1, Home: 1, End: 1 })) return;
    e.preventDefault();
    if (target !== undefined && target !== year) onChange(target);
  };
  return (
    <div className="timeline">
      <input
        type="range"
        min={0}
        max={years.length - 1}
        step={1}
        value={i}
        aria-label="Election year"
        aria-valuetext={String(year)}
        style={{ ["--p" as string]: `${(i / (years.length - 1)) * 100}%` }}
        onChange={onDrag}
        onKeyDown={onKey}
      />
      <div className="timeline-ticks" aria-hidden="true">
        {years.map((y) => {
          const ok = allowed.includes(y);
          return (
            <span key={y} className={y === year ? "is-on" : ok ? "" : "is-off"} onClick={ok ? () => onChange(y) : undefined}>{y}</span>
          );
        })}
      </div>
    </div>
  );
}

function Panel({ summary, race, county, countyName, onClearCounty }: {
  summary: RaceSummary; race: RaceResults | null; county: string | null; countyName: string | null; onClearCounty: () => void;
}) {
  const official = summary.status !== "unofficial";
  const won = official ? "won" : "leads";
  let rows: Row[] = summary.statewide;
  let headline: string;
  let winnerId: string | null = summary.statewide[0]?.id ?? null;
  let total = summary.total;

  if (county && race) {
    const c = race.counties[county];
    const o = countyOutcome(race, county);
    total = c?.total ?? 0;
    winnerId = o.winnerId;
    rows = (c?.results ?? []).map(([id, votes]) => ({
      id, votes, ...race.candidates[id], pct: total ? (100 * votes) / total : 0,
    }));
    headline = o.winnerId
      ? `${race.candidates[o.winnerId].name.split(" / ")[0]} ${won} ${countyName} County by ${o.marginPts.toFixed(1)} points.`
      : official ? `${countyName} County reported no votes.` : `${countyName} County hasn’t reported votes yet.`;
  } else {
    const [a, b] = summary.statewide;
    headline = `${a.name.split(" / ")[0]} ${won} Texas by ${(a.pct - (b?.pct ?? 0)).toFixed(1)} points.`;
  }

  const rep = summary.countiesWon.REP ?? 0;
  const dem = summary.countiesWon.DEM ?? 0;

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={`${summary.id}:${county ?? "tx"}`}
        className="panel-body"
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -4 }}
        transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="race-head">
          {county && (
            <button type="button" className="crumb" onClick={onClearCounty}>
              <ArrowLeft size={15} aria-hidden="true" /> All of Texas
            </button>
          )}
          <h2>{county ? `${countyName} County` : "Texas"}</h2>
          <p className="race-sub">{summary.officeLabel} · {summary.year}</p>
        </div>

        {!official && (
          <p className="status-note">
            Unofficial · {summary.sourceLabel} · {summary.countiesReported} of 254 counties reported. Not yet certified.
          </p>
        )}

        <p className="headline" aria-live="polite">{headline}</p>

        {total > 0 && <CandidateList rows={rows} winnerId={winnerId} official={official} />}
        {total > 0 && <p className="total">{fmt.format(total)} votes{county ? "" : " statewide"}</p>}

        {!county && (
          <section className="won" aria-label="Counties won">
            <div className="won-bar" aria-hidden="true">
              <span style={{ flexGrow: rep, background: FABRIC.REP[2] }} />
              <span style={{ flexGrow: dem, background: FABRIC.DEM[2] }} />
            </div>
            <p className="won-key">
              <span><b>{rep}</b> counties for {winnerName(summary, "REP")}</span>
              {summary.countiesReported < 254 && <span><b>{254 - summary.countiesReported}</b> not reported</span>}
              <span><b>{dem}</b> for {winnerName(summary, "DEM")}</span>
            </p>
          </section>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

/** Phones: the selected county's answer, pinned at the bottom so a tap always shows something. */
function Peek({ race, fips, countyName, official, onOpen, onClose }: {
  race: RaceResults; fips: string; countyName: string | null; official: boolean; onOpen: () => void; onClose: () => void;
}) {
  const o = countyOutcome(race, fips);
  const w = o.winnerId ? race.candidates[o.winnerId] : null;
  return (
    <motion.div
      className="peek"
      role="region"
      aria-label={`${countyName} County result`}
      initial={{ y: "110%" }}
      animate={{ y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
    >
      <button type="button" className="peek-main" onClick={onOpen}>
        <strong>{countyName} County</strong>
        <span>
          {w && <i className={`swatch swatch--${w.party}`} aria-hidden="true" />}
          {w ? `${lastName(w.name)} (${PARTY_NAME[w.party]}) ${official ? "won" : "leads"} by ${o.marginPts.toFixed(1)} pts` : "No votes reported"}
        </span>
        <em>See full results</em>
      </button>
      <button type="button" className="icon-btn" aria-label="Close county" onClick={onClose}>
        <X size={18} aria-hidden="true" />
      </button>
    </motion.div>
  );
}

function winnerName(s: RaceSummary, party: "REP" | "DEM") {
  const c = s.statewide.find((r) => r.party === party);
  return c ? lastName(c.name) : PARTY_NAME[party];
}

function Legend({ is3d, showNone }: { is3d: boolean; showNone: boolean }) {
  return (
    <figure className="legend" aria-label={`Map key: color shows the winner's party, shade shows the margin${is3d ? ", block height shows the winner's vote share" : ""}`}>
      <div className="legend-grid">
        <span>Rep.</span>
        {FABRIC.REP.map((c, i) => <i key={c} style={{ background: c }} title={`Republican, ${MARGIN_BANDS[i].label}`} />)}
        <span>Dem.</span>
        {FABRIC.DEM.map((c, i) => <i key={c} style={{ background: c }} title={`Democrat, ${MARGIN_BANDS[i].label}`} />)}
        <span />
        {MARGIN_BANDS.map((b) => <small key={b.label}>{b.label.replace(" pts", "")}</small>)}
      </div>
      <figcaption>Shade: margin of victory, points{is3d && <><br />Height: winner’s share of the vote</>}</figcaption>
      {showNone && <p className="legend-none"><i style={{ background: FABRIC.UNREPORTED }} aria-hidden="true" /> No votes reported</p>}
    </figure>
  );
}
