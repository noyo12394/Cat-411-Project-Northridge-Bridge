import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import ChartShell from './ChartShell'

const COLORS = ['#dbeafe', '#93c5fd', '#60a5fa', '#2563eb', '#6d28d9']

export function VulnerabilityDistributionChart({ data }) {
  return (
    <ChartShell
      eyebrow="Statewide portfolio"
      title="Intrinsic screening distribution"
      description="This distribution is drawn from the repo-derived statewide SVI portfolio rather than a hazard-inclusive damage score."
    >
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 12, right: 10, left: -8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.22)" vertical={false} />
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

export function RiskDistributionDonut({ data }) {
  return (
    <ChartShell
      eyebrow="Risk bands"
      title="Bridge risk composition"
      description="The site keeps this as an intrinsic vulnerability portfolio view. PGA enters later in the event scenario mode, not here."
    >
      <ResponsiveContainer>
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="label" innerRadius={72} outerRadius={112} paddingAngle={3}>
            {data.map((entry, index) => (
              <Cell key={entry.label} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => value.toLocaleString()} contentStyle={{ borderRadius: 18, border: '1px solid rgba(226,232,240,0.95)' }} />
        </PieChart>
      </ResponsiveContainer>
    </ChartShell>
  )
}
