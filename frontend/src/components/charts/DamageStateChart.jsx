import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import ChartShell from './ChartShell'

const COLORS = ['#e2e8f0', '#bfdbfe', '#60a5fa', '#2563eb', '#7c3aed']

export default function DamageStateChart({ data }) {
  return (
    <ChartShell
      eyebrow="Damage framing"
      title="Modal damage-state composition"
      description="Derived from the statewide HAZUS probability table by taking the modal damage state for each bridge."
    >
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 12, right: 12, left: -8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.24)" vertical={false} />
          <XAxis dataKey="label" tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip formatter={(value) => value.toLocaleString()} contentStyle={{ borderRadius: 18, border: '1px solid rgba(226,232,240,0.95)' }} />
          <Bar dataKey="count" radius={[12, 12, 4, 4]}>
            {data.map((entry, index) => (
              <Cell key={entry.label} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartShell>
  )
}
