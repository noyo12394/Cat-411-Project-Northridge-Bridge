import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
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
import type { DashboardInputs, ResearchData } from '../types/research'

interface AssetFragilitySectionProps {
  data: ResearchData
  inputs: DashboardInputs
}

export function AssetFragilitySection({
  data,
  inputs,
}: AssetFragilitySectionProps) {
  const selectedBridge =
    data.portfolio.find((bridge) => bridge.structureNumber === inputs.structureNumber) ?? null
  const fragility = data.fragilityProfile
  const damageByClass = fragility?.damageByClass.slice(0, 6) ?? []
  const curves = fragility?.fragilityCurves ?? []

  return (
    <SectionShell
      id="asset-fragility"
      index="03"
      eyebrow="asset + fragility"
      title="Bridge attributes and fragility logic stay legible together."
      description="This section keeps the structural asset description tangible: age, geometry, skew, condition, bridge class, and span configuration, then connects those attributes to fragility behavior rather than burying everything inside one opaque risk number."
    >
      <div className="grid gap-5 xl:grid-cols-[0.84fr_1.16fr]">
        <Panel
          eyebrow="active bridge"
          title="Structural attribute deck"
          description="These are the bridge-level variables driving the current query. They are exactly the kind of descriptors professors expect to see before any hazard scenario is invoked."
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <MetricCard label="year built" value={String(inputs.yearBuilt)} accent="signal" />
            <MetricCard
              label="reconstructed"
              value={inputs.yearReconstructed === '' ? 'none' : String(inputs.yearReconstructed)}
              accent="moss"
            />
            <MetricCard label="spans" value={String(inputs.spans)} accent="seismic" />
            <MetricCard label="max span" value={`${inputs.maxSpan.toFixed(0)} ft`} accent="seismic" />
            <MetricCard label="skew" value={`${inputs.skew.toFixed(0)}°`} accent="signal" />
            <MetricCard label="condition" value={inputs.condition.toFixed(1)} accent="moss" />
            <MetricCard label="HAZUS class" value={inputs.bridgeClass} accent="hazard" />
            <MetricCard label="SVI" value={inputs.svi.toFixed(3)} accent="seismic" />
          </div>

          {selectedBridge ? (
            <div className="mt-5 rounded-[1.8rem] border border-line bg-white/5 p-5 text-sm leading-7 text-muted">
              <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-seismic/70">
                current portfolio reference
              </p>
              <p className="mt-3">
                Structure <span className="text-ink">{selectedBridge.structureNumber}</span> in{' '}
                <span className="text-ink">{selectedBridge.countyLabel}</span> currently sits in the{' '}
                <span className="text-ink">{selectedBridge.riskBand}</span> band with exported EDR{' '}
                <span className="text-ink">{selectedBridge.edr.toFixed(3)}</span>.
              </p>
            </div>
          ) : null}
        </Panel>

        <div className="grid gap-5">
          <ChartFrame
            title="Fragility curve families"
            description="These curves are exported from the research pipeline by grouping lower-, middle-, and higher-vulnerability bridges and tracing damage-state exceedance as PGA increases."
          >
            <div className="h-[320px]">
              <ResponsiveContainer>
                <LineChart
                  data={curves.flatMap((curve) =>
                    curve.points.map((point) => ({
                      ...point,
                      band: curve.label,
                    })),
                  )}
                >
                  <CartesianGrid stroke="rgba(132,157,186,0.12)" strokeDasharray="4 8" />
                  <XAxis dataKey="pga" tick={{ fill: '#9db0c8', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9db0c8', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 20,
                      border: '1px solid rgba(173,196,223,0.18)',
                      background: 'rgba(9,15,24,0.94)',
                      color: '#eff4fb',
                    }}
                  />
                  <Legend />
                  {curves.map((curve, index) => (
                    <Line
                      key={curve.label}
                      type="monotone"
                      data={curve.points}
                      name={`${curve.label} EDR`}
                      dataKey="edr"
                      stroke={['#7dd3fc', '#ffd166', '#f97373'][index] ?? '#7dd3fc'}
                      strokeWidth={3}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartFrame>

          <div className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
            <ChartFrame
              title="Average damage-state composition by class"
              description="The exported bridge classes still matter. This view makes it easier to discuss structural family effects before moving into the ML section."
            >
              <div className="h-[320px]">
                <ResponsiveContainer>
                  <BarChart data={damageByClass}>
                    <CartesianGrid stroke="rgba(132,157,186,0.12)" strokeDasharray="4 8" />
                    <XAxis dataKey="bridgeClass" tick={{ fill: '#9db0c8', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#9db0c8', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        borderRadius: 20,
                        border: '1px solid rgba(173,196,223,0.18)',
                        background: 'rgba(9,15,24,0.94)',
                        color: '#eff4fb',
                      }}
                    />
                    <Legend />
                    <Bar dataKey="ds1" stackId="damage" fill="#7dd3fc" name="Slight" />
                    <Bar dataKey="ds2" stackId="damage" fill="#66d1a6" name="Moderate" />
                    <Bar dataKey="ds3" stackId="damage" fill="#ffd166" name="Extensive" />
                    <Bar dataKey="ds4" stackId="damage" fill="#f97373" name="Complete" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartFrame>

            <Panel
              eyebrow="discipline"
              title="What belongs here"
              description="Fragility is the bridge between asset properties and damage estimation. This section intentionally stays structural and fragility-oriented rather than drifting into ML or operational urgency."
            >
              <div className="space-y-4 text-sm leading-7 text-muted">
                <p>
                  The bridge attributes shown at left remain stable descriptors of the asset itself.
                </p>
                <p>
                  Fragility logic translates those descriptors into damage susceptibility, but still
                  does not justify putting PGA inside the intrinsic screening mode.
                </p>
                <p>
                  In the dashboard, fragility is what prepares the transition from asset knowledge to
                  event-specific damage estimation.
                </p>
              </div>
            </Panel>
          </div>
        </div>
      </div>
    </SectionShell>
  )
}
