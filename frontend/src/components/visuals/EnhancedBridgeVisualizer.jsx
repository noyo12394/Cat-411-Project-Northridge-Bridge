import { useMemo } from 'react'

const CRACK_TEMPLATES = [
  { x: 160, y: 200, segs: [[5, -3], [4, 5], [3, -2], [5, 4]] },
  { x: 300, y: 198, segs: [[6, 4], [5, -3], [4, 5], [3, -2]] },
  { x: 420, y: 202, segs: [[5, 3], [4, -5], [6, 3], [4, -2]] },
  { x: 230, y: 205, segs: [[4, -3], [5, 4], [3, -2]] },
  { x: 480, y: 200, segs: [[5, -4], [4, 5], [3, -3]] },
  { x: 360, y: 196, segs: [[6, 3], [5, -4], [4, 3], [5, -3]] },
  { x: 148, y: 130, segs: [[3, 8], [4, -3], [2, 6]] },
  { x: 514, y: 125, segs: [[3, 8], [4, -4], [3, 5]] },
  { x: 200, y: 220, segs: [[8, 3], [6, -4], [5, 3]] },
  { x: 450, y: 219, segs: [[7, 4], [6, -3], [5, 2]] },
  { x: 330, y: 221, segs: [[6, 2], [5, -3], [7, 3]] },
  { x: 260, y: 213, segs: [[9, 4], [7, -3], [6, 4]] },
  { x: 390, y: 211, segs: [[8, -3], [6, 4], [5, -2]] },
]

const DEBRIS_PARTICLES = [
  { x: 200, dy: 20, rx: 3, ry: 2, delay: 0 },
  { x: 240, dy: 35, rx: 4, ry: 3, delay: 0.1 },
  { x: 300, dy: 45, rx: 5, ry: 3, delay: 0.2 },
  { x: 340, dy: 30, rx: 3, ry: 2, delay: 0.15 },
  { x: 380, dy: 40, rx: 4, ry: 3, delay: 0.25 },
  { x: 420, dy: 25, rx: 3, ry: 2, delay: 0.05 },
  { x: 460, dy: 38, rx: 4, ry: 3, delay: 0.18 },
]

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
  let cx = tmpl.x, cy = tmpl.y
  for (const [dx, dy] of tmpl.segs) {
    cx += dx; cy += dy
    d += ` L${cx} ${cy}`
  }
  return d
}

const STATUS_LEVELS = [
  { min: 0, max: 30, label: 'Intact', sub: 'Full structural capacity retained', color: '#66d1a6', bg: 'rgba(102,209,166,0.12)' },
  { min: 30, max: 50, label: 'Slight damage', sub: 'Hairline cracks · cosmetic only', color: '#ffd166', bg: 'rgba(255,209,102,0.12)' },
  { min: 50, max: 70, label: 'Moderate damage', sub: 'Visible cracking · inspection needed', color: '#ff9c69', bg: 'rgba(255,156,105,0.12)' },
  { min: 70, max: 85, label: 'Extensive damage', sub: 'Partial deformation · restricted load', color: '#f97373', bg: 'rgba(249,115,115,0.14)' },
  { min: 85, max: 101, label: 'Collapse risk', sub: 'Structural failure imminent', color: '#dc2626', bg: 'rgba(220,38,38,0.18)' },
]

function getStatus(v) {
  return STATUS_LEVELS.find((l) => v >= l.min && v < l.max) ?? STATUS_LEVELS[4]
}

