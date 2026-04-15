import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import SurfaceCard from '../common/SurfaceCard'

export default function RiskDistributionChart({ data }) {
  return (
    <SurfaceCard className="p-6">
      <p className="eyebrow">Chart 03</p>
      <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">Risk level distribution</h3>
      <p className="mt-2 text-sm leading-7 text-muted">A portfolio view of bridges grouped into low, medium, high, and critical tiers.</p>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_0.8fr] lg:items-center">
        <div className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="value" innerRadius={68} outerRadius={108} paddingAngle={3} stroke="none">
                {data.map((entry) => (
                  <Cell key={entry.name} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [value.toLocaleString(), 'Bridges']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="space-y-4">
          {data.map((item) => (
            <div key={item.name} className="flex items-center justify-between rounded-[22px] border border-slate-100 bg-slate-50 px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.fill }} />
                <span className="font-medium text-ink">{item.name}</span>
              </div>
              <span className="text-sm text-muted">{item.value.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>
    </SurfaceCard>
  )
}
