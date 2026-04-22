import { useCallback, useEffect, useRef, useState } from 'react'

const CRACK_TEMPLATES = [
  { x: 160, y: 200, segs: [[5, -3], [4, 5], [3, -2], [5, 4]] },
  { x: 300, y: 198, segs: [[6, 4], [5, -3], [4, 5], [3, -2]] },
  { x: 420, y: 202, segs: [[5, 3], [4, -5], [6, 3], [4, -2]] },
  { x: 230, y: 205, segs: [[4, -3], [5, 4], [3, -2]] },
  { x: 480, y: 200, segs: [[5, -4], [4, 5], [3, -3]] },
  { x: 360, y: 196, segs: [[6, 3], [5, -4], [4, 3], [5, -3]] },
  { x: 148, y: 130, segs: [[3, 8], [4, -3], [2, 6]] },
  { x: 514, y: 125, segs: [[3, 8], [4, -4], [3, 5]] },
  { x: 152, y: 160, segs: [[4, 5], [3, -3], [4, 4]] },
  { x: 518, y: 155, segs: [[4, 6], [3, -4], [4, 5]] },
  { x: 200, y: 220, segs: [[8, 3], [6, -4], [5, 3]] },
  { x: 450, y: 219, segs: [[7, 4], [6, -3], [5, 2]] },
  { x: 330, y: 221, segs: [[6, 2], [5, -3], [7, 3]] },
]

const LEVELS = [
  {
    label: 'Low Vulnerability',
    sub: 'Structure intact — minor monitoring recommended',
    badge: 'Low',
    badgeBg: '#e8f5e2',
    badgeColor: '#3B6D11',
    badgeBorder: '#3B6D1155',
  },
  {
    label: 'Moderate Vulnerability',
    sub: 'Minor deficiencies detected — schedule inspection',
    badge: 'Moderate',
    badgeBg: '#faeeda',
    badgeColor: '#854F0B',
    badgeBorder: '#854F0B55',
  },
  {
    label: 'High Vulnerability',
    sub: 'Significant deterioration — prioritize intervention',
    badge: 'High',
    badgeBg: '#fcebeb',
    badgeColor: '#A32D2D',
    badgeBorder: '#A32D2D55',
  },
  {
    label: 'Critical Vulnerability',
    sub: 'Structural failure risk — immediate action required',
    badge: 'Critical',
    badgeBg: '#F7C1C1',
    badgeColor: '#791F1F',
    badgeBorder: '#791F1F55',
  },
]

function getLevel(v) {
  if (v < 30) return LEVELS[0]
  if (v < 60) return LEVELS[1]
  if (v < 80) return LEVELS[2]
  return LEVELS[3]
}

function lerpHex(a, b, t) {
  const ah = a.replace('#', '')
  const bh = b.replace('#', '')
  const ar = [parseInt(ah.slice(0, 2), 16), parseInt(ah.slice(2, 4), 16), parseInt(ah.slice(4, 6), 16)]
  const br = [parseInt(bh.slice(0, 2), 16), parseInt(bh.slice(2, 4), 16), parseInt(bh.slice(4, 6), 16)]
  const r = ar.map((v, i) => Math.round(v + (br[i] - v) * t))
  return `rgb(${r[0]},${r[1]},${r[2]})`
}

function buildCrackPath(tmpl) {
  let d = `M${tmpl.x} ${tmpl.y}`
  let cx = tmpl.x
  let cy = tmpl.y
  for (const [dx, dy] of tmpl.segs) {
    cx += dx
    cy += dy
    d += ` L${cx} ${cy}`
  }
  return d
}

