import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import SurfaceCard from '../common/SurfaceCard'

export default function FeatureImportanceChart({ data }) {
  return (
    <SurfaceCard className="p-6">
      <p className="eyebrow">Chart 01</p>
      <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">Feature importance</h3>
      <p className="mt-2 text-sm leading-7 text-muted">Illustrative importance values for the intrinsic vulnerability engine.</p>
      <div className="mt-6 h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 10, right: 10, bottom: 0, left: 40 }}>
            <CartesianGrid stroke="#e8eef5" strokeDasharray="3 3" />
            <XAxis type="number" tickFormatter={(value) => `${Math.round(value * 100)}%`} stroke="#72839a" />
            <YAxis type="category" dataKey="feature" width={120} stroke="#72839a" />
            <Tooltip formatter={(value) => [`${Math.round(value * 100)}%`, 'Importance']} />
            <Bar dataKey="importance" radius={[10, 10, 10, 10]} fill="#1f5fbf" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </SurfaceCard>
  )
}
