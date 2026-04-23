const bridgeClasses = ['HWB1', 'HWB2', 'HWB3', 'HWB4', 'HWB5', 'HWB6', 'HWB7', 'HWB8', 'HWB9', 'HWB10', 'HWB11', 'HWB12']

function Field({ label, help, children }) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-semibold text-slate-900">{label}</span>
      {children}
      {help ? <span className="block text-xs leading-5 text-slate-600">{help}</span> : null}
    </label>
  )
}

function FieldGroup({ eyebrow, title, description, children }) {
  return (
    <div className="paper-panel-soft rounded-[26px] p-5">
      <p className="paper-eyebrow">{eyebrow}</p>
      <h4 className="mt-2 text-lg font-semibold tracking-[-0.03em] text-slate-900">{title}</h4>
      <p className="mt-2 text-sm leading-6 text-slate-700">{description}</p>
      <div className="mt-5 grid gap-5 md:grid-cols-2">{children}</div>
    </div>
  )
}

export default function DashboardForm({
  inputs,
  mode,
  onChange,
  onLoadSample,
  onReset,
  sampleBridges,
  onRun,
}) {
  const modeCopy =
    mode === 'event'
      ? 'Scenario PGA appears only in this hazard-inclusive mode.'
      : mode === 'priority'
        ? 'ADT and optional NDVI shift urgency here, not baseline structural weakness.'
        : 'This mode screens intrinsic bridge vulnerability only, without PGA.'

  return (
    <div className="paper-panel rounded-[30px] p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="max-w-2xl">
          <p className="paper-eyebrow">Input panel</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-900">
            Bridge-level query
          </h3>
          <p className="mt-3 paper-copy">{modeCopy}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {sampleBridges?.map((sample) => (
            <button
              key={sample.label}
              type="button"
              onClick={() => onLoadSample(sample)}
              className="rounded-full border border-slate-200/90 bg-slate-50/95 px-3 py-2 text-xs font-medium text-slate-700 transition hover:border-slate-300 hover:bg-white"
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      <form className="mt-6 space-y-5" onSubmit={onRun}>
        <FieldGroup
          eyebrow="Structural attributes"
          title="Core vulnerability inputs"
          description="These inputs belong in the intrinsic bridge screening layer because they describe structural age, geometry, condition, and class."
        >
          <Field
            label="Year Built"
            help="Older bridges tend to reflect earlier detailing eras and different baseline fragility families."
          >
            <input
              className="field-input"
              type="number"
              value={inputs.yearBuilt}
              onChange={(event) => onChange('yearBuilt', event.target.value)}
            />
          </Field>
          <Field
            label="Year Reconstructed"
            help="Leave blank if no known rehabilitation or reconstruction year is available."
          >
            <input
              className="field-input"
              type="number"
              value={inputs.yearReconstructed}
              onChange={(event) => onChange('yearReconstructed', event.target.value)}
            />
          </Field>
          <Field
            label="Skew Angle (degrees)"
            help="Higher skew amplifies irregular support response under seismic loading."
          >
            <input
              className="field-input"
              type="number"
              value={inputs.skew}
              onChange={(event) => onChange('skew', event.target.value)}
            />
          </Field>
          <Field
            label="Number of Spans"
            help="Used as a geometry complexity indicator in the intrinsic model."
          >
            <input
              className="field-input"
              type="number"
              value={inputs.spans}
              onChange={(event) => onChange('spans', event.target.value)}
            />
          </Field>
          <Field
            label="Maximum Span Length (ft)"
            help="Longer spans increase demand and structural consequence of poor detailing."
          >
            <input
              className="field-input"
              type="number"
              step="0.1"
              value={inputs.maxSpan}
              onChange={(event) => onChange('maxSpan', event.target.value)}
            />
          </Field>
          <Field
            label="Structural Condition Rating"
            help="Represents the structural condition proxy used in the screening layer. 0 = poor, 9 = excellent."
          >
            <input
              className="field-input"
              type="number"
              min="0"
              max="9"
              value={inputs.condition}
              onChange={(event) => onChange('condition', event.target.value)}
            />
          </Field>
          <Field
            label="Bridge Class / HWB Class"
            help="Bridge class stays as a structural family descriptor even when PGA is excluded from baseline screening."
          >
            <select
              className="field-input"
              value={inputs.bridgeClass}
              onChange={(event) => onChange('bridgeClass', event.target.value)}
            >
              {bridgeClasses.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </Field>
          <Field
            label="SVI Score"
            help="Use the SVI directly to reflect the repo's weighted intrinsic screening output."
          >
            <input
              className="field-input"
              type="number"
              min="0"
              max="1"
              step="0.001"
              value={inputs.svi}
              onChange={(event) => onChange('svi', event.target.value)}
            />
          </Field>
        </FieldGroup>

        <FieldGroup
          eyebrow="Context and consequence"
          title="Post-event and prioritization inputs"
          description="These fields are kept separate so the dashboard does not confuse structural vulnerability with hazard demand or traffic consequence."
        >
          <Field
            label="Optional NDVI Change"
            help="Used only as a post-event attention adjustment. Negative values indicate possible degradation."
          >
            <input
              className="field-input"
              type="number"
              step="0.01"
              value={inputs.ndviChange}
              onChange={(event) => onChange('ndviChange', event.target.value)}
            />
          </Field>
          <Field
            label="Traffic Importance / ADT"
            help="Traffic belongs in prioritization and disruption logic, not the intrinsic vulnerability score."
          >
            <input
              className="field-input"
              type="number"
              value={inputs.adt}
              onChange={(event) => onChange('adt', event.target.value)}
            />
          </Field>
          {mode === 'event' ? (
            <Field
              label="Scenario PGA (g)"
              help="Hazard intensity is introduced only in event mode."
            >
              <input
                className="field-input"
                type="number"
                min="0"
                max="0.5"
                step="0.01"
                value={inputs.scenarioPga}
                onChange={(event) => onChange('scenarioPga', event.target.value)}
              />
            </Field>
          ) : null}
        </FieldGroup>

        <div className="flex flex-wrap gap-3 pt-1">
          <button
            type="submit"
            className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(15,23,42,0.22)] transition hover:-translate-y-0.5 hover:bg-slate-900"
          >
            Run Prediction
          </button>
          <button
            type="button"
            onClick={onReset}
            className="rounded-full border border-slate-200/90 bg-white px-5 py-3 text-sm font-semibold text-slate-800 transition hover:border-slate-300 hover:bg-slate-50"
          >
            Reset Fields
          </button>
          <button
            type="button"
            onClick={() => onLoadSample(sampleBridges?.[1])}
            className="rounded-full border border-blue-200/90 bg-blue-50/95 px-5 py-3 text-sm font-semibold text-blue-800 transition hover:border-blue-300"
          >
            Load Sample Bridge
          </button>
        </div>
      </form>
    </div>
  )
}
