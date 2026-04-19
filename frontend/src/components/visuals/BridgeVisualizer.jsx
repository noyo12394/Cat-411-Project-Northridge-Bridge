import { useCallback, useEffect, useState } from 'react'

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
  { label: 'Low Vulnerability',      sub: 'Structure intact — minor monitoring recommended',     badge: 'Low',      bg: '#e8f5e2', color: '#3B6D11', border: '#3B6D1133' },
  { label: 'Moderate Vulnerability', sub: 'Minor deficiencies detected — schedule inspection',   badge: 'Moderate', bg: '#faeeda', color: '#854F0B', border: '#854F0B33' },
  { label: 'High Vulnerability',     sub: 'Significant deterioration — prioritize intervention', badge: 'High',     bg: '#fcebeb', color: '#A32D2D', border: '#A32D2D33' },
  { label: 'Critical Vulnerability', sub: 'Structural failure risk — immediate action required', badge: 'Critical', bg: '#F7C1C1', color: '#791F1F', border: '#791F1F33' },
]

function getLevel(v) {
  if (v < 30) return LEVELS[0]
  if (v < 60) return LEVELS[1]
  if (v < 80) return LEVELS[2]
  return LEVELS[3]
}

function lerp(a, b, t) {
  const ah = a.replace('#', ''), bh = b.replace('#', '')
  const ar = [parseInt(ah.slice(0,2),16), parseInt(ah.slice(2,4),16), parseInt(ah.slice(4,6),16)]
  const br = [parseInt(bh.slice(0,2),16), parseInt(bh.slice(2,4),16), parseInt(bh.slice(4,6),16)]
  return `rgb(${ar.map((v,i) => Math.round(v+(br[i]-v)*t)).join(',')})`
}

function crackPath(tmpl) {
  let d = `M${tmpl.x} ${tmpl.y}`, cx = tmpl.x, cy = tmpl.y
  for (const [dx,dy] of tmpl.segs) { cx+=dx; cy+=dy; d+=` L${cx} ${cy}` }
  return d
}

