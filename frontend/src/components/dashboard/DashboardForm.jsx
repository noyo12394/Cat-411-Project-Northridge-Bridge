import { FlaskConical, Play, RotateCcw } from 'lucide-react'
import Button from '../common/Button'
import { bridgeClassOptions } from '../../data/sampleBridges'

const numericFields = [
  { name: 'yearBuilt', label: 'Year Built', placeholder: 'e.g. 1972', help: 'Older bridges generally carry a higher intrinsic vulnerability score.' },
  { name: 'yearReconstructed', label: 'Year Reconstructed', placeholder: 'e.g. 2003', help: 'Rehabilitation reduces the score modestly rather than dominating it.' },
  { name: 'skewAngle', label: 'Skew Angle (degrees)', placeholder: 'e.g. 24', help: 'Higher skew can increase unseating and demand irregularity.' },
  { name: 'numberOfSpans', label: 'Number of Spans', placeholder: 'e.g. 4', help: 'Additional spans can increase complexity and vulnerability.' },
  { name: 'maximumSpanLength', label: 'Maximum Span Length (ft)', placeholder: 'e.g. 145', help: 'Longer spans are treated as a modest vulnerability amplifier.' },
  { name: 'conditionRating', label: 'Structural Condition Rating', placeholder: '0-9', help: 'Lower ratings increase the vulnerability estimate most strongly.' },
  { name: 'sviScore', label: 'SVI Score', placeholder: '0.00 - 1.00', help: 'Compact engineering vulnerability descriptor from the project methodology.' },
  { name: 'ndviChange', label: 'Optional NDVI Change', placeholder: 'e.g. -0.08', help: 'Optional post-event adjustment only. Negative values raise the score slightly.' },
  { name: 'trafficImportance', label: 'Traffic Importance / ADT', placeholder: 'e.g. 38000', help: 'Used only in consequence and inspection priority logic.' },
]

export default function DashboardForm({
  values,
  onFieldChange,
  onPredict,
  onReset,
  onLoadSample,
  activeSampleName,
}) {
  return (
    <div className="surface-card p-6 lg:p-7">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="eyebrow">Input panel</p>
          <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">
            Bridge-level query
          </h3>
          <p className="mt-2 max-w-xl text-sm leading-7 text-muted">
            Enter bridge attributes that logically belong in a vulnerability model. The interface intentionally excludes PGA from
            the core input layer so the score reflects intrinsic structural risk rather than event demand.
          </p>
        </div>
        <div className="rounded-2xl border border-ocean/10 bg-ocean/5 px-4 py-3 text-sm text-ocean">
          <span className="font-semibold">Current sample:</span> {activeSampleName}
        </div>
      </div>

      <div className="mt-8 grid gap-5 md:grid-cols-2">
        {numericFields.slice(0, 6).map((field) => (
          <label key={field.name}>
            <span className="field-label">{field.label}</span>
            <input
              type="number"
              step="any"
              name={field.name}
              value={values[field.name]}
              onChange={onFieldChange}
              className="field-input"
              placeholder={field.placeholder}
            />
            <span className="field-help">{field.help}</span>
          </label>
        ))}

        <label>
          <span className="field-label">Bridge Class / HWB Class</span>
          <select name="bridgeClass" value={values.bridgeClass} onChange={onFieldChange} className="field-input">
            {bridgeClassOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <span className="field-help">Class is retained as a structural descriptor, not a replacement for the full model.</span>
        </label>

        {numericFields.slice(6).map((field) => (
          <label key={field.name}>
            <span className="field-label">{field.label}</span>
            <input
              type="number"
              step="any"
              name={field.name}
              value={values[field.name]}
              onChange={onFieldChange}
              className="field-input"
              placeholder={field.placeholder}
            />
            <span className="field-help">{field.help}</span>
          </label>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Button onClick={onPredict} icon={<Play className="h-4 w-4" />}>
          Run Prediction
        </Button>
        <Button onClick={onReset} variant="secondary" icon={<RotateCcw className="h-4 w-4" />}>
          Reset Fields
        </Button>
        <Button onClick={onLoadSample} variant="subtle" icon={<FlaskConical className="h-4 w-4" />}>
          Load Sample Bridge
        </Button>
      </div>
    </div>
  )
}
