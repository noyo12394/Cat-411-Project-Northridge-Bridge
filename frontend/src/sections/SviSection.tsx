import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { ChartFrame } from '../components/charts/ChartFrame'
import { Panel } from '../components/common/Panel'
import { SectionShell } from '../components/common/SectionShell'
import type { DashboardInputs, ResearchData } from '../types/research'

interface SviSectionProps {
  data: ResearchData
  inputs: DashboardInputs
}

export function SviSection({ data, inputs }: SviSectionProps) {
  const selectedBridge =
    data.portfolio.find((bridge) => bridge.structureNumber === inputs.structureNumber) ?? null

  const priorRows = data.methodology.priors.map((prior) => ({
    label: prior.label,
    weight: prior.weight,
  }))

  const componentRows = selectedBridge
    ? [
        { label: 'Condition', value: selectedBridge.componentCondition },
        { label: 'SVI', value: selectedBridge.componentSVI },
        { label: 'Age', value: selectedBridge.componentAge },
        { label: 'Rehab', value: selectedBridge.componentRehab },
        { label: 'Skew', value: selectedBridge.componentSkew },
        { label: 'Max span', value: selectedBridge.componentMaxSpan },
        { label: 'Class', value: selectedBridge.componentBridgeClass },
        { label: 'Spans', value: selectedBridge.componentSpans },
      ]
    : []

  return (
    <SectionShell
      id="svi"
      index="04"
      eyebrow="SVI"
      title="SVI acts as an interpretable structural screening layer."
      description="This section explains the Seismic Vulnerability Index as a weighted, bridge-intrinsic screening device. The goal is immediate academic legibility: what goes in, how it is weighted, and what a higher score means."
    >
      <div className="grid gap-5 xl:grid-cols-[0.88fr_1.12fr]">
        <Panel
          eyebrow="interpretation"
          title="Why SVI matters here"
          description="SVI is not a magic number. It is the bridge-specific screening layer that helps connect engineering intuition with the machine-learning vulnerability story."
        >
          <div className="space-y-4 text-sm leading-7 text-muted">
            <p>
              A low SVI means the bridge looks structurally more stable on the repo’s weighted
              screening criteria.
            </p>
            <p>
              A high SVI means the bridge’s age, condition, skew, geometry, and structural family are
              collectively pushing it toward greater intrinsic vulnerability.
            </p>
            <p>
              The UI keeps SVI visible because it is one of the fastest ways to explain the project’s
              structural logic to a professor or reviewer.
            </p>
          </div>
        </Panel>

        <ChartFrame
          title="SVI weighting priors"
          description="These are the explicit contribution weights exported from the methodology layer."
        >
          <div className="h-[280px]">
            <ResponsiveContainer>
              <BarChart data={priorRows}>
                <CartesianGrid stroke="rgba(132,157,186,0.12)" strokeDasharray="4 8" />
                <XAxis dataKey="label" tick={{ fill: '#9db0c8', fontSize: 12 }} angle={-18} textAnchor="end" height={60} />
                <YAxis tick={{ fill: '#9db0c8', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    borderRadius: 20,
                    border: '1px solid rgba(173,196,223,0.18)',
                    background: 'rgba(9,15,24,0.94)',
                    color: '#eff4fb',
                  }}
                />
                <Bar dataKey="weight" fill="#7dd3fc" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartFrame>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <ChartFrame
          title="Current bridge contribution profile"
          description="When a bridge is selected in the workbench, its normalized contribution pattern is surfaced here so the SVI logic becomes instantly explainable."
        >
          <div className="h-[320px]">
            <ResponsiveContainer>
              <BarChart data={componentRows} layout="vertical">
                <CartesianGrid stroke="rgba(132,157,186,0.12)" strokeDasharray="4 8" />
                <XAxis type="number" tick={{ fill: '#9db0c8', fontSize: 12 }} />
                <YAxis type="category" dataKey="label" tick={{ fill: '#9db0c8', fontSize: 12 }} width={86} />
                <Tooltip
                  contentStyle={{
                    borderRadius: 20,
                    border: '1px solid rgba(173,196,223,0.18)',
                    background: 'rgba(9,15,24,0.94)',
                    color: '#eff4fb',
                  }}
                />
                <Bar dataKey="value" fill="#66d1a6" radius={[0, 10, 10, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartFrame>

        <Panel
          eyebrow="current state"
          title="Selected bridge SVI context"
          description="This ties the bridge-specific SVI value back to the broader statewide portfolio."
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-[1.6rem] border border-line bg-white/5 p-4">
              <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted">selected SVI</p>
              <p className="mt-3 font-display text-4xl text-ink">{inputs.svi.toFixed(3)}</p>
            </div>
            <div className="rounded-[1.6rem] border border-line bg-white/5 p-4">
              <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted">statewide mean SVI</p>
              <p className="mt-3 font-display text-4xl text-ink">
                {data.summary.portfolio.meanSVI.toFixed(3)}
              </p>
            </div>
          </div>
          <div className="mt-5 rounded-[1.6rem] border border-line bg-white/5 p-4 text-sm leading-7 text-muted">
            The selected bridge is{' '}
            <span className="text-ink">
              {inputs.svi >= data.summary.portfolio.meanSVI ? 'above' : 'below'}
            </span>{' '}
            the portfolio mean, which is why the SVI layer is such a useful screening reference before
            the dashboard moves into hazard or prioritization.
          </div>
        </Panel>
      </div>
    </SectionShell>
  )
}
