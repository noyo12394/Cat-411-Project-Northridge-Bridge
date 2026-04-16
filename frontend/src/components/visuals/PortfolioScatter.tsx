import { useId } from 'react'

interface ScatterPoint {
  structureNumber: string
  latitude: number | null
  longitude: number | null
  value: number
  label: string
}

interface PortfolioScatterProps {
  points: ScatterPoint[]
  highlightedStructure?: string
  hue?: 'seismic' | 'hazard' | 'moss'
}

const hueMap = {
  seismic: ['#7dd3fc', '#49b6ff'],
  hazard: ['#ffd166', '#f97373'],
  moss: ['#66d1a6', '#49b6ff'],
}

export function PortfolioScatter({
  points,
  highlightedStructure,
  hue = 'seismic',
}: PortfolioScatterProps) {
  const gradientId = useId()
  const valid = points.filter(
    (point) => point.latitude != null && point.longitude != null && Number.isFinite(point.value),
  )

  if (!valid.length) {
    return (
      <div className="flex h-[320px] items-center justify-center rounded-[1.6rem] border border-dashed border-line bg-white/5 text-sm text-muted">
        Spatial bridge coordinates are unavailable for this view.
      </div>
    )
  }

  const latitudes = valid.map((point) => point.latitude as number)
  const longitudes = valid.map((point) => point.longitude as number)
  const minLat = Math.min(...latitudes)
  const maxLat = Math.max(...latitudes)
  const minLng = Math.min(...longitudes)
  const maxLng = Math.max(...longitudes)
  const maxValue = Math.max(...valid.map((point) => point.value), 0.001)
  const [start, end] = hueMap[hue]

  return (
    <div className="overflow-hidden rounded-[1.6rem] border border-line bg-[radial-gradient(circle_at_center,rgba(73,182,255,0.08),transparent_48%),linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))]">
      <svg viewBox="0 0 720 320" className="h-[320px] w-full">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={start} />
            <stop offset="100%" stopColor={end} />
          </linearGradient>
        </defs>
        <rect x="0" y="0" width="720" height="320" fill="rgba(8,14,24,0.82)" />
        {Array.from({ length: 8 }).map((_, index) => (
          <line
            key={`v-${index}`}
            x1={60 + index * 80}
            y1="28"
            x2={60 + index * 80}
            y2="292"
            stroke="rgba(132, 157, 186, 0.09)"
          />
        ))}
        {Array.from({ length: 5 }).map((_, index) => (
          <line
            key={`h-${index}`}
            x1="60"
            y1={44 + index * 56}
            x2="660"
            y2={44 + index * 56}
            stroke="rgba(132, 157, 186, 0.09)"
          />
        ))}
        <path
          d="M126 260 C168 218, 210 208, 248 202 C284 196, 304 172, 346 164 C392 154, 440 162, 490 144 C542 126, 592 108, 618 98"
          fill="none"
          stroke="rgba(125, 211, 252, 0.18)"
          strokeWidth="28"
          strokeLinecap="round"
        />
        <path
          d="M126 260 C168 218, 210 208, 248 202 C284 196, 304 172, 346 164 C392 154, 440 162, 490 144 C542 126, 592 108, 618 98"
          fill="none"
          stroke="rgba(125, 211, 252, 0.35)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeDasharray="4 6"
        />
        {valid.map((point) => {
          const x = 84 + (((point.longitude as number) - minLng) / Math.max(0.0001, maxLng - minLng)) * 560
          const y = 268 - (((point.latitude as number) - minLat) / Math.max(0.0001, maxLat - minLat)) * 182
          const radius = 1.5 + (point.value / maxValue) * 5.4
          const highlighted = point.structureNumber === highlightedStructure

          return (
            <g key={point.structureNumber}>
              <circle
                cx={x}
                cy={y}
                r={highlighted ? radius + 4 : radius}
                fill={highlighted ? 'rgba(255,255,255,0.16)' : 'transparent'}
              />
              <circle
                cx={x}
                cy={y}
                r={radius}
                fill={`url(#${gradientId})`}
                opacity={highlighted ? 1 : 0.76}
              />
            </g>
          )
        })}
      </svg>
    </div>
  )
}
