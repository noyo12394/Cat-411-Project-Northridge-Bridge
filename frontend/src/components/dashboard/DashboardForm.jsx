const bridgeClasses = ['HWB1', 'HWB2', 'HWB3', 'HWB4', 'HWB5', 'HWB6', 'HWB7', 'HWB8', 'HWB9', 'HWB10', 'HWB11', 'HWB12']

function Field({ label, help, children }) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-semibold text-slate-900">{label}</span>
      {children}
      {help ? <span className="block text-xs leading-5 text-slate-500">{help}</span> : null}
    </label>
  )
}

export default function DashboardForm({ inputs, mode, onChange, onLoadSample, onReset, sampleBridges, onRun }) {
  return (
    <div className="rounded-[30px] border border-white/80 bg-white/92 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Input panel</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">Bridge-level query</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {sampleBridges?.map((sample) => (
            <button
              key={sample.label}
              type="button"
              onClick={() => onLoadSample(sample)}
              className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-600 transition hover:border-slate-300 hover:bg-white"
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      <form className="mt-6 grid gap-5 md:grid-cols-2" onSubmit={onRun}>
        <Field label="Year Built" help="Older bridges tend to reflect earlier detailing eras and different baseline fragility families.">
          <input className="field-input" type="number" value={inputs.yearBuilt} onChange={(event) => onChange('yearBuilt', event.target.value)} />
        </Field>
        <Field label="Year Reconstructed" help="Leave blank if no known rehabilitation / reconstruction year is available.">
          <input className="field-input" type="number" value={inputs.yearReconstructed} onChange={(event) => onChange('yearReconstructed', event.target.value)} />
        </Field>
        <Field label="Skew Angle (degrees)" help="Higher skew amplifies irregular support response under seismic loading.">
          <input className="field-input" type="number" value={inputs.skew} onChange={(event) => onChange('skew', event.target.value)} />
        </Field>
        <Field label="Number of Spans" help="Used as a geometry complexity indicator in the intrinsic model.">
          <input className="field-input" type="number" value={inputs.spans} onChange={(event) => onChange('spans', event.target.value)} />
        </Field>
        <Field label="Maximum Span Length (ft)" help="Longer spans increase demand and structural consequence of poor detailing.">
          <input className="field-input" type="number" step="0.1" value={inputs.maxSpan} onChange={(event) => onChange('maxSpan', event.target.value)} />
        </Field>
        <Field label="Structural Condition Rating" help="Represents the structural condition proxy used in the screening layer. 0 = poor, 9 = excellent.">
          <input className="field-input" type="number" min="0" max="9" value={inputs.condition} onChange={(event) => onChange('condition', event.target.value)} />
        </Field>
        <Field label="Bridge Class / HWB Class" help="HAZUS bridge class remains a structural family descriptor even when PGA is excluded from baseline screening.">
          <select className="field-input" value={inputs.bridgeClass} onChange={(event) => onChange('bridgeClass', event.target.value)}>
            {bridgeClasses.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </Field>
        <Field label="SVI Score" help="You can type the SVI directly to reflect the repo's weighted intrinsic screening output.">
          <input className="field-input" type="number" min="0" max="1" step="0.001" value={inputs.svi} onChange={(event) => onChange('svi', event.target.value)} />
        </Field>
        <Field label="Optional NDVI Change" help="Used only as a post-event attention adjustment. Negative values indicate possible degradation.">
          <input className="field-input" type="number" step="0.01" value={inputs.ndviChange} onChange={(event) => onChange('ndviChange', event.target.value)} />
        </Field>
        <Field label="Traffic Importance / ADT" help="Traffic belongs in prioritization and disruption logic, not the intrinsic vulnerability score.">
          <input className="field-input" type="number" value={inputs.adt} onChange={(event) => onChange('adt', event.target.value)} />
        </Field>
        {mode === 'event' ? (
          <Field label="Scenario PGA (g)" help="Hazard intensity is introduced only in event mode.">
            <input className="field-input" type="number" min="0" max="0.5" step="0.01" value={inputs.scenarioPga} onChange={(event) => onChange('scenarioPga', event.target.value)} />
          </Field>
        ) : null}

        <div className="md:col-span-2 flex flex-wrap gap-3 pt-2">
          <button type="submit" className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(15,23,42,0.22)] transition hover:-translate-y-0.5">
            Run Prediction
          </button>
          <button type="button" onClick={onReset} className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300">
            Reset Fields
          </button>
          <button type="button" onClick={() => onLoadSample(sampleBridges?.[1])} className="rounded-full border border-blue-200 bg-blue-50 px-5 py-3 text-sm font-semibold text-blue-700 transition hover:border-blue-300">
            Load Sample Bridge
          </button>
        </div>
      </form>
    </div>
  )
}