export default function EnhancedBridgeVisualizer({
  vulnerability = 20,
  svi,
  edr,
  damageProbs,
  pga,
  showMetrics = true,
  showDamageBreakdown = true,
}) {
  const effectiveVulnerability = useMemo(() => {
    const base = Math.max(0, Math.min(100, vulnerability))
    const moderateDamage = damageProbs?.DS2 ?? 0
    const severeDamage = (damageProbs?.DS3 ?? 0) + (damageProbs?.DS4 ?? 0)
    const edrNormalized = Math.min(1, Math.max(0, (edr ?? 0) / 0.45))
    const eventDemand = Math.min(1, Math.max(0, (pga ?? 0) / 0.8))
    const eventStress = Math.min(
      1,
      severeDamage * 1.15 + moderateDamage * 0.45 + edrNormalized * 0.65 + eventDemand * 0.25,
    )

    return Math.round(Math.min(100, base * 0.65 + eventStress * 45))
  }, [damageProbs, edr, pga, vulnerability])

  const t = effectiveVulnerability / 100
  const status = getStatus(effectiveVulnerability)

  const {
    structColor, cableColor, pierColor, skyColor, waterColor, rustOpacity,
    cableSag, deckSag, deckTilt, centerDrop, leftTowerTilt, rightTowerTilt,
    cableSnapLeft, cableSnapRight, numCracks, showDebris, showCollapse,
    deckFragmented,
  } = useMemo(() => {
    const structColor =
      t < 0.5 ? lerpHex('#c8a86b', '#8a7a60', t / 0.5)
              : lerpHex('#8a7a60', '#4a3020', (t - 0.5) / 0.5)
    const cableColor =
      t < 0.5 ? lerpHex('#8a7040', '#6a6050', t / 0.5)
              : lerpHex('#6a6050', '#3a2818', (t - 0.5) / 0.5)
    const pierColor = lerpHex('#b89850', '#4a3020', t)
    const skyColor =
      t < 0.5 ? lerpHex('#1a2438', '#1f2a3e', t / 0.5)
              : lerpHex('#1f2a3e', '#2a1818', (t - 0.5) / 0.5)
    const waterColor =
      t < 0.5 ? lerpHex('#1a3348', '#1e3648', t / 0.5)
              : lerpHex('#1e3648', '#2a2028', (t - 0.5) / 0.5)

    const rustOpacity = Math.max(0, ((t - 0.35) / 0.65) * 0.6)
    const cableSag = 155 + t * 40
    const deckSag = t > 0.6 ? (t - 0.6) * 50 : 0
    const deckTilt = t > 0.75 ? (t - 0.75) * 12 : 0
    const centerDrop = t > 0.8 ? (t - 0.8) * 80 : 0
    const leftTowerTilt = t > 0.85 ? (t - 0.85) * 8 : 0
    const rightTowerTilt = t > 0.9 ? (t - 0.9) * -10 : 0
    const cableSnapLeft = t > 0.82
    const cableSnapRight = t > 0.88
    const numCracks = Math.floor(t * CRACK_TEMPLATES.length)
    const showDebris = t > 0.75
    const showCollapse = t > 0.85
    const deckFragmented = t > 0.8

    return {
      structColor, cableColor, pierColor, skyColor, waterColor, rustOpacity,
      cableSag, deckSag, deckTilt, centerDrop, leftTowerTilt, rightTowerTilt,
      cableSnapLeft, cableSnapRight, numCracks, showDebris, showCollapse,
      deckFragmented,
    }
  }, [t])

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-2xl border border-line bg-canvas">
        <svg
          width="100%"
          viewBox="0 0 680 340"
          aria-label={`Bridge at ${effectiveVulnerability}% vulnerability: ${status.label}`}
          role="img"
        >
          <defs>
            <clipPath id="bridge-clip-enhanced">
              <rect x="40" y="30" width="600" height="310" />
            </clipPath>
            <linearGradient id="water-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={waterColor} stopOpacity="0.9" />
              <stop offset="100%" stopColor={waterColor} stopOpacity="1" />
            </linearGradient>
          </defs>

          <rect x="40" y="30" width="600" height="195" fill={skyColor} />
          <rect x="40" y="225" width="600" height="115" fill="url(#water-grad)" />

          <g opacity="0.35">
            <line x1="60" y1="245" x2="220" y2="245" stroke="#4a6278" strokeWidth="1.5" />
            <line x1="260" y1="255" x2="420" y2="255" stroke="#4a6278" strokeWidth="1.5" />
            <line x1="460" y1="248" x2="620" y2="248" stroke="#4a6278" strokeWidth="1.5" />
            <line x1="80" y1="275" x2="330" y2="275" stroke="#4a6278" strokeWidth="1" />
            <line x1="390" y1="280" x2="620" y2="280" stroke="#4a6278" strokeWidth="1" />
          </g>

          <rect x="140" y="220" width="30" height="120" rx="2" fill={pierColor} />
          <rect x="510" y="220" width="30" height="120" rx="2" fill={pierColor} />

          <g style={{ transform: `rotate(${leftTowerTilt}deg)`, transformOrigin: '155px 220px', transition: 'transform 0.4s ease-out' }}>
            <rect x="140" y="70" width="30" height="150" rx="2" fill={structColor} />
            <rect x="132" y="100" width="46" height="10" rx="1" fill={structColor} />
            <rect x="146" y="62" width="18" height="12" rx="2" fill={lerpHex('#d4b06a', '#5a4030', t)} />
          </g>

          <g style={{ transform: `rotate(${rightTowerTilt}deg)`, transformOrigin: '525px 220px', transition: 'transform 0.4s ease-out' }}>
            <rect x="510" y="70" width="30" height="150" rx="2" fill={structColor} />
            <rect x="502" y="100" width="46" height="10" rx="1" fill={structColor} />
            <rect x="516" y="62" width="18" height="12" rx="2" fill={lerpHex('#d4b06a', '#5a4030', t)} />
          </g>

          {!cableSnapLeft && (
            <path
              d={`M155 68 Q220 ${cableSag} 340 ${205 + deckSag}`}
              fill="none" stroke={cableColor} strokeWidth="3"
              style={{ transition: 'all 0.4s ease-out' }}
            />
          )}
          {cableSnapLeft && (
            <>
              <path d={`M155 68 Q200 ${cableSag - 10} 240 ${cableSag + 20}`}
                fill="none" stroke={cableColor} strokeWidth="3" />
              <path d={`M340 ${205 + deckSag} Q290 ${215 + deckSag} 260 ${240 + deckSag}`}
                fill="none" stroke={cableColor} strokeWidth="2" opacity="0.7" />
            </>
          )}

          {!cableSnapRight && (
            <path
              d={`M525 68 Q460 ${cableSag} 340 ${205 + deckSag}`}
              fill="none" stroke={cableColor} strokeWidth="3"
              style={{ transition: 'all 0.4s ease-out' }}
            />
          )}
          {cableSnapRight && (
            <>
              <path d={`M525 68 Q490 ${cableSag - 10} 445 ${cableSag + 25}`}
                fill="none" stroke={cableColor} strokeWidth="3" />
              <path d={`M340 ${205 + deckSag} Q390 ${218 + deckSag} 420 ${245 + deckSag}`}
                fill="none" stroke={cableColor} strokeWidth="2" opacity="0.7" />
            </>
          )}

          <g stroke={cableColor} strokeWidth="1.5" style={{ transition: 'opacity 0.3s' }} opacity={cableSnapLeft ? 0.3 : 1}>
            <line x1="185" y1="115" x2="185" y2={205 + deckSag * 0.5} />
            <line x1="220" y1="138" x2="220" y2={205 + deckSag * 0.7} />
            <line x1="255" y1="160" x2="255" y2={205 + deckSag * 0.9} />
            <line x1="290" y1="180" x2="290" y2={205 + deckSag} />
          </g>
          <g stroke={cableColor} strokeWidth="1.5" style={{ transition: 'opacity 0.3s' }} opacity={cableSnapRight ? 0.3 : 1}>
            <line x1="495" y1="115" x2="495" y2={205 + deckSag * 0.5} />
            <line x1="460" y1="138" x2="460" y2={205 + deckSag * 0.7} />
            <line x1="425" y1="160" x2="425" y2={205 + deckSag * 0.9} />
            <line x1="390" y1="180" x2="390" y2={205 + deckSag} />
          </g>

          {!deckFragmented && (
            <g style={{ transform: `translateY(${deckSag}px) rotate(${deckTilt * 0.3}deg)`, transformOrigin: '340px 205px', transition: 'all 0.4s ease-out' }}>
              <rect x="80" y="200" width="520" height="22" rx="2" fill={structColor} />
              <rect x="80" y="222" width="520" height="12" rx="1" fill={lerpHex('#b8985a', '#3a2418', t)} />
              <rect x="80" y="200" width="520" height="22" rx="2" fill="#8B4513" opacity={rustOpacity} />
            </g>
          )}

          {deckFragmented && (
            <>
              <g style={{ transform: `translate(0, ${deckSag * 0.3}px) rotate(${-deckTilt * 0.5}deg)`, transformOrigin: '170px 205px', transition: 'all 0.4s ease-out' }}>
                <rect x="80" y="200" width="180" height="22" rx="2" fill={structColor} />
                <rect x="80" y="222" width="180" height="12" rx="1" fill={lerpHex('#b8985a', '#3a2418', t)} />
                <rect x="80" y="200" width="180" height="22" rx="2" fill="#8B4513" opacity={rustOpacity} />
              </g>

              <g style={{ transform: `translate(0, ${centerDrop}px) rotate(${deckTilt * 1.2}deg)`, transformOrigin: '340px 210px', transition: 'all 0.4s ease-out' }}>
                <rect x="260" y="200" width="160" height="22" rx="2" fill={lerpHex(structColor, '#2a1810', 0.4)} />
                <rect x="260" y="222" width="160" height="12" rx="1" fill="#2a1810" />
                <rect x="260" y="200" width="160" height="22" rx="2" fill="#6B2613" opacity={Math.min(0.8, rustOpacity + 0.3)} />
                {showCollapse && (
                  <g stroke="#1a0a00" strokeWidth="1.5" fill="none" opacity="0.9">
                    <path d="M290 200 L295 222" />
                    <path d="M330 200 L335 222" />
                    <path d="M370 200 L375 222" />
                    <path d="M260 210 L420 210" strokeDasharray="3 2" />
                  </g>
                )}
              </g>

              <g style={{ transform: `translate(0, ${deckSag * 0.3}px) rotate(${deckTilt * 0.5}deg)`, transformOrigin: '510px 205px', transition: 'all 0.4s ease-out' }}>
                <rect x="420" y="200" width="180" height="22" rx="2" fill={structColor} />
                <rect x="420" y="222" width="180" height="12" rx="1" fill={lerpHex('#b8985a', '#3a2418', t)} />
                <rect x="420" y="200" width="180" height="22" rx="2" fill="#8B4513" opacity={rustOpacity} />
              </g>
            </>
          )}

          <g clipPath="url(#bridge-clip-enhanced)">
            {CRACK_TEMPLATES.slice(0, numCracks).map((tmpl, i) => {
              const crackOpacity = Math.min(1, (t * CRACK_TEMPLATES.length - i) * 1.5)
              const crackW = t > 0.7 ? 2 : 1
              const crackColor = t > 0.6 ? '#0a0500' : '#3a2a10'
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
                      fill="#000"
                      opacity={((t - 0.7) / 0.3 * 0.8).toFixed(2)}
                    />
                  )}
                </g>
              )
            })}
          </g>

          {showDebris && (
            <g>
              {DEBRIS_PARTICLES.map((p, i) => {
                const fallT = Math.min(1, (t - 0.75) / 0.25)
                const fallY = 225 + fallT * p.dy * 2
                return (
                  <ellipse
                    key={i}
                    cx={p.x + (fallT * 3)}
                    cy={fallY}
                    rx={p.rx * (0.5 + fallT * 0.5)}
                    ry={p.ry * (0.5 + fallT * 0.5)}
                    fill="#2a1810"
                    opacity={fallT * 0.8}
                    style={{ transition: 'all 0.5s ease-in' }}
                  />
                )
              })}
            </g>
          )}

          {showCollapse && (
            <g opacity={Math.min(0.6, (t - 0.85) * 3)}>
              <path d="M280 230 Q300 215 320 230 Q340 215 360 230 Q380 215 400 230"
                stroke="#0a0a0a" strokeWidth="1" fill="none" opacity="0.4" />
              <ellipse cx="340" cy={245 + centerDrop * 0.3} rx="50" ry="4" fill="#0a0a0a" opacity="0.3" />
            </g>
          )}
        </svg>
      </div>

      {showDamageBreakdown ? (
        <div className="grid grid-cols-4 gap-2">
          {damageProbs ? (
            <>
              <div className="rounded-xl border border-line bg-canvas/60 p-2.5 text-center">
                <div className="font-mono text-[9px] uppercase tracking-wider text-muted">DS0 none</div>
                <div className="mt-0.5 font-mono text-xs font-semibold text-moss">{(damageProbs.DS0 * 100).toFixed(1)}%</div>
              </div>
              <div className="rounded-xl border border-line bg-canvas/60 p-2.5 text-center">
                <div className="font-mono text-[9px] uppercase tracking-wider text-muted">DS1 slight</div>
                <div className="mt-0.5 font-mono text-xs font-semibold text-signal">{(damageProbs.DS1 * 100).toFixed(1)}%</div>
              </div>
              <div className="rounded-xl border border-line bg-canvas/60 p-2.5 text-center">
                <div className="font-mono text-[9px] uppercase tracking-wider text-muted">DS2 mod</div>
                <div className="mt-0.5 font-mono text-xs font-semibold text-ember">{(damageProbs.DS2 * 100).toFixed(1)}%</div>
              </div>
              <div className="rounded-xl border border-line bg-canvas/60 p-2.5 text-center">
                <div className="font-mono text-[9px] uppercase tracking-wider text-muted">DS3+DS4</div>
                <div className="mt-0.5 font-mono text-xs font-semibold text-hazard">{((damageProbs.DS3 + damageProbs.DS4) * 100).toFixed(1)}%</div>
              </div>
            </>
          ) : null}
        </div>
      ) : null}

      {showMetrics ? (
        <div className="grid grid-cols-3 gap-2">
          <div className="rounded-xl border border-line bg-canvas/60 p-2.5 text-center">
            <div className="font-mono text-[9px] uppercase tracking-wider text-muted">SVI</div>
            <div className="mt-0.5 font-mono text-xs font-semibold text-ocean">
              {typeof svi === 'number' ? svi.toFixed(3) : 'n/a'}
            </div>
          </div>
          <div className="rounded-xl border border-line bg-canvas/60 p-2.5 text-center">
            <div className="font-mono text-[9px] uppercase tracking-wider text-muted">EDR</div>
            <div className="mt-0.5 font-mono text-xs font-semibold text-ember">
              {typeof edr === 'number' ? edr.toFixed(4) : 'n/a'}
            </div>
          </div>
          <div className="rounded-xl border border-line bg-canvas/60 p-2.5 text-center">
            <div className="font-mono text-[9px] uppercase tracking-wider text-muted">PGA (g)</div>
            <div className="mt-0.5 font-mono text-xs font-semibold text-signal">
              {typeof pga === 'number' ? pga.toFixed(2) : 'n/a'}
            </div>
          </div>
        </div>
      ) : null}

      <div
        className="rounded-2xl border p-3 text-center transition-all duration-300"
        style={{ background: status.bg, borderColor: `${status.color}44` }}
      >
        <p className="font-display text-base font-semibold" style={{ color: status.color }}>
          {status.label}
        </p>
        <p className="mt-0.5 text-xs text-muted">{status.sub}</p>
      </div>
    </div>
  )
}
