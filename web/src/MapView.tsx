import { useEffect, useRef, useState } from "react";
import { Map as MLMap, NavigationControl, setWorkerUrl, type ExpressionSpecification } from "maplibre-gl";
// MapLibre resolves its worker next to its own module, which no longer exists after bundling.
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";

setWorkerUrl(workerUrl);
import { FABRIC, PARTY_NAME, countyOutcome, fabricFor, lastName, type RaceResults } from "./data";

type Counties = GeoJSON.FeatureCollection<GeoJSON.Polygon | GeoJSON.MultiPolygon, { fips: string; name: string }>;

interface Props {
  geo: Counties;
  race: RaceResults | null;
  official: boolean;
  selected: string | null;
  onSelect: (fips: string | null) => void;
  is3d: boolean;
  onIs3d: (v: boolean) => void;
}

const TEXAS: [[number, number], [number, number]] = [[-106.65, 25.84], [-93.51, 36.5]];
const TEXAS_CENTER: [number, number] = [-99.3, 31.2];
const WAVE_MS = 700;
/** Keep Texas clear of the legend (top-left) and the timeline card (bottom). */
const fitPadding = (el: HTMLElement) =>
  el.clientWidth < 600 ? { top: 140, bottom: 112, left: 12, right: 12 } : { top: 32, bottom: 128, left: 32, right: 32 };
// 3D: each county is a block whose height is the winner's vote share (linear from 0).
const PITCH = 50;
const BEARING = -12;
const METERS_PER_PCT = 2400; // 100% would be a 240 km block (Texas is ~1,200 km wide); linear from 0
const SELECTED = "#6a55cc";
const TILT_ZOOM = 0.45; // the flat fit leaves Texas small once tilted (the far edge recedes)
const HEIGHT: ExpressionSpecification = ["coalesce", ["feature-state", "h"], 0];
const homeCamera = (m: MLMap, el: HTMLElement, threeD: boolean) => {
  const bearing = threeD ? BEARING : 0;
  const cam = m.cameraForBounds(TEXAS, { padding: fitPadding(el), bearing });
  return { ...cam, zoom: (cam?.zoom ?? 5) + (threeD ? TILT_ZOOM : 0), pitch: threeD ? PITCH : 0, bearing };
};

/** Winner's share of the county's votes, in percent (0 when nothing was reported). */
function winnerShare(race: RaceResults, fips: string): number {
  const c = race.counties[fips];
  return c && c.total ? (100 * c.results[0][1]) / c.total : 0;
}
const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const canHover = () => window.matchMedia("(hover: hover) and (pointer: fine)").matches;

function bbox(geom: GeoJSON.Polygon | GeoJSON.MultiPolygon): [number, number, number, number] {
  let [x0, y0, x1, y1] = [Infinity, Infinity, -Infinity, -Infinity];
  const rings = geom.type === "Polygon" ? geom.coordinates : geom.coordinates.flat();
  for (const ring of rings) for (const [x, y] of ring) {
    if (x < x0) x0 = x; if (y < y0) y0 = y; if (x > x1) x1 = x; if (y > y1) y1 = y;
  }
  return [x0, y0, x1, y1];
}

