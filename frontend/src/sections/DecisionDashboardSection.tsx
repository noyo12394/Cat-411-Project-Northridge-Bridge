import type { ReactNode } from 'react'
import { BridgeStateVisual } from '../components/visuals/BridgeStateVisual.tsx'
import { MetricCard } from '../components/common/MetricCard'
import { Panel } from '../components/common/Panel'
import { SectionShell } from '../components/common/SectionShell'
import { DASHBOARD_MODES } from '../lib/dashboardModel'
import type {
  DashboardAssessment,
  DashboardInputs,
  DashboardModeId,
  ResearchData,
} from '../types/research'

interface DecisionDashboardSectionProps {
  data: ResearchData
  mode: DashboardModeId
  inputs: DashboardInputs
  assessment: DashboardAssessment
  onModeChange: (mode: DashboardModeId) => void
  onInputChange: <K extends keyof DashboardInputs>(field: K, value: DashboardInputs[K]) => void
  onLoadSample: (structureNumber: string) => void
  onReset: () => void
}

function Field({
  label,
  help,
  children,
}: {
  label: string
  help: string
  children: ReactNode
}) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-semibold text-ink">{label}</span>
      {children}
      <span className="block text-xs leading-5 text-muted">{help}</span>
    </label>
  )
}

export function DecisionDashboardSection({
  data,
  mode,
  inputs,
  assessment,
  onModeChange,
  onInputChange,
  onLoadSample,
  onReset,
}: DecisionDashboardSectionProps) {
  const watchlist = [...data.portfolio]
    .sort((left, right) => right.priorityScore - left.priorityScore)
    .slice(0, 5)

  return (
    <SectionShell
      id="decision-dashboard"
      index="08"
      eyebrow="decision dashboard"
      title="A live operational workbench with explicit model modes."
      description="This is the interactive interface: choose a bridge or enter a synthetic case, switch between intrinsic vulnerability, event damage, and prioritization, and watch the bridge twin respond in real time."
    >
      <div className="flex flex-wrap gap-3">
        {DASHBOARD_MODES.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => onModeChange(tab.id)}
            className={
              mode === tab.id
                ? 'rounded-full border border-seismic/30 bg-seismic/12 px-5 py-3 text-sm font-semibold text-seismic'
                : 'rounded-full border border-line bg-white/5 px-5 py-3 text-sm font-semibold text-muted'
            }
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.88fr_1.12fr] xl:items-start">
        <Panel
          eyebrow="bridge input panel"
          title="Bridge selection or synthetic input"
          description="The controls update live. Structural fields always matter; PGA only matters in event mode; ADT only matters in prioritization."
        >
          <div className="mb-5 flex flex-wrap gap-2">
            {data.summary.sampleBridges.map((sample) => (
              <button
                key={sample.structureNumber}
                type="button"
                onClick={() => onLoadSample(sample.structureNumber)}
                className="rounded-full border border-line bg-white/6 px-4 py-2 text-sm text-muted transition hover:border-seismic/20 hover:text-ink"
              >
                {sample.label}
              </button>
            ))}
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <Field
              label="Structure number"
              help="Paste the bridge identifier directly, or use the sample bridge pills above."
            >
              <input
                className="lab-input"
                value={inputs.structureNumber}
                onChange={(event) => onInputChange('structureNumber', event.target.value)}
              />
            </Field>
            <Field
              label="Bridge class / HWB class"
              help="Structural family descriptor carried through the engineering and ML layers."
            >
              <select
                className="lab-input"
                value={inputs.bridgeClass}
                onChange={(event) => onInputChange('bridgeClass', event.target.value)}
              >
                {['HWB1', 'HWB2', 'HWB3', 'HWB4', 'HWB5', 'HWB6', 'HWB7', 'HWB8', 'HWB9', 'HWB10', 'HWB11', 'HWB12'].map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </Field>

            <Field
              label="Year built"
              help="Earlier design eras tend to correspond to weaker seismic detailing assumptions."
            >
              <input
                className="lab-input"
                type="number"
                value={inputs.yearBuilt}
                onChange={(event) => onInputChange('yearBuilt', Number(event.target.value))}
              />
            </Field>
            <Field
              label="Reconstructed year"
              help="Leave blank when no rehabilitation history is known."
            >
              <input
                className="lab-input"
                type="number"
                value={inputs.yearReconstructed}
                onChange={(event) =>
                  onInputChange(
                    'yearReconstructed',
                    event.target.value === '' ? '' : Number(event.target.value),
                  )
                }
              />
            </Field>

            <Field label="Number of spans" help="Structural geometry complexity indicator.">
              <input
                className="lab-input"
                type="number"
                value={inputs.spans}
                onChange={(event) => onInputChange('spans', Number(event.target.value))}
              />
            </Field>
            <Field
              label="Max span length (ft)"
              help="Longer spans raise demand concentration and consequence."
            >
              <input
                className="lab-input"
                type="number"
                value={inputs.maxSpan}
                onChange={(event) => onInputChange('maxSpan', Number(event.target.value))}
              />
            </Field>

            <Field label="Skew (degrees)" help="Higher skew can amplify irregular response.">
              <input
                className="lab-input"
                type="number"
                value={inputs.skew}
                onChange={(event) => onInputChange('skew', Number(event.target.value))}
              />
            </Field>
            <Field label="Condition rating" help="0 is poor, 9 is excellent.">
              <input
                className="lab-input"
                type="number"
                min="0"
                max="9"
                step="0.1"
                value={inputs.condition}
                onChange={(event) => onInputChange('condition', Number(event.target.value))}
              />
            </Field>

            <Field
              label="SVI score"
              help="Bridge-intrinsic structural screening score from the SVI workflow."
            >
              <input
                className="lab-input"
                type="number"
                min="0"
                max="1"
                step="0.001"
                value={inputs.svi}
                onChange={(event) => onInputChange('svi', Number(event.target.value))}
              />
            </Field>
            <Field
              label="ADT / traffic"
              help="This matters in prioritization, not in the intrinsic vulnerability score."
            >
              <input
                className="lab-input"
                type="number"
                value={inputs.adt}
                onChange={(event) => onInputChange('adt', Number(event.target.value))}
              />
            </Field>

            <Field
              label="Scenario PGA"
              help="Hazard demand is available, but only event mode is allowed to use it."
            >
              <input
                className="lab-input"
                type="number"
                min="0"
                max="0.45"
                step="0.01"
                value={inputs.scenarioPga}
                onChange={(event) => onInputChange('scenarioPga', Number(event.target.value))}
              />
            </Field>
            <Field
              label="NDVI change"
              help="Optional post-event evidence. It augments context rather than replacing structural logic."
            >
              <input
                className="lab-input"
                type="number"
                min="-0.35"
                max="0.2"
                step="0.01"
                value={inputs.ndviChange}
                onChange={(event) =>
                  onInputChange('ndviChange', event.target.value === '' ? '' : Number(event.target.value))
                }
              />
            </Field>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button type="button" className="lab-button lab-button-primary" onClick={onReset}>
              Reset to seeded bridge
            </button>
            <button type="button" className="lab-button" onClick={() => onLoadSample(data.summary.sampleBridges[1]?.structureNumber ?? '')}>
              Load reference sample
            </button>
          </div>
        </Panel>

        <div className="space-y-5 xl:sticky xl:top-24">
          <div className="grid gap-4 md:grid-cols-3">
            <MetricCard label="intrinsic" value={assessment.intrinsicScore.toFixed(3)} accent="seismic" />
            <MetricCard label="event damage" value={assessment.eventScore.toFixed(3)} accent="hazard" />
            <MetricCard label="priority" value={assessment.priorityScore.toFixed(3)} accent="signal" />
          </div>

          <BridgeStateVisual
            assessment={assessment}
            title="Decision-support bridge twin"
            caption="The visual twin follows structural severity continuously. Priority mode adds urgency and traffic consequence without faking extra structural collapse."
          />

          <div className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
            <Panel
              eyebrow="why this bridge"
              title="Interpretability summary"
              description="These are the strongest drivers in the current query, sorted by contribution."
            >
              <div className="space-y-3">
                {assessment.drivers.slice(0, 6).map((driver) => (
                  <div key={driver.key} className="rounded-[1.4rem] border border-line bg-white/5 p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-semibold text-ink">{driver.label}</h3>
                        <p className="mt-2 text-sm leading-6 text-muted">{driver.description}</p>
                      </div>
                      <div className="rounded-full border border-line bg-white/6 px-3 py-1 text-sm text-ink">
                        {driver.value.toFixed(3)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Panel>

            <div className="space-y-5">
              <Panel
                eyebrow="current output"
                title={`${assessment.damageLabel} / ${assessment.riskLevel}`}
                description={assessment.narrative}
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <MetricCard label="active score" value={assessment.headlineScore.toFixed(3)} accent="hazard" />
                  <MetricCard label="confidence" value={assessment.confidenceLabel} accent="moss" />
                  <MetricCard label="traffic band" value={assessment.trafficLabel} accent="signal" />
                  <MetricCard label="mode label" value={assessment.scenarioLabel} accent="seismic" />
                </div>
              </Panel>

              <Panel
                eyebrow="recommendations"
                title="Decision guidance"
                description="Short, mode-specific guidance derived from the current state."
              >
                <div className="space-y-3">
                  {assessment.recommendations.map((item) => (
                    <div key={item.title} className="rounded-[1.4rem] border border-line bg-white/5 p-4">
                      <h3 className="font-semibold text-ink">{item.title}</h3>
                      <p className="mt-2 text-sm leading-6 text-muted">{item.detail}</p>
                    </div>
                  ))}
                </div>
              </Panel>
            </div>
          </div>
        </div>
      </div>

      <Panel
        eyebrow="portfolio watchlist"
        title="High-priority bridges from the exported statewide portfolio"
        description="These are not derived from the current form state; they come from the exported portfolio ranking and give the dashboard a real statewide operational context."
      >
        <div className="grid gap-4 lg:grid-cols-5">
          {watchlist.map((bridge) => (
            <button
              key={bridge.structureNumber}
              type="button"
              onClick={() => onLoadSample(bridge.structureNumber)}
              className="rounded-[1.5rem] border border-line bg-white/5 p-4 text-left transition hover:border-seismic/24 hover:bg-white/8"
            >
              <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted">
                {bridge.countyLabel}
              </p>
              <h3 className="mt-3 font-display text-xl font-semibold tracking-[-0.04em] text-ink">
                {bridge.structureNumber}
              </h3>
              <p className="mt-2 text-sm text-muted">
                priority {bridge.priorityScore.toFixed(3)} / {bridge.bridgeClass}
              </p>
            </button>
          ))}
        </div>
      </Panel>
    </SectionShell>
  )
}
