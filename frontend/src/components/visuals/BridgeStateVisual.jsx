import { useEffect, useMemo, useRef } from 'react'
import { motion as Motion, useAnimationControls, useReducedMotion } from 'framer-motion'
import { getBridgeStageLegend, getBridgeStructuralState } from '../../lib/bridgeVisualState'

const spring = {
  type: 'spring',
  stiffness: 120,
  damping: 18,
  mass: 0.9,
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

function buildGeometry(visual) {
  const deckThickness = 28
  const baseY = 258
  const gap = 6 + visual.jointGap * 0.38
  const rightShift = visual.jointGap * 0.2
  const rightDrop = visual.collapseOffset * 0.24 + visual.supportFailure * 18
  const leftSag = visual.deckSag * 0.78
  const rightSag = visual.deckSag * 0.94 + rightDrop * 0.38

  const left = {
    startX: 108,
    endX: 382,
    y0: 110 + leftSag * 0.08,
    y1: 116 + leftSag * 0.42,
    y2: 120 + leftSag * 0.72,
    y3: 116 + leftSag * 0.48,
  }

  const right = {
    startX: 392 + gap,
    endX: 652 + rightShift,
    y0: 116 + rightSag * 0.34,
    y1: 122 + rightSag * 0.68,
    y2: 126 + rightSag * 0.94,
    y3: 118 + rightSag * 0.58 + rightDrop * 0.12,
  }

  const leftDeckPath = `M ${left.startX} ${left.y0} C 170 ${left.y0 - 4}, 238 ${left.y1}, 286 ${left.y2} S 346 ${left.y3}, ${left.endX} ${left.y3}`
  const rightDeckPath = `M ${right.startX} ${right.y0} C 448 ${right.y0 + 4}, 514 ${right.y1}, 564 ${right.y2} S 622 ${right.y3}, ${right.endX} ${right.y3}`

  const piers = [
    {
      key: 'pier-west',
      x: 176,
      topY: left.y0 + 22,
      width: 24,
      height: baseY - (left.y0 + 22),
      rotation: -visual.pierTilt * 0.08,
      settle: 0,
    },
    {
      key: 'pier-mid',
      x: 304,
      topY: left.y2 + 18,
      width: 26,
      height: baseY - (left.y2 + 18),
      rotation: visual.pierTilt * 0.12,
      settle: visual.supportFailure * 3,
    },
    {
      key: 'pier-east',
      x: 492 + rightShift * 0.2,
      topY: right.y1 + 18,
      width: 28,
      height: baseY - (right.y1 + 18) - visual.supportFailure * 12,
      rotation: -visual.pierTilt * 0.28 - visual.supportFailure * 4,
      settle: visual.supportFailure * 10,
    },
    {
      key: 'pier-far-east',
      x: 610 + rightShift * 0.18,
      topY: right.y3 + 16,
      width: 22,
      height: baseY - (right.y3 + 16) - visual.supportFailure * 6,
      rotation: visual.pierTilt * 0.14,
      settle: visual.supportFailure * 5,
    },
  ]

  return {
    baseY,
    deckThickness,
    gap,
    rightDrop,
    rightShift,
    rightRotation: visual.segmentRotation * 0.4 + visual.supportFailure * 6,
    leftDeckPath,
    rightDeckPath,
    jointX: 387,
    jointY: (left.y3 + right.y0) / 2,
    piers,
    shadowY: baseY + 12,
  }
}

function buildCracks(visual, geometry) {
  if (visual.crackOpacity < 0.08) {
    return []
  }

  const seeds = [
    { x: 284, y: 144, dx: -14, dy: 30 },
    { x: 344, y: 150, dx: 12, dy: 24 },
    { x: geometry.jointX - 4, y: geometry.jointY - 4, dx: -8, dy: 30 },
    { x: geometry.jointX + geometry.gap + 6, y: geometry.jointY + 2, dx: 12, dy: 34 },
    { x: 514 + geometry.rightShift * 0.25, y: 156 + geometry.rightDrop * 0.18, dx: -12, dy: 28 },
    { x: 580 + geometry.rightShift * 0.12, y: 164 + geometry.rightDrop * 0.28, dx: 14, dy: 24 },
  ]

  return seeds.slice(0, Math.max(1, visual.crackCount)).map((seed, index) => {
    const branch = 7 + index * 1.8
    return {
      key: `crack-${index}`,
      path: `M ${seed.x} ${seed.y} l ${seed.dx * 0.35} ${seed.dy * 0.34} l ${branch} ${branch * 0.9} l ${-branch * 0.6} ${branch}`,
      opacity: Math.max(0, visual.crackOpacity - index * 0.08),
      width: index < 2 ? 2.8 : 2.1,
    }
  })
}

function buildDust(visual, geometry) {
  if (visual.debrisOpacity < 0.04) {
    return []
  }

  return Array.from({ length: Math.max(2, visual.dustCount) }).map((_, index) => ({
    key: `dust-${index}`,
    x: geometry.jointX + 18 + index * 10,
    y: geometry.baseY - 10 - (index % 3) * 5,
    scale: 0.3 + index * 0.09,
    delay: index * 0.05,
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
  const replayControls = useAnimationControls()
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
    if (!replayToken || reducedMotion) return
    replayControls.start({
      scale: [1, 1.01 + visual.supportFailure * 0.025, 1],
      x: [0, 3 + visual.pierTilt * 0.14, -2 - visual.pierTilt * 0.08, 0],
      y: [0, -4 - visual.deckSag * 0.05, 0],
      rotate: [0, visual.segmentRotation * 0.02, -visual.segmentRotation * 0.015, 0],
      transition: { duration: 0.82, ease: [0.22, 1, 0.36, 1] },
    })
  }, [
    reducedMotion,
    replayControls,
    replayToken,
    visual.deckSag,
    visual.pierTilt,
    visual.segmentRotation,
    visual.supportFailure,
  ])

  useEffect(() => {
    if (reducedMotion) return
    const nextScore = visual.visualScore ?? visual.score

    if (previousVisualScore.current == null) {
      previousVisualScore.current = nextScore
      return
    }

    const delta = Math.abs(nextScore - previousVisualScore.current)
    previousVisualScore.current = nextScore

    if (delta < 0.035) return

    replayControls.start({
      scale: [1, 1.008 + delta * 0.045, 1],
      x: [0, delta * 5, -delta * 4, 0],
      y: [0, -delta * 8, 0],
      rotate: [0, delta * 1.3, -delta * 1.1, 0],
      transition: { duration: 0.72, ease: [0.22, 1, 0.36, 1] },
    })
  }, [reducedMotion, replayControls, visual.score, visual.visualScore])

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
              <stop offset="0%" stopColor="#e2e8f0" stopOpacity="0.94" />
              <stop offset="45%" stopColor="#9ae6ff" stopOpacity="0.88" />
              <stop offset="100%" stopColor="#f6ad55" stopOpacity={0.24 + visual.emergencyTint * 0.32} />
            </linearGradient>
            <linearGradient id="pierFill" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#dbeafe" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#64748b" stopOpacity="0.82" />
            </linearGradient>
            <radialGradient id="dustFill" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(255,237,213,0.92)" />
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

          <Motion.g animate={replayControls} style={{ transformBox: 'fill-box', transformOrigin: 'center center' }}>
            <Motion.ellipse
              cx="384"
              cy={geometry.shadowY}
              rx="264"
              ry={12 + visual.supportFailure * 6}
              fill="rgba(2,6,23,0.55)"
              animate={{ opacity: 0.36 + visual.stressGlow * 0.22, scaleX: 1 + visual.waveAmplitude * 0.01 }}
              transition={spring}
            />

            {geometry.piers.map((pier) => (
              <Motion.g
                key={pier.key}
                animate={{ x: pier.x, y: pier.topY + pier.settle, rotate: pier.rotation }}
                transition={spring}
                style={{ transformBox: 'fill-box', transformOrigin: 'center top' }}
              >
                <rect
                  x={-pier.width / 2}
                  y="0"
                  width={pier.width}
                  height={pier.height}
                  rx="12"
                  fill="url(#pierFill)"
                  stroke={`rgba(255,255,255,${0.18 + visual.crackOpacity * 0.1})`}
                  strokeWidth="1.2"
                />
                <rect
                  x={-pier.width / 2 - 10}
                  y="-9"
                  width={pier.width + 20}
                  height="10"
                  rx="5"
                  fill="rgba(203,213,225,0.92)"
                  opacity={0.84}
                />
              </Motion.g>
            ))}

            <Motion.path
              d={geometry.leftDeckPath}
              fill="none"
              stroke="rgba(8,15,28,0.55)"
              strokeWidth={geometry.deckThickness + 12}
              strokeLinecap="round"
              animate={{ d: geometry.leftDeckPath }}
              transition={spring}
            />
            <Motion.path
              d={geometry.rightDeckPath}
              fill="none"
              stroke="rgba(8,15,28,0.55)"
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

            <Motion.g
              animate={{
                x: geometry.rightShift * 0.18,
                y: geometry.rightDrop * 0.18,
                rotate: geometry.rightRotation,
              }}
              transition={spring}
              style={{ transformBox: 'fill-box', transformOrigin: '460px 140px' }}
            >
              <Motion.path
                d={geometry.rightDeckPath}
                fill="none"
                stroke="url(#deckStroke)"
                strokeWidth={geometry.deckThickness}
                strokeLinecap="round"
                animate={{ d: geometry.rightDeckPath }}
                transition={spring}
              />
            </Motion.g>

            <Motion.path
              d={geometry.leftDeckPath}
              fill="none"
              stroke="rgba(255,255,255,0.35)"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray="1 10"
              animate={{ opacity: 0.16 + visual.stressGlow * 0.18 }}
              transition={spring}
            />

            <Motion.path
              d={geometry.rightDeckPath}
              fill="none"
              stroke="rgba(255,255,255,0.26)"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray="1 10"
              animate={{ opacity: 0.12 + visual.stressGlow * 0.16 }}
              transition={spring}
            />

            {geometry.gap > 8 ? (
              <Motion.rect
                x={geometry.jointX}
                y={geometry.jointY - 18}
                width={geometry.gap * 0.84}
                height={42 + visual.supportFailure * 8}
                rx="10"
                fill="rgba(6,11,20,0.82)"
                animate={{ opacity: 0.24 + visual.supportFailure * 0.4 }}
                transition={spring}
              />
            ) : null}

            {cracks.map((crack) => (
              <Motion.path
                key={crack.key}
                d={crack.path}
                fill="none"
                stroke={crack.key.includes('0') || crack.key.includes('2') ? '#fb923c' : '#fca5a5'}
                strokeWidth={crack.width}
                strokeLinecap="round"
                animate={{ opacity: crack.opacity }}
                transition={spring}
              />
            ))}

            {visual.deckBreak ? (
              <Motion.path
                d={`M ${geometry.jointX + 6} ${geometry.jointY - 6} l 10 16 l -7 20`}
                fill="none"
                stroke="#fde68a"
                strokeWidth="3.2"
                strokeLinecap="round"
                animate={{ opacity: 0.45 + visual.crackOpacity * 0.34 }}
                transition={spring}
              />
            ) : null}

            {dust.map((puff) => (
              <Motion.circle
                key={puff.key}
                cx={puff.x}
                cy={puff.y}
                r="14"
                fill="url(#dustFill)"
                animate={
                  reducedMotion
                    ? { opacity: visual.debrisOpacity * 0.18, scale: 0.6 + puff.scale * visual.debrisOpacity }
                    : {
                        opacity: [0, visual.debrisOpacity * 0.3, 0],
                        scale: [0.4, 0.9 + puff.scale * 0.6, 1.3 + puff.scale],
                        y: [0, -10 - puff.scale * 4, -22 - puff.scale * 8],
                        x: [0, (puff.scale - 0.4) * 6, (puff.scale - 0.4) * 10],
                      }
                }
                transition={{
                  duration: reducedMotion ? 0.2 : 2.4 + puff.delay,
                  repeat: reducedMotion ? 0 : Infinity,
                  repeatDelay: reducedMotion ? 0 : 0.5,
                  delay: puff.delay,
                  ease: 'easeOut',
                }}
              />
            ))}
          </Motion.g>
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