export default function MapView({ geo, race, official, selected, onSelect, is3d, onIs3d }: Props) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MLMap | null>(null);
  const [ready, setReady] = useState(false);
  const raceRef = useRef(race);
  raceRef.current = race;
  const [tip, setTip] = useState<{ x: number; y: number; fips: string } | null>(null);
  const [moved, setMoved] = useState(false);
  const [tilt, setTilt] = useState(PITCH);
  const [turn, setTurn] = useState(BEARING);
  const home = useRef({ zoom: 0, pitch: PITCH, bearing: BEARING });

  const names = useRef(new Map(geo.features.map((f) => [f.properties.fips, f.properties.name])));
  const boxes = useRef(new Map(geo.features.map((f) => [f.properties.fips, bbox(f.geometry)])));
  // West-to-east order for the recolor wave, by longitude of each county's center.
  const order = useRef(
    [...boxes.current.entries()].sort((a, b) => (a[1][0] + a[1][2]) - (b[1][0] + b[1][2]) || b[1][3] - a[1][3]).map(([f]) => f),
  );

  useEffect(() => {
    const m = new MLMap({
      container: el.current!,
      style: {
        version: 8, sources: {},
        light: { anchor: "map", position: [1.4, 200, 30], intensity: 0.18 }, // soft: river-bend walls would stripe under stronger light
        layers: [{ id: "bg", type: "background", paint: { "background-color": "rgba(0,0,0,0)" } }],
      },
      bounds: TEXAS,
      fitBoundsOptions: { padding: fitPadding(el.current!) },
      attributionControl: false,
      cooperativeGestures: !canHover(), // mouse/trackpad: plain scroll zooms; touch: two fingers, so the page still scrolls
      renderWorldCopies: false,
    });
    m.keyboard.disable(); // arrow keys step through counties instead of panning (see onKeyDown)
    m.addControl(new NavigationControl({ showCompass: true, visualizePitch: true }), "top-right");
    m.on("load", () => {
      m.addSource("counties", { type: "geojson", data: geo, promoteId: "fips" });
      // Absolute URL: the worker would resolve a relative one against its own /assets/ path.
      m.addSource("outline", { type: "geojson", data: new URL(`${import.meta.env.BASE_URL}data/tx-outline.geojson`, location.href).href });
      m.addLayer({ id: "outline", type: "line", source: "outline",
        layout: { "line-join": "round" },
        paint: { "line-color": "#c9c2dc", "line-width": ["interpolate", ["linear"], ["zoom"], 4, 1, 8, 2] } });
      m.addLayer({ id: "blocks", type: "fill-extrusion", source: "counties",
        paint: {
          "fill-extrusion-color": ["case", ["boolean", ["feature-state", "selected"], false], SELECTED,
            ["coalesce", ["feature-state", "fill"], FABRIC.UNREPORTED]],
          "fill-extrusion-height": HEIGHT,
          "fill-extrusion-vertical-gradient": true,
        } });
      // County borders: 2D only (in 3D, ground-level lines would sit buried under the blocks).
      m.addLayer({ id: "borders", type: "line", source: "counties", layout: { visibility: "none" },
        paint: { "line-color": "#000000", "line-width": ["interpolate", ["linear"], ["zoom"], 4, 0.4, 8, 1.2] } });
      const cam = homeCamera(m, el.current!, true);
      home.current = { zoom: cam.zoom, pitch: cam.pitch, bearing: cam.bearing }; // set before jumpTo: it fires moveend synchronously
      m.jumpTo(cam);
      setReady(true);
    });
    m.on("pitch", () => setTilt(Math.round(m.getPitch())));
    m.on("rotate", () => setTurn(Math.round(m.getBearing())));
    m.on("moveend", () => {
      const h = home.current;
      // tilt and rotation are the user's settings (sliders), so they don't count as "moved"
      setMoved(m.getZoom() > h.zoom + 0.15 || !m.getBounds().contains(TEXAS_CENTER));
    });

    m.on("mousemove", "blocks", (e) => {
      const fips = e.features?.[0]?.properties?.fips as string | undefined;
      if (!fips) return;
      if (!canHover()) return; // taps synthesize mousemove; phones get the bottom bar instead
      m.getCanvas().style.cursor = "pointer";
      setTip({ x: e.point.x, y: e.point.y, fips });
    });
    m.on("mouseleave", "blocks", () => {
      m.getCanvas().style.cursor = "";
      setTip(null);
    });
    m.on("click", (e) => {
      const hit = m.queryRenderedFeatures(e.point, { layers: ["blocks"] })[0];
      onSelectRef.current((hit?.properties?.fips as string) ?? null);
    });
    map.current = m;
    return () => { m.remove(); map.current = null; };
  }, [geo]);

  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  // Signature move: blocks recolor and rise in a soft west-to-east wave when the election changes.
  useEffect(() => {
    const m = map.current;
    if (!ready || !m || !race) return;
    const fills = new Map(order.current.map((f) => {
      const o = countyOutcome(race, f);
      return [f, { fill: fabricFor(o), h: winnerShare(race, f) * METERS_PER_PCT }];
    }));
    if (reducedMotion()) {
      for (const [f, s] of fills) m.setFeatureState({ source: "counties", id: f }, s);
      return;
    }
    let raf = 0;
    let done = 0;
    const start = performance.now();
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / WAVE_MS);
      const eased = 1 - Math.pow(1 - t, 3);
      const upto = Math.round(eased * order.current.length);
      for (; done < upto; done++) {
        const f = order.current[done];
        m.setFeatureState({ source: "counties", id: f }, fills.get(f)!);
      }
      if (t < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => {
      cancelAnimationFrame(raf);
      for (; done < order.current.length; done++) {
        const f = order.current[done];
        m.setFeatureState({ source: "counties", id: f }, fills.get(f)!);
      }
    };
  }, [ready, race]);

  useEffect(() => {
    const m = map.current;
    if (!ready || !m || !selected) return;
    m.setFeatureState({ source: "counties", id: selected }, { selected: true });
    return () => { m.setFeatureState({ source: "counties", id: selected }, { selected: false }); };
  }, [ready, selected]);

  // Keyboard path: arrows step through counties alphabetically, Escape returns to all of Texas.
  const alpha = useRef([...names.current.entries()].sort((a, b) => a[1].localeCompare(b[1])).map(([f]) => f));
  const onKeyDown = (e: React.KeyboardEvent) => {
    const list = alpha.current;
    const at = selected ? list.indexOf(selected) : -1;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") onSelect(list[(at + 1) % list.length]);
    else if (e.key === "ArrowLeft" || e.key === "ArrowUp") onSelect(list[(at - 1 + list.length) % list.length]);
    else if (e.key === "Escape") onSelect(null);
    else return;
    e.preventDefault();
  };

  const resetView = () => {
    const m = map.current;
    if (m) m.easeTo({ ...homeCamera(m, el.current!, is3d), pitch: m.getPitch(), bearing: m.getBearing(), duration: reducedMotion() ? 0 : 700 });
  };

  // 2D/3D switch: flatten the blocks and the camera together.
  useEffect(() => {
    const m = map.current;
    if (!ready || !m) return;
    m.setPaintProperty("blocks", "fill-extrusion-height", is3d ? HEIGHT : 0);
    m.setLayoutProperty("borders", "visibility", is3d ? "none" : "visible");
    const cam = homeCamera(m, el.current!, is3d);
    home.current = { zoom: cam.zoom, pitch: cam.pitch, bearing: cam.bearing };
    m.easeTo({ ...cam, duration: reducedMotion() ? 0 : 800 });
  }, [ready, is3d]);

  const tipInfo = tip && race ? (() => {
    const o = countyOutcome(race, tip.fips);
    const name = names.current.get(tip.fips);
    if (!o.winnerId) return { name, line: "No votes reported", party: null };
    const w = race.candidates[o.winnerId];
    return { name, line: `${lastName(w.name)} ${official ? "won" : "leads"} with ${winnerShare(race, tip.fips).toFixed(1)}%`, party: w.party };
  })() : null;

  return (
    <div className="map-wrap">
      <div ref={el} className="map" role="application" tabIndex={0} onKeyDown={onKeyDown}
        aria-label="3D map of Texas counties: color shows the winning party, block height shows the winner's vote share. Use the arrow keys to step through counties alphabetically; Escape returns to all of Texas." />
      <div className="dims" role="radiogroup" aria-label="Map view">
        <button type="button" role="radio" aria-checked={!is3d} className={is3d ? "" : "is-on"} onClick={() => onIs3d(false)}>2D</button>
        <button type="button" role="radio" aria-checked={is3d} className={is3d ? "is-on" : ""} onClick={() => onIs3d(true)}>3D</button>
      </div>
      {is3d && (
        <div className="tilt">
          <label>
            <span>Tilt</span>
            <input type="range" min={0} max={60} step={1} value={tilt}
              aria-valuetext={`${tilt} degrees up from flat`}
              onChange={(e) => map.current?.setPitch(Number(e.target.value))} />
          </label>
          <label>
            <span>Rotate</span>
            <input type="range" min={-180} max={180} step={1} value={turn}
              aria-valuetext={`${turn} degrees from north`}
              onChange={(e) => map.current?.setBearing(Number(e.target.value))} />
          </label>
        </div>
      )}
      {moved && <button type="button" className="map-reset" onClick={resetView}>Show all of Texas</button>}
      {tip && tipInfo && (
        <div className="map-tip" style={{ transform: `translate(${tip.x + 14}px, ${tip.y + 14}px)` }} aria-hidden="true">
          <strong>{tipInfo.name} County</strong>
          <span>
            {tipInfo.party && <i className={`swatch swatch--${tipInfo.party}`} />}
            {tipInfo.line}
            {tipInfo.party && <em> · {PARTY_NAME[tipInfo.party]}</em>}
          </span>
        </div>
      )}
    </div>
  );
}
