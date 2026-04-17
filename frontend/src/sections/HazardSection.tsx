import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { ChartFrame } from '../components/charts/ChartFrame'
import { MetricCard } from '../components/common/MetricCard'
import { Panel } from '../components/common/Panel'
import { SectionShell } from '../components/common/SectionShell'
import { PortfolioScatter } from '../components/visuals/PortfolioScatter'
import type { ResearchData } from '../types/research'

interface HazardSectionProps {
  data: ResearchData
  scenarioPga: number
  onScenarioChange: (nextValue: number) => void
}

function figurePath(data: ResearchData, file: string) {
  return data.researchFigures.find((item) => item.file === file)?.path ?? null
}

export function HazardSection({
  data,
  scenarioPga,
  onScenarioChange,
}: HazardSectionProps) {
  const hazard = data.hazardProfile
  const meanFigure = figurePath(data, 'future_scenario_mean_edr.png')
  const riskFigure = figurePath(data, 'future_scenario_risk_bands.png')

  return (
    <SectionShell
      id="hazard"
      index="02"
      eyebrow="hazard"
      title="Hazard is event-specific and enters only when the question is damage."
      description="This section carries the Northridge hindcast and scenario logic. The slider below is allowed to alter event damage, but it never rewires the intrinsic vulnerability layer."
    >
      <div className="grid gap-5 xl:grid-cols-[0.78fr_1.22fr]">
        <Panel
          eyebrow="scenario control"
          title="PGA scenario panel"
          description="Scrubbing the PGA slider updates the shared dashboard state and the bridge twin. This is where seismic demand belongs."
        >
          <div className="space-y-6">
            <div className="rounded-[1.8rem] border border-line bg-white/5 p-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted">
                    scenario PGA
                  </p>
                  <p className="mt-2 font-display text-4xl tracking-[-0.05em] text-ink">
                    {scenarioPga.toFixed(2)} g
                  </p>
                </div>
                <div className="rounded-full border border-seismic/20 bg-seismic/10 px-4 py-2 text-sm text-seismic">
                  event mode only
                </div>
              </div>
              <input
                className="lab-range mt-6"
                type="range"
                min="0"
                max="0.45"
                step="0.01"
                value={scenarioPga}
                onChange={(event) => onScenarioChange(Number(event.target.value))}
              />
              <div className="mt-3 flex justify-between font-mono text-[11px] uppercase tracking-[0.24em] text-muted">
                <span>0.00 g</span>
                <span>0.20 g</span>
                <span>0.45 g</span>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <MetricCard
                label="hazard sampled bridges"
                value={data.summary.counts.hazardSampled.toLocaleString()}
                detail="Bridges with sampled ShakeMap PGA in the repo workflow."
                accent="signal"
              />
              <MetricCard
                label="positive PGA bridges"
                value={(hazard?.positivePgaBridges ?? data.summary.counts.hazardSampled).toLocaleString()}
                detail="Bridges with non-zero event demand in the exported hazard profile."
                accent="hazard"
              />
            </div>

            {hazard ? (
              <div className="grid gap-4 sm:grid-cols-3">
                <MetricCard
                  label="p90 PGA"
                  value={`${hazard.quantiles.p90.toFixed(3)} g`}
                  accent="seismic"
                />
                <MetricCard
                  label="p95 PGA"
                  value={`${hazard.quantiles.p95.toFixed(3)} g`}
                  accent="signal"
                />
                <MetricCard
                  label="max PGA"
                  value={`${hazard.quantiles.max.toFixed(3)} g`}
                  accent="hazard"
                />
              </div>
            ) : null}
          </div>
        </Panel>

        <div className="grid gap-5">
          <ChartFrame
            title="Future scenario damage curve"
            description="The repo-exported scenario summary shows how mean predicted EDR rises as PGA increases. The event model is powerful, but it belongs strictly to the hazard-specific layer."
          >
            <div className="h-[320px]">
              <ResponsiveContainer>
                <AreaChart data={data.futureScenarios}>
                  <defs>
                    <linearGradient id="hazardArea" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#7dd3fc" stopOpacity={0.55} />
                      <stop offset="100%" stopColor="#7dd3fc" stopOpacity={0.04} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(132,157,186,0.12)" strokeDasharray="4 8" />
                  <XAxis dataKey="scenario" tick={{ fill: '#9db0c8', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9db0c8', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 20,
                      border: '1px solid rgba(173,196,223,0.18)',
                      background: 'rgba(9,15,24,0.94)',
                      color: '#eff4fb',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="meanPredictedEdr"
                    stroke="#7dd3fc"
                    fill="url(#hazardArea)"
                    strokeWidth={3}
                  />
                  <Line type="monotone" dataKey="p95PredictedEdr" stroke="#ff9c69" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </ChartFrame>

          <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <ChartFrame
              title="Hazard intensity footprint"
              description="A lightweight California scatter derived from exported bridge coordinates. Larger points indicate stronger sampled PGA."
            >
              <PortfolioScatter
                points={
                  hazard?.samplePoints.map((point) => ({
                    structureNumber: point.structureNumber,
                    latitude: point.latitude,
                    longitude: point.longitude,
                    value: point.pga,
                    label: point.countyLabel,
                  })) ?? []
                }
                hue="hazard"
              />
            </ChartFrame>

            <div className="grid gap-5">
              <ChartFrame
                title="PGA distribution"
                description="Repo-backed histogram from the hazard export. It supports the hindcast framing instead of pretending every bridge saw the same demand."
              >
                <div className="h-[220px]">
                  <ResponsiveContainer>
                    <LineChart data={hazard?.histogram ?? []}>
                      <CartesianGrid stroke="rgba(132,157,186,0.12)" strokeDasharray="4 8" />
                      <XAxis dataKey="label" tick={{ fill: '#9db0c8', fontSize: 12 }} />
                      <YAxis tick={{ fill: '#9db0c8', fontSize: 12 }} />
                      <Tooltip
                        contentStyle={{
                          borderRadius: 20,
                          border: '1px solid rgba(173,196,223,0.18)',
                          background: 'rgba(9,15,24,0.94)',
                          color: '#eff4fb',
                        }}
                      />
                      <Line type="monotone" dataKey="count" stroke="#ffd166" strokeWidth={3} dot={{ r: 2 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </ChartFrame>

              <Panel
                eyebrow="research figures"
                title="Exported evidence from the Python workflow"
                description="Where the repo already has figures, the site surfaces them directly instead of rebuilding everything as browser-native charts."
              >
                <div className="grid gap-4 md:grid-cols-2">
                  {[meanFigure, riskFigure].filter(Boolean).map((path) => (
                    <img
                      key={path}
                      src={path!}
                      alt="Hazard research figure"
                      className="rounded-[1.6rem] border border-line bg-basin object-cover"
                    />
                  ))}
                </div>
              </Panel>
            </div>
          </div>
        </div>
      </div>
    </SectionShell>
  )
}
