import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import ChartShell from './ChartShell'

const BAR_COLORS = ['#1d4ed8', '#2563eb', '#3b82f6', '#6366f1', '#8b5cf6', '#0f766e', '#0284c7', '#7c3aed']

export default function FeatureImportanceChart({ data, source }) {
  return (
    <ChartShell
      eyebrow="Model inputs"
      title="Feature importance / contribution priors"
      description="When repo feature-importance exports are valid we show them directly. Otherwise the adapter falls back to domain-prior weights aligned with the bridge-intrinsic screening logic."
      aside={<span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 font-medium text-slate-600">Source: {source === 'repo' ? 'Repo export' : 'Adapter fallback'}</span>}
    >
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 18, bottom: 8, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.25)" horizontal={false} />
          <XAxis type="number" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis dataKey="feature" type="category" width={148} tick={{ fill: '#334155', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip formatter={(value) => Number(value).toFixed(3)} contentStyle={{ borderRadius: 18, border: '1px solid rgba(226,232,240,0.95)' }} />
          <Bar dataKey="importance" radius={[10, 10, 10, 10]}>
            {data.map((entry, index) => (
              <Cell key={entry.feature} fill={BAR_COLORS[index % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartShell>
  )
}
