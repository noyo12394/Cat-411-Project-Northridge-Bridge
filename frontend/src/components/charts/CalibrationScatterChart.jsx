import { CartesianGrid, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from 'recharts'
import ChartShell from './ChartShell'

export default function CalibrationScatterChart({ data, metrics }) {
  return (
    <ChartShell
      eyebrow="Calibration artifact"
      title="Actual vs predicted bridge ML artifact"
      description="These points come from the repo's non-degenerate bridge-level prediction artifact. They provide a calibration-style research visual even when the newest exported regression metrics are unreliable."
      aside={
        <div className="rounded-2xl border border-slate-200/80 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
          <div>Rows: {metrics.rows?.toLocaleString?.() ?? metrics.rows}</div>
          <div>Model: {metrics.modelLabel}</div>
          <div>RMSE: {metrics.rmse?.toFixed?.(3) ?? metrics.rmse}</div>
        </div>
      }
    >
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 12, right: 20, bottom: 12, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.24)" />
          <XAxis type="number" dataKey="Actual_EDR" name="Actual EDR" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis type="number" dataKey="Predicted_EDR" name="Predicted EDR" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip cursor={{ strokeDasharray: '4 4' }} contentStyle={{ borderRadius: 18, border: '1px solid rgba(226,232,240,0.95)' }} />
          <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 0.18, y: 0.18 }]} stroke="#334155" strokeDasharray="6 6" />
          <Scatter data={data} fill="#2563eb" fillOpacity={0.78} />
        </ScatterChart>
      </ResponsiveContainer>
    </ChartShell>
  )
}
