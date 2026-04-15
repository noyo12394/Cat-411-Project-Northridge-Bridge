import { CartesianGrid, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from 'recharts'
import SurfaceCard from '../common/SurfaceCard'

export default function ReliabilityChart({ data }) {
  return (
    <SurfaceCard className="p-6">
      <p className="eyebrow">Chart 04</p>
      <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">Model reliability view</h3>
      <p className="mt-2 text-sm leading-7 text-muted">Mock actual-vs-predicted relationship for presentation of model calibration quality.</p>
      <div className="mt-6 h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 15, bottom: 5, left: 0 }}>
            <CartesianGrid stroke="#e8eef5" strokeDasharray="3 3" />
            <XAxis type="number" dataKey="actual" name="Actual" domain={[0, 1]} stroke="#72839a" />
            <YAxis type="number" dataKey="predicted" name="Predicted" domain={[0, 1]} stroke="#72839a" />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={(value) => [Number(value).toFixed(2), 'Score']} />
            <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]} stroke="#102033" strokeDasharray="4 4" />
            <Scatter data={data} fill="#5664f5" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </SurfaceCard>
  )
}
