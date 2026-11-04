export type Party = "REP" | "DEM" | "LIB" | "GRN" | "WRI" | "IND";
export type Office = "PRES" | "SEN" | "GOV";

export interface StatewideRow {
  id: string;
  name: string;
  party: Party;
  votes: number;
  pct: number;
}

export interface RaceSummary {
  id: string;
  year: number;
  office: Office;
  officeLabel: string;
  date: string;
  status: "canvassed" | "unofficial";
  source: string;
  sourceLabel: string;
  countiesReported: number;
  total: number;
  countiesWon: Partial<Record<Party, number>>;
  statewide: StatewideRow[];
}

export interface CountyResult {
  total: number;
  results: [candidateId: string, votes: number][]; // sorted by votes, descending
}

export interface RaceResults {
  id: string;
  candidates: Record<string, { name: string; party: Party }>;
  counties: Record<string, CountyResult>;
}

export const OFFICES: { id: Office; label: string; short: string }[] = [
  { id: "PRES", label: "President", short: "President" },
  { id: "SEN", label: "U.S. Senate", short: "Senate" },
  { id: "GOV", label: "Governor", short: "Governor" },
];

export const PARTY_NAME: Record<Party, string> = {
  REP: "Republican",
  DEM: "Democrat",
  LIB: "Libertarian",
  GRN: "Green",
  WRI: "Write-in",
  IND: "Independent",
};

/** Fabric shades, keyed by party and margin band. Party color is data only. */
export const FABRIC = {
  REP: ["#f2a0a6", "#dc4a55", "#b01e2c"],
  DEM: ["#97b8ee", "#3f75d4", "#1a4aa3"],
  OTHER: ["#ece6d3", "#ddd2b0", "#c9b98a"],
  UNREPORTED: "#e8e6ee",
} as const;

export const MARGIN_BANDS = [
  { label: "<10 pts", min: 0 },
  { label: "10–30 pts", min: 10 },
  { label: "30+ pts", min: 30 },
];

export function marginBand(marginPts: number): number {
  return marginPts >= 30 ? 2 : marginPts >= 10 ? 1 : 0;
}

export interface CountyOutcome {
  winnerId: string | null;
  party: Party | null;
  marginPts: number; // winner pct minus runner-up pct
  total: number;
}

export function countyOutcome(race: RaceResults, fips: string): CountyOutcome {
  const c = race.counties[fips];
  if (!c || c.total === 0) return { winnerId: null, party: null, marginPts: 0, total: 0 };
  const [first, second] = c.results;
  const margin = ((first[1] - (second?.[1] ?? 0)) / c.total) * 100;
  return { winnerId: first[0], party: race.candidates[first[0]].party, marginPts: margin, total: c.total };
}

export function fabricFor(o: CountyOutcome): string {
  if (!o.party) return FABRIC.UNREPORTED;
  const band = marginBand(o.marginPts);
  if (o.party === "REP") return FABRIC.REP[band];
  if (o.party === "DEM") return FABRIC.DEM[band];
  return FABRIC.OTHER[band];
}

const cache = new Map<string, Promise<unknown>>();
function getJSON<T>(path: string): Promise<T> {
  if (!cache.has(path)) {
    const p = fetch(`${import.meta.env.BASE_URL}data/${path}`).then((r) => {
      if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
      return r.json();
    });
    p.catch(() => cache.delete(path));
    cache.set(path, p);
  }
  return cache.get(path) as Promise<T>;
}

export const loadRaces = () => getJSON<RaceSummary[]>("races.json");
export const loadRace = (id: string) => getJSON<RaceResults>(`results/${id}.json`);
export const loadCounties = () => getJSON<GeoJSON.FeatureCollection<GeoJSON.Polygon | GeoJSON.MultiPolygon, { fips: string; name: string }>>("tx-counties.geojson");

export const fmt = new Intl.NumberFormat("en-US");
export const fmtPct = (n: number) => (n > 0 && n < 0.05 ? "<0.1%" : `${n.toFixed(1)}%`);


export function lastName(name: string): string {
  const first = name.split(" / ")[0].replace(/\s*\(.*?\)|"[^"]*"/g, "").trim();
  const parts = first.split(/\s+/);
  const last = parts[parts.length - 1];
  return /^(Jr\.?|Sr\.?|II|III)$/i.test(last) ? parts[parts.length - 2] : last;
}
