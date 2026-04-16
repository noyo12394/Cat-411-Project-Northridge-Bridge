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
import type { ResearchData } from '../types/research'

interface NdviSectionProps {
  data: ResearchData
  ndviChange: number | ''
  onNdviChange: (nextValue: number | '') => void
}

function figurePath(data: ResearchData, file: string) {
  return data.researchFigures.find((item) => item.file === file)?.path ?? null
}

export function NdviSection({
  data,
  ndviChange,
  onNdviChange,
}: NdviSectionProps) {
  const proxyRows = data.proxyValidation.models.map((model) => ({
    label: model.label,
    exactAccuracy: model.exactAccuracy,
    withinOneStateAccuracy: model.withinOneStateAccuracy,
    weightedKappa: model.weightedKappa,
  }))
  const confusionMatrix = figurePath(data, 'damage_state_confusion_matrices.png')

  return (
    <SectionShell
      id="ndvi"
      index="05"
      eyebrow="NDVI / ground-failure augmentation"
      title="NDVI is an optional post-event augmentation layer, not the default structural driver."
      description="This section is explicit about NDVI’s role. It can improve post-event inference and ground-failure sensitivity, but it should not be mistaken for the core bridge-intrinsic vulnerability model."
    >
      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel
          eyebrow="optional evidence"
          title="Ground-failure proxy control"
          description="Use this only when you want to inject possible post-event degradation into the shared dashboard state. It is optional by design."
        >
          <div className="rounded-[1.8rem] border border-line bg-white/5 p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted">
                  NDVI change
                </p>
                <p className="mt-2 font-display text-4xl tracking-[-0.05em] text-ink">
                  {ndviChange === '' ? 'off' : Number(ndviChange).toFixed(2)}
                </p>
              </div>
              <button type="button" className="lab-button" onClick={() => onNdviChange('')}>
                clear augmentation
              </button>
            </div>
            <input
              className="lab-range mt-6"
              type="range"
              min="-0.35"
              max="0.2"
              step="0.01"
              value={ndviChange === '' ? 0 : ndviChange}
              onChange={(event) => onNdviChange(Number(event.target.value))}
            />
            <div className="mt-3 flex justify-between font-mono text-[11px] uppercase tracking-[0.24em] text-muted">
              <span>-0.35 stress</span>
              <span>0.00 neutral</span>
              <span>0.20 recovery</span>
            </div>
          </div>
          <div className="mt-5 space-y-4 text-sm leading-7 text-muted">
            <p>
              Negative NDVI values are treated as potential degradation or ground-failure evidence and
              can intensify post-event attention.
            </p>
            <p>
              Positive values slightly relax the contextual layer, but they do not erase structural
              vulnerability.
            </p>
          </div>
        </Panel>

        <ChartFrame
          title="Proxy-validation comparison"
          description="This is where NDVI earns its place: not as the default driver, but as an augmentation layer that can outperform a univariate HAZUS-only baseline on the proxy-validation subset."
        >
          <div className="h-[320px]">
            <ResponsiveContainer>
              <BarChart data={proxyRows}>
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
                <Bar dataKey="exactAccuracy" fill="#7dd3fc" radius={[8, 8, 0, 0]} />
                <Bar dataKey="withinOneStateAccuracy" fill="#66d1a6" radius={[8, 8, 0, 0]} />
                <Bar dataKey="weightedKappa" fill="#ffd166" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartFrame>
      </div>

      <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <Panel
          eyebrow="research stance"
          title="Why the NDVI layer stays visually distinct"
          description="The site gives NDVI its own framing because the modeling discipline matters academically."
        >
          <ul className="space-y-3 text-sm leading-7 text-muted">
            <li>• NDVI is not the default vulnerability input.</li>
            <li>• NDVI is most useful after an event, when the goal is to refine or prioritize attention.</li>
            <li>• The hybrid proxy-validation results justify keeping the layer, but not promoting it to the structural core.</li>
          </ul>
        </Panel>

        {confusionMatrix ? (
          <Panel
            eyebrow="repo figure"
            title="Classifier evidence"
            description="The confusion-matrix export is surfaced directly from the repo so the augmentation story remains tied to the research artifacts."
          >
            <img
              src={confusionMatrix}
              alt="Damage-state confusion matrices"
              className="rounded-[1.6rem] border border-line bg-basin"
            />
          </Panel>
        ) : null}
      </div>
    </SectionShell>
  )
}
