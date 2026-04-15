import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import ChartShell from './ChartShell'

export default function FutureScenarioChart({ data }) {
  return (
    <ChartShell
      eyebrow="Scenario analysis"
      title="Future earthquake stress-test summary"
      description="These curves come directly from the repo's future scenario scorer. They belong in event-damage framing, not baseline vulnerability screening."
    >
      <ResponsiveContainer>
        <AreaChart data={data} margin={{ top: 12, right: 12, left: -8, bottom: 0 }}>
          <defs>
            <linearGradient id="meanEdrFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#2563eb" stopOpacity={0.45} />
              <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="riskBandFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.03} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.24)" />
          <XAxis dataKey="scenario" tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="left" tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="right" orientation="right" tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ borderRadius: 18, border: '1px solid rgba(226,232,240,0.95)' }} />
          <Legend />
          <Area yAxisId="left" type="monotone" dataKey="meanPredictedEdr" name="Mean predicted EDR" stroke="#2563eb" fill="url(#meanEdrFill)" strokeWidth={3} />
          <Area yAxisId="right" type="monotone" dataKey="bridgesEdrGe002" name="Bridges above 0.02 EDR" stroke="#8b5cf6" fill="url(#riskBandFill)" strokeWidth={3} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartShell>
  )
}