export default function BridgeVisualizer({ value = 20, onChange }) {
  const [score, setScore] = useState(value)
  useEffect(() => { setScore(value) }, [value])

  const handleChange = useCallback((e) => {
    const v = parseInt(e.target.value)
    setScore(v)
    onChange?.(v)
  }, [onChange])

  const t = score / 100
  const lv = getLevel(score)
  const structColor = t < 0.5 ? lerp('#c8a86b','#8a7a60',t/0.5) : lerp('#8a7a60','#5a4030',(t-0.5)/0.5)
  const cableColor  = t < 0.5 ? lerp('#8a7040','#6a6050',t/0.5) : lerp('#6a6050','#4a3828',(t-0.5)/0.5)
  const skyColor    = t < 0.5 ? lerp('#ddeeff','#c8ccd8',t/0.5) : lerp('#c8ccd8','#a0a0a8',(t-0.5)/0.5)
  const waterColor  = t < 0.5 ? lerp('#b8d8f0','#9ab0c8',t/0.5) : lerp('#9ab0c8','#7890a0',(t-0.5)/0.5)
  const pierColor   = lerp('#b89850','#4a3020',t)
  const finialColor = lerp('#d4b06a','#5a4030',t)
  const rustOpacity = Math.max(0,(t-0.4)/0.6*0.55)
  const cableSag    = 155 + t * 25
  const numCracks   = Math.floor(t * CRACK_TEMPLATES.length)

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-2">
        <div className="flex justify-between font-mono text-xs text-muted">
          <span>Low vulnerability</span>
          <span>High vulnerability</span>
        </div>
        <div className="flex items-center gap-4">
          <input
            type="range" min="0" max="100" step="1" value={score}
            onChange={handleChange}
            className="h-2 flex-1 cursor-pointer appearance-none rounded-full bg-line outline-none
              [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-5
              [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:rounded-full
              [&::-webkit-slider-thumb]:bg-ocean [&::-webkit-slider-thumb]:shadow-float
              [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:hover:scale-110"
          />
          <span
            className="min-w-[100px] rounded-full px-3 py-1 text-center text-xs font-semibold transition-all duration-300"
            style={{ background: lv.bg, color: lv.color, border: `1px solid ${lv.border}` }}
          >
            {score}% — {lv.badge}
          </span>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-line bg-panel shadow-soft">
        <svg width="100%" viewBox="0 0 680 300" role="img" aria-label={`Bridge at ${score}% vulnerability`}>
          <defs>
            <clipPath id="bvc"><rect x="60" y="40" width="560" height="240"/></clipPath>
          </defs>
          <rect x="60" y="40" width="560" height="165" rx="3" fill={skyColor}/>
          <rect x="60" y="205" width="560" height="75" fill={waterColor}/>
          <g opacity="0.3">
            <line x1="80"  y1="220" x2="200" y2="220" stroke="#fff" strokeWidth="1.5"/>
            <line x1="240" y1="228" x2="380" y2="228" stroke="#fff" strokeWidth="1.5"/>
            <line x1="420" y1="220" x2="560" y2="220" stroke="#fff" strokeWidth="1.5"/>
            <line x1="100" y1="240" x2="290" y2="240" stroke="#fff" strokeWidth="1"/>
            <line x1="350" y1="244" x2="580" y2="244" stroke="#fff" strokeWidth="1"/>
          </g>
          <rect x="140" y="205" width="28" height="70" rx="2" fill={pierColor}/>
          <rect x="512" y="205" width="28" height="70" rx="2" fill={pierColor}/>
          <rect x="140" y="75"  width="28" height="130" rx="2" fill={structColor}/>
          <rect x="512" y="75"  width="28" height="130" rx="2" fill={structColor}/>
          <rect x="134" y="104" width="40" height="10"  rx="1" fill={structColor}/>
          <rect x="506" y="104" width="40" height="10"  rx="1" fill={structColor}/>
          <rect x="146" y="66"  width="16" height="12"  rx="2" fill={finialColor}/>
          <rect x="518" y="66"  width="16" height="12"  rx="2" fill={finialColor}/>
          <path d={`M154 71 Q210 ${cableSag} 300 188`} fill="none" stroke={cableColor} strokeWidth="3"/>
          <path d={`M526 71 Q470 ${cableSag} 380 188`} fill="none" stroke={cableColor} strokeWidth="3"/>
          <g stroke={cableColor} strokeWidth="1.5">
            <line x1="180" y1="110" x2="180" y2="188"/>
            <line x1="210" y1="132" x2="210" y2="188"/>
            <line x1="240" y1="151" x2="240" y2="188"/>
            <line x1="270" y1="166" x2="270" y2="188"/>
            <line x1="500" y1="110" x2="500" y2="188"/>
            <line x1="470" y1="132" x2="470" y2="188"/>
            <line x1="440" y1="151" x2="440" y2="188"/>
            <line x1="410" y1="166" x2="410" y2="188"/>
          </g>
          <rect x="80" y="188" width="520" height="20" rx="2" fill={structColor}/>
          <rect x="80" y="208" width="520" height="12" rx="1" fill={lerp('#b8985a','#4a3020',t)}/>
          <rect x="80" y="188" width="520" height="20" rx="2" fill="#8B4513" opacity={rustOpacity}/>
          <g clipPath="url(#bvc)">
            {CRACK_TEMPLATES.slice(0,numCracks).map((tmpl,i) => {
              const op = Math.min(1,(t*CRACK_TEMPLATES.length-i)*1.5)
              return (
                <g key={i}>
                  <path d={crackPath(tmpl)} fill="none"
                    stroke={t>0.6?'#1a0a00':'#3a2a10'}
                    strokeWidth={t>0.7?2:1} strokeLinecap="round" opacity={op}/>
                  {t>0.7&&i<6&&(
                    <ellipse cx={tmpl.x+tmpl.segs[0][0]/2} cy={tmpl.y+tmpl.segs[0][1]/2}
                      rx={Math.min(3,(t-0.7)*10)} ry="1.5"
                      fill="#0a0500" opacity={((t-0.7)/0.3*0.8).toFixed(2)}/>
                  )}
                </g>
              )
            })}
          </g>
        </svg>
      </div>

      <div className="text-center">
        <p className="text-sm font-semibold transition-colors duration-300" style={{ color: lv.color }}>
          {lv.label}
        </p>
        <p className="mt-1 text-xs text-muted">{lv.sub}</p>
      </div>
    </div>
  )
}