export default function BridgeVisualizer({ value = 20, onChange }) {
  const [score, setScore] = useState(value)
  const svgRef = useRef(null)

  const handleChange = useCallback(
    (e) => {
      const v = parseInt(e.target.value)
      setScore(v)
      onChange?.(v)
    },
    [onChange],
  )

  useEffect(() => {
    setScore(value)
  }, [value])

  const t = score / 100
  const lv = getLevel(score)

  const structColor =
    t < 0.5
      ? lerpHex('#c8a86b', '#8a7a60', t / 0.5)
      : lerpHex('#8a7a60', '#5a4030', (t - 0.5) / 0.5)

  const cableColor =
    t < 0.5
      ? lerpHex('#8a7040', '#6a6050', t / 0.5)
      : lerpHex('#6a6050', '#4a3828', (t - 0.5) / 0.5)

  const skyColor =
    t < 0.5
      ? lerpHex('#ddeeff', '#c8ccd8', t / 0.5)
      : lerpHex('#c8ccd8', '#a0a0a8', (t - 0.5) / 0.5)

  const waterColor =
    t < 0.5
      ? lerpHex('#b8d8f0', '#9ab0c8', t / 0.5)
      : lerpHex('#9ab0c8', '#7890a0', (t - 0.5) / 0.5)

  const pierColor = lerpHex('#b89850', '#4a3020', t)
  const rustOpacity = Math.max(0, (t - 0.4) / 0.6 * 0.55)
  const cableSag = 155 + t * 25
  const numCracks = Math.floor(t * CRACK_TEMPLATES.length)

  return (
    <div className="flex flex-col gap-6">
      {/* Slider controls */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-muted font-mono">
          <span>Low vulnerability</span>
          <span>High vulnerability</span>
        </div>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={score}
            onChange={handleChange}
            className="h-2 flex-1 cursor-pointer appearance-none rounded-full bg-line outline-none
              [&::-webkit-slider-thumb]:appearance-none
              [&::-webkit-slider-thumb]:h-5
              [&::-webkit-slider-thumb]:w-5
              [&::-webkit-slider-thumb]:rounded-full
              [&::-webkit-slider-thumb]:bg-ocean
              [&::-webkit-slider-thumb]:shadow-float
              [&::-webkit-slider-thumb]:transition-transform
              [&::-webkit-slider-thumb]:hover:scale-110"
          />
          <span
            className="min-w-[90px] rounded-full px-4 py-1 text-center text-sm font-semibold transition-all duration-300"
            style={{
              background: lv.badgeBg,
              color: lv.badgeColor,
              border: `1px solid ${lv.badgeBorder}`,
            }}
          >
            {score}% — {lv.badge}
          </span>
        </div>
      </div>

      {/* Bridge SVG */}
      <div className="overflow-hidden rounded-3xl border border-line bg-panel shadow-panel">
        <svg
          ref={svgRef}
          width="100%"
          viewBox="0 0 680 320"
          aria-label={`Bridge vulnerability at ${score}%: ${lv.label}`}
          role="img"
        >
          {/* Sky */}
          <rect x="60" y="40" width="560" height="175" rx="4" fill={skyColor} />

          {/* Water */}
          <rect x="60" y="215" width="560" height="65" fill={waterColor} />
          <g opacity="0.35">
            <line x1="80" y1="228" x2="200" y2="228" stroke="#fff" strokeWidth="1.5" />
            <line x1="240" y1="235" x2="380" y2="235" stroke="#fff" strokeWidth="1.5" />
            <line x1="420" y1="228" x2="560" y2="228" stroke="#fff" strokeWidth="1.5" />
            <line x1="100" y1="245" x2="290" y2="245" stroke="#fff" strokeWidth="1" />
            <line x1="350" y1="248" x2="580" y2="248" stroke="#fff" strokeWidth="1" />
          </g>

          {/* Piers in water */}
          <rect x="140" y="218" width="28" height="62" rx="2" fill={pierColor} />
          <rect x="512" y="218" width="28" height="62" rx="2" fill={pierColor} />

          {/* Left tower */}
          <rect x="140" y="80" width="28" height="138" rx="2" fill={structColor} />
          {/* Right tower */}
          <rect x="512" y="80" width="28" height="138" rx="2" fill={structColor} />
          {/* Tower crossbars */}
          <rect x="134" y="110" width="40" height="10" rx="1" fill={structColor} />
          <rect x="506" y="110" width="40" height="10" rx="1" fill={structColor} />
          {/* Tower finials */}
          <rect x="146" y="72" width="16" height="12" rx="2" fill={lerpHex('#d4b06a', '#5a4030', t)} />
          <rect x="518" y="72" width="16" height="12" rx="2" fill={lerpHex('#d4b06a', '#5a4030', t)} />

          {/* Suspension cables */}
          <path
            d={`M154 78 Q210 ${cableSag} 300 195`}
            fill="none"
            stroke={cableColor}
            strokeWidth="3"
          />
          <path
            d={`M526 78 Q470 ${cableSag} 380 195`}
            fill="none"
            stroke={cableColor}
            strokeWidth="3"
          />

          {/* Hanger cables left */}
          <g stroke={cableColor} strokeWidth="1.5">
            <line x1="180" y1="118" x2="180" y2="195" />
            <line x1="210" y1="140" x2="210" y2="195" />
            <line x1="240" y1="158" x2="240" y2="195" />
            <line x1="270" y1="172" x2="270" y2="195" />
          </g>
          {/* Hanger cables right */}
          <g stroke={cableColor} strokeWidth="1.5">
            <line x1="500" y1="118" x2="500" y2="195" />
            <line x1="470" y1="140" x2="470" y2="195" />
            <line x1="440" y1="158" x2="440" y2="195" />
            <line x1="410" y1="172" x2="410" y2="195" />
          </g>

          {/* Bridge deck */}
          <rect x="80" y="195" width="520" height="22" rx="2" fill={structColor} />
          {/* Understructure */}
          <rect x="80" y="217" width="520" height="14" rx="1" fill={lerpHex('#b8985a', '#4a3020', t)} />

          {/* Rust overlay */}
          <rect x="80" y="195" width="520" height="22" rx="2" fill="#8B4513" opacity={rustOpacity} />

          {/* Cracks */}
          <g clipPath="url(#bridge-clip-react)">
            {CRACK_TEMPLATES.slice(0, numCracks).map((tmpl, i) => {
              const crackOpacity = Math.min(1, (t * CRACK_TEMPLATES.length - i) * 1.5)
              const crackW = t > 0.7 ? 2 : 1
              const crackColor = t > 0.6 ? '#1a0a00' : '#3a2a10'
              return (
                <g key={i}>
                  <path
                    d={buildCrackPath(tmpl)}
                    fill="none"
                    stroke={crackColor}
                    strokeWidth={crackW}
                    strokeLinecap="round"
                    opacity={crackOpacity}
                  />
                  {t > 0.7 && i < 6 && (
                    <ellipse
                      cx={tmpl.x + tmpl.segs[0][0] / 2}
                      cy={tmpl.y + tmpl.segs[0][1] / 2}
                      rx={Math.min(3, (t - 0.7) * 10)}
                      ry="1.5"
                      fill="#0a0500"
                      opacity={((t - 0.7) / 0.3 * 0.8).toFixed(2)}
                    />
                  )}
                </g>
              )
            })}
          </g>

          <defs>
            <clipPath id="bridge-clip-react">
              <rect x="60" y="40" width="560" height="260" />
            </clipPath>
          </defs>
        </svg>
      </div>

      {/* Status label */}
      <div className="text-center">
        <p
          className="text-base font-semibold transition-all duration-300"
          style={{ color: lv.badgeColor }}
        >
          {lv.label}
        </p>
        <p className="mt-1 text-sm text-muted">{lv.sub}</p>
      </div>
    </div>
  )
}
