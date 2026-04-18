import { useEffect, useMemo, useRef } from 'react'
import { motion as Motion, useAnimationControls, useReducedMotion } from 'framer-motion'
import { getBridgeStageLegend, getBridgeStructuralState } from '../../lib/bridgeVisualState'

const spring = {
  type: 'spring',
  stiffness: 128,
  damping: 22,
  mass: 0.86,
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function formatMetric(value, digits = 1) {
  return clamp(value, 0, 999).toFixed(digits)
}

function StateChip({ label, active, tone }) {
  const activeClasses =
    tone === 'critical'
      ? 'border-orange-300/80 bg-orange-500/18 text-orange-100 shadow-[0_0_22px_rgba(251,146,60,0.2)]'
      : 'border-sky-300/80 bg-sky-500/18 text-sky-100 shadow-[0_0_20px_rgba(56,189,248,0.18)]'

  return (
    <span
      className={`rounded-full border px-3 py-1.5 text-[11px] font-medium uppercase tracking-[0.24em] ${
        active ? activeClasses : 'border-white/10 bg-white/[0.03] text-slate-400'
      }`}
    >
      {label}
    </span>
  )
}

function buildPierPath({ x, topY, baseY, width, lean }) {
  const halfWidth = width / 2
  const bottomCenter = x + lean
  return `M ${x - halfWidth} ${topY} L ${x + halfWidth} ${topY} L ${bottomCenter + halfWidth} ${baseY} L ${bottomCenter - halfWidth} ${baseY} Z`
}

function buildGeometry(visual) {
  const baseY = 248
  const deckThickness = 24
  const jointGap = 2 + visual.jointGap * 0.38
  const rightShift = visual.jointGap * 0.14 + visual.supportFailure * 3.8
  const rightDrop = visual.collapseOffset * 0.26
  const leftSag = visual.deckSag * 0.52
  const rightSag = visual.deckSag * 0.68 + rightDrop * 0.22

  const left = {
    startX: 156,
    endX: 380,
    y0: 118,
    c1x: 214,
    c1y: 118 + leftSag * 0.08,
    c2x: 286,
    c2y: 126 + leftSag * 0.42,
    y3: 130 + leftSag * 0.58,
  }

  const right = {
    startX: 384 + jointGap,
    endX: 566 + rightShift,
    y0: 124 + rightSag * 0.12,
    c1x: 446 + rightShift * 0.18,
    c1y: 130 + rightSag * 0.38,
    c2x: 514 + rightShift * 0.24,
    c2y: 138 + rightSag * 0.62,
    y3: 140 + rightSag * 0.74 + rightDrop * 0.18,
  }

  const leftDeckPath = `M ${left.startX} ${left.y0} C ${left.c1x} ${left.c1y}, ${left.c2x} ${left.c2y}, ${left.endX} ${left.y3}`
  const rightDeckPath = `M ${right.startX} ${right.y0} C ${right.c1x} ${right.c1y}, ${right.c2x} ${right.c2y}, ${right.endX} ${right.y3}`

  const piers = [
    {
      key: 'pier-west',
      x: 210,
      topY: 146 + leftSag * 0.08,
      width: 18,
      lean: -visual.pierTilt * 0.04,
      settle: 0,
      compression: 0,
    },
    {
      key: 'pier-mid',
      x: 304,
      topY: 150 + leftSag * 0.2,
      width: 19,
      lean: visual.pierTilt * 0.08,
      settle: visual.supportFailure * 2.5,
      compression: visual.supportFailure * 2,
    },
    {
      key: 'pier-east',
      x: 436 + rightShift * 0.12,
      topY: 150 + rightSag * 0.16,
      width: 19,
      lean: visual.pierTilt * 0.16 + visual.supportFailure * 7,
      settle: visual.supportFailure * 6,
      compression: visual.supportFailure * 10,
    },
    {
      key: 'pier-far-east',
      x: 520 + rightShift * 0.18,
      topY: 144 + rightSag * 0.34 + rightDrop * 0.08,
      width: 18,
      lean: -visual.pierTilt * 0.08 - visual.supportFailure * 6,
      settle: visual.supportFailure * 4,
      compression: visual.supportFailure * 6,
    },
  ].map((pier) => {
    const y = pier.topY + pier.settle
    const bottomY = baseY - pier.compression
    return {
      ...pier,
      y,
      bottomY,
      path: buildPierPath({ x: pier.x, topY: y, baseY: bottomY, width: pier.width, lean: pier.lean }),
      capX: pier.x - pier.width / 2 - 8,
      capY: y - 6,
      capWidth: pier.width + 16,
    }
  })

  return {
    baseY,
    deckThickness,
    jointX: 382,
    jointY: (left.y3 + right.y0) / 2,
    leftDeckPath,
    rightDeckPath,
    shadowY: baseY + 12,
    jointGap,
    rightDrop,
    rightShift,
    rightRotation: visual.segmentRotation,
    piers,
  }
}

function buildCracks(visual, geometry) {
  if (visual.crackCount <= 0 || visual.crackOpacity <= 0.04) {
    return []
  }

  const seeds = [
    { x: 292, y: 152, dx: -10, dy: 18 },
    { x: geometry.jointX - 14, y: geometry.jointY - 8, dx: -7, dy: 22 },
    { x: geometry.jointX + 10, y: geometry.jointY - 4, dx: 8, dy: 20 },
    { x: 432 + geometry.rightShift * 0.1, y: 156 + geometry.rightDrop * 0.05, dx: -8, dy: 22 },
    { x: 518 + geometry.rightShift * 0.16, y: 154 + geometry.rightDrop * 0.12, dx: 10, dy: 24 },
    { x: 560 + geometry.rightShift * 0.18, y: 148 + geometry.rightDrop * 0.16, dx: -8, dy: 16 },
  ]

  return seeds.slice(0, visual.crackCount).map((seed, index) => {
    const branch = 4 + index * 1.4
    return {
      key: `crack-${index}`,
      path: `M ${seed.x} ${seed.y} l ${seed.dx * 0.5} ${seed.dy * 0.46} l ${branch} ${branch * 0.9} l ${-branch * 0.7} ${branch * 0.95}`,
      opacity: Math.max(0, visual.crackOpacity - index * 0.08),
      width: index < 2 ? 2.3 : 1.8,
      stroke: index < 2 ? '#fb923c' : '#fca5a5',
    }
  })
}

function buildDust(visual, geometry) {
  if (visual.dustCount <= 0 || visual.debrisOpacity <= 0.02) {
    return []
  }

  return Array.from({ length: visual.dustCount }).map((_, index) => ({
    key: `dust-${index}`,
    x: geometry.jointX + 24 + index * 8,
    y: geometry.baseY - 4 - (index % 3) * 4,
    radius: 10 + index * 1.5,
    opacity: Math.max(0.04, visual.debrisOpacity * (0.22 - index * 0.015)),
  }))
}

export default function BridgeStateVisual({
  score = 0.4,
  visualState,
  title = 'Structural state visual',
  caption,
  replayToken = 0,
}) {
  const reducedMotion = useReducedMotion()
  const pulseControls = useAnimationControls()
  const previousVisualScore = useRef(null)

  const visual = useMemo(
    () => visualState ?? getBridgeStructuralState({ vulnerabilityScore: score }),
    [score, visualState],
  )
  const geometry = useMemo(() => buildGeometry(visual), [visual])
  const cracks = useMemo(() => buildCracks(visual, geometry), [visual, geometry])
  const dust = useMemo(() => buildDust(visual, geometry), [visual, geometry])
  const stageLegend = useMemo(() => getBridgeStageLegend(), [])

  useEffect(() => {
    if (!reducedMotion && replayToken) {
      pulseControls.start({
        opacity: [0, 0.18, 0],
        transition: { duration: 0.62, ease: [0.22, 1, 0.36, 1] },
      })
    }
  }, [pulseControls, reducedMotion, replayToken])

  useEffect(() => {
    if (reducedMotion) return
    const nextScore = visual.visualScore ?? visual.score

    if (previousVisualScore.current == null) {
      previousVisualScore.current = nextScore
      return
    }

    const delta = Math.abs(nextScore - previousVisualScore.current)
    previousVisualScore.current = nextScore

    if (delta < 0.03) return

    pulseControls.start({
      opacity: [0, 0.14 + delta * 0.2, 0],
      transition: { duration: 0.54, ease: [0.22, 1, 0.36, 1] },
    })
  }, [pulseControls, reducedMotion, visual.score, visual.visualScore])

  const modeLabel =
    visual.mode === 'event'
      ? 'View: Event Damage Scenario'
      : visual.mode === 'priority'
        ? 'View: Inspection Prioritization'
        : 'View: Intrinsic Vulnerability'

  return (
    <div className="relative overflow-hidden rounded-[32px] border border-white/10 bg-[linear-gradient(180deg,#07111d_0%,#091524_35%,#0c1626_100%)] p-6 shadow-[0_28px_80px_rgba(15,23,42,0.34)]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_10%,rgba(56,189,248,0.12),transparent_24%),radial-gradient(circle_at_82%_10%,rgba(139,92,246,0.10),transparent_22%),linear-gradient(90deg,rgba(148,163,184,0.05)_1px,transparent_1px),linear-gradient(rgba(148,163,184,0.05)_1px,transparent_1px)] bg-[size:auto,auto,32px_32px,32px_32px]" />

      <div className="relative flex flex-col gap-5 border-b border-white/10 pb-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-2xl">
          <p className="font-mono text-[11px] uppercase tracking-[0.34em] text-sky-200/70">
            Structural state
          </p>
          <h3 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-white">{title}</h3>
          <p className="mt-3 text-sm leading-7 text-slate-300">{caption ?? visual.summary}</p>
        </div>
        <div className="flex flex-wrap items-start gap-2">
          <span className="rounded-full border border-sky-300/20 bg-sky-500/10 px-3 py-2 text-[11px] font-medium uppercase tracking-[0.24em] text-sky-100">
            {modeLabel}
          </span>
          <span className="rounded-full border border-orange-300/20 bg-orange-400/10 px-3 py-2 text-[11px] font-medium uppercase tracking-[0.24em] text-orange-100">
            {visual.stageHeading}
          </span>
          <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-[11px] font-medium uppercase tracking-[0.24em] text-slate-200">
            Score {score.toFixed(2)}
          </span>
        </div>
      </div>

      <div className="relative mt-5 flex flex-wrap gap-2">
        {stageLegend.map((stage) => (
          <StateChip
            key={stage.key}
            label={stage.label}
            active={stage.key === visual.stageKey}
            tone={stage.key === 'critical' ? 'critical' : 'default'}
          />
        ))}
      </div>

      <div className="relative mt-6 rounded-[28px] border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.03)_0%,rgba(255,255,255,0.02)_100%)] p-4">
        <svg viewBox="0 0 760 310" className="h-[280px] w-full">
          <defs>
            <linearGradient id="deckStroke" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#e2e8f0" stopOpacity="0.96" />
              <stop offset="45%" stopColor="#a5f3fc" stopOpacity="0.88" />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.16 + visual.emergencyTint * 0.28} />
            </linearGradient>
            <linearGradient id="deckHighlight" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(255,255,255,0.42)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0.08)" />
            </linearGradient>
            <linearGradient id="pierFill" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#dbeafe" stopOpacity="0.92" />
              <stop offset="100%" stopColor="#64748b" stopOpacity="0.84" />
            </linearGradient>
            <radialGradient id="dustFill" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(255,237,213,0.82)" />
              <stop offset="100%" stopColor="rgba(249,115,22,0)" />
            </radialGradient>
          </defs>

          {Array.from({ length: 7 }).map((_, index) => (
            <line
              key={`grid-h-${index}`}
              x1="38"
              x2="722"
              y1={44 + index * 34}
              y2={44 + index * 34}
              stroke="rgba(148,163,184,0.08)"
              strokeDasharray="4 10"
            />
          ))}

          <Motion.rect
            x="48"
            y="52"
            width="664"
            height="202"
            rx="26"
            fill="rgba(96,165,250,0.09)"
            initial={{ opacity: 0 }}
            animate={pulseControls}
          />

          <Motion.ellipse
            cx="380"
            cy={geometry.shadowY}
            rx="198"
            ry={11 + visual.supportFailure * 4}
            fill="rgba(2,6,23,0.46)"
            animate={{ opacity: 0.24 + visual.stressGlow * 0.2, scaleX: 1 + visual.waveAmplitude * 0.01 }}
            transition={spring}
          />

          {geometry.piers.map((pier) => (
            <g key={pier.key}>
              <Motion.path
                d={pier.path}
                fill="url(#pierFill)"
                stroke={`rgba(255,255,255,${0.14 + visual.crackOpacity * 0.12})`}
                strokeWidth="1.1"
                animate={{ d: pier.path }}
                transition={spring}
              />
              <Motion.rect
                x={pier.capX}
                y={pier.capY}
                width={pier.capWidth}
                height="8"
                rx="4"
                fill="rgba(226,232,240,0.9)"
                animate={{ x: pier.capX, y: pier.capY, width: pier.capWidth }}
                transition={spring}
              />
            </g>
          ))}

          <Motion.path
            d={geometry.leftDeckPath}
            fill="none"
            stroke="rgba(8,15,28,0.56)"
            strokeWidth={geometry.deckThickness + 12}
            strokeLinecap="round"
            animate={{ d: geometry.leftDeckPath }}
            transition={spring}
          />
          <Motion.path
            d={geometry.rightDeckPath}
            fill="none"
            stroke="rgba(8,15,28,0.56)"
            strokeWidth={geometry.deckThickness + 12}
            strokeLinecap="round"
            animate={{ d: geometry.rightDeckPath }}
            transition={spring}
          />

          <Motion.path
            d={geometry.leftDeckPath}
            fill="none"
            stroke="url(#deckStroke)"
            strokeWidth={geometry.deckThickness}
            strokeLinecap="round"
            animate={{ d: geometry.leftDeckPath }}
            transition={spring}
          />
          <Motion.path
            d={geometry.rightDeckPath}
            fill="none"
            stroke="url(#deckStroke)"
            strokeWidth={geometry.deckThickness}
            strokeLinecap="round"
            animate={{ d: geometry.rightDeckPath }}
            transition={spring}
          />

          <Motion.path
            d={geometry.leftDeckPath}
            fill="none"
            stroke="url(#deckHighlight)"
            strokeWidth="4"
            strokeLinecap="round"
            animate={{ d: geometry.leftDeckPath, opacity: 0.16 + visual.stressGlow * 0.1 }}
            transition={spring}
          />
          <Motion.path
            d={geometry.rightDeckPath}
            fill="none"
            stroke="url(#deckHighlight)"
            strokeWidth="4"
            strokeLinecap="round"
            animate={{ d: geometry.rightDeckPath, opacity: 0.14 + visual.stressGlow * 0.1 }}
            transition={spring}
          />

          {geometry.jointGap > 2 ? (
            <Motion.rect
              x={geometry.jointX}
              y={geometry.jointY - 14}
              width={geometry.jointGap}
              height={30 + visual.supportFailure * 12}
              rx="8"
              fill="rgba(6,11,20,0.86)"
              animate={{ x: geometry.jointX, y: geometry.jointY - 14, width: geometry.jointGap }}
              transition={spring}
            />
          ) : null}

          {cracks.map((crack) => (
            <Motion.path
              key={crack.key}
              d={crack.path}
              fill="none"
              stroke={crack.stroke}
              strokeWidth={crack.width}
              strokeLinecap="round"
              animate={{ d: crack.path, opacity: crack.opacity }}
              transition={spring}
            />
          ))}

          {visual.deckBreak ? (
            <Motion.path
              d={`M ${geometry.jointX + 2} ${geometry.jointY - 12} l 8 12 l -6 18`}
              fill="none"
              stroke="#fde68a"
              strokeWidth="3"
              strokeLinecap="round"
              animate={{ opacity: 0.3 + visual.crackOpacity * 0.35 }}
              transition={spring}
            />
          ) : null}

          {dust.map((puff) => (
            <Motion.circle
              key={puff.key}
              cx={puff.x}
              cy={puff.y}
              r={puff.radius}
              fill="url(#dustFill)"
              animate={{ opacity: puff.opacity, scale: 0.5 + visual.debrisOpacity * 0.9 }}
              transition={spring}
            />
          ))}
        </svg>
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,300px)]">
        <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-4 py-4 text-sm leading-7 text-slate-300">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">
            Dynamic structural summary
          </p>
          <p className="mt-3">{visual.summary}</p>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-[22px] border border-white/10 bg-white/[0.04] px-3 py-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-slate-400">Deck sag</p>
            <p className="mt-2 text-2xl font-semibold text-white">{formatMetric(visual.deckSag)}</p>
          </div>
          <div className="rounded-[22px] border border-white/10 bg-white/[0.04] px-3 py-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-slate-400">Support drift</p>
            <p className="mt-2 text-2xl font-semibold text-white">{formatMetric(visual.pierTilt)}</p>
          </div>
          <div className="rounded-[22px] border border-white/10 bg-white/[0.04] px-3 py-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-slate-400">Failure onset</p>
            <p className="mt-2 text-2xl font-semibold text-white">
              {formatMetric((visual.visualScore ?? visual.score) * 100, 0)}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
