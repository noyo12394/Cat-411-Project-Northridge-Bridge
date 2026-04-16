import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { ChartFrame } from '../components/charts/ChartFrame'
import { MetricCard } from '../components/common/MetricCard'
import { Panel } from '../components/common/Panel'
import { SectionShell } from '../components/common/SectionShell'
import type { ResearchData } from '../types/research'

interface ValidationSectionProps {
  data: ResearchData
}

export function ValidationSection({ data }: ValidationSectionProps) {
  const proxyModels = data.proxyValidation.models
  const bridgeMlMetrics = data.dataHealth?.bridgeMlCalibrationMetrics

  return (
    <SectionShell
      id="validation"
      index="07"
      eyebrow="validation"
      title="The dashboard stays defensible by surfacing evidence, not just scores."
      description="Validation matters because this is ultimately a research interface. The site exposes calibration evidence, proxy-validation comparisons, and metrics that can be defended in academic review."
    >
      <div className="grid gap-5 lg:grid-cols-[1.08fr_0.92fr]">
        <ChartFrame
          title="Calibration scatter from exported bridge ML artifact"
          description="This scatter is taken from the repo-backed calibration points already exported into the site summary."
          aside={
            bridgeMlMetrics ? (
              <div className="rounded-full border border-line bg-white/6 px-4 py-2 text-sm text-muted">
                {bridgeMlMetrics.modelLabel}
              </div>
            ) : null
          }
        >
          <div className="h-[360px]">
            <ResponsiveContainer>
              <ScatterChart>
                <CartesianGrid stroke="rgba(132,157,186,0.12)" strokeDasharray="4 8" />
                <XAxis
                  type="number"
                  dataKey="Actual_EDR"
                  tick={{ fill: '#9db0c8', fontSize: 12 }}
                  name="Actual EDR"
                />
                <YAxis
                  type="number"
                  dataKey="Predicted_EDR"
                  tick={{ fill: '#9db0c8', fontSize: 12 }}
                  name="Predicted EDR"
                />
                <Tooltip
                  cursor={{ strokeDasharray: '4 8' }}
                  contentStyle={{
                    borderRadius: 20,
                    border: '1px solid rgba(173,196,223,0.18)',
                    background: 'rgba(9,15,24,0.94)',
                    color: '#eff4fb',
                  }}
                />
                <Scatter data={data.summary.calibrationPoints} fill="#7dd3fc" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </ChartFrame>

        <Panel
          eyebrow="proxy validation"
          title="Reference comparison"
          description="The proxy-validation subset is not perfect ground truth, but it gives the project a more credible validation story than reporting only a single aggregate metric."
        >
          <div className="grid gap-4">
            {proxyModels.map((model) => (
              <div key={model.label} className="rounded-[1.6rem] border border-line bg-white/5 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-display text-xl font-semibold tracking-[-0.04em] text-ink">
                      {model.label}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-muted">
                      Exact accuracy {model.exactAccuracy.toFixed(3)}, within-one-state accuracy{' '}
                      {model.withinOneStateAccuracy.toFixed(3)}, weighted kappa{' '}
                      {model.weightedKappa.toFixed(3)}.
                    </p>
                  </div>
                  <div className="rounded-full border border-line bg-white/6 px-3 py-2 font-mono text-[11px] uppercase tracking-[0.24em] text-muted">
                    underprediction {model.underpredictionRate.toFixed(3)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {bridgeMlMetrics ? (
        <div className="grid gap-4 md:grid-cols-3">
          <MetricCard label="bridge ML MAE" value={bridgeMlMetrics.mae.toFixed(3)} accent="seismic" />
          <MetricCard label="bridge ML RMSE" value={bridgeMlMetrics.rmse.toFixed(3)} accent="signal" />
          <MetricCard label="bridge ML R²" value={bridgeMlMetrics.r2.toFixed(3)} accent="moss" />
        </div>
      ) : null}
    </SectionShell>
  )
}
