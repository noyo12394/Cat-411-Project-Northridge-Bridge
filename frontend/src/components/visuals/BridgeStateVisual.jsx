import { useEffect, useMemo } from 'react'
import { motion, useAnimationControls, useReducedMotion } from 'framer-motion'
import { getBridgeStageLegend, getBridgeStructuralState } from '../../lib/bridgeVisualState'

const spring = {
  type: 'spring',
  stiffness: 110,
  damping: 18,
  mass: 0.92,
}

function range(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function buildCracks(visual) {
  const count = Math.max(1, visual.crackCount)
  return Array.from({ length: count }).map((_, index) => {
    const side = index % 2 === 0 ? -1 : 1
    const baseX = 382 + side * (10 + index * 13)
    const baseY = 164 + visual.deckSag * 0.42 + (index % 3) * 4
    const length = 14 + index * 2.8
    return {
      key: `crack-${index}`,
      path: `M${baseX} ${baseY} L${baseX - 6 * side} ${baseY + length * 0.4} L${baseX + 4 * side} ${baseY + length} L${baseX - 5 * side} ${baseY + length * 1.48}`,
      width: index < 2 ? 3.4 : 2.2,
      opacity: Math.max(0, visual.crackOpacity - index * 0.085),
    }
  })
}

function buildDust(visual) {
  return Array.from({ length: visual.dustCount }).map((_, index) => ({
    key: `dust-${index}`,
    x: 425 + index * 14,
    y: 298 - (index % 3) * 6,
    scale: 0.35 + index * 0.11,
    delay: index * 0.08,
  }))
}

function StateChip({ label, active, tone }) {
  const toneClass = active
    ? tone === 'critical'
      ? 'border-orange-300/80 bg-orange-500/18 text-orange-100 shadow-[0_0_22px_rgba(251,146,60,0.2)]'
      : 'border-sky-300/80 bg-sky-500/18 text-sky-100 shadow-[0_0_20px_rgba(56,189,248,0.18)]'
    : 'border-white/10 bg-white/[0.03] text-slate-400'

  return (
    <span className={`rounded-full border px-3 py-1.5 text-[11px] font-medium uppercase tracking-[0.24em] ${toneClass}`}>
      {label}
    </span>
  )
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
  const visual = useMemo(() => visualState ?? getBridgeStructuralState({ vulnerabilityScore: score }), [score, visualState])
  const stageLegend = useMemo(() => getBridgeStageLegend(), [])
  const cracks = useMemo(() => buildCracks(visual), [visual])
  const dust = useMemo(() => buildDust(visual), [visual])

  useEffect(() => {
    if (!replayToken || reducedMotion) return
    replayControls.start({
      scale: [1, 1.012, 1],
      y: [0, -5, 0],
      transition: { duration: 0.85, ease: [0.22, 1, 0.36, 1] },
    })
  }, [reducedMotion, replayControls, replayToken])

  const waveTravel = 0.2 + visual.waveAmplitude * 0.06
  const deckBaseline = 160 + visual.deckSag * 0.55
  const collapseDrop = visual.collapseOffset
  const pierTilt = visual.pierTilt
  const jointGap = visual.jointGap
  const deckRotation = visual.segmentRotation
  const tintOpacity = 0.14 + visual.emergencyTint * 0.34
  const modeLabel =
    visual.mode === 'event'
      ? 'View: Event Damage Scenario'
      : visual.mode === 'priority'
        ? 'View: Inspection Prioritization'
        : 'View: Intrinsic Vulnerability'

  const segments = [
    {
      key: 'west',
      x: 82,
      y: deckBaseline - 7,
      width: 156,
      rotation: -deckRotation * 0.2,
      extraDrop: 0,
    },
    {
      key: 'midwest',
      x: 240,
      y: deckBaseline - 12,
      width: 144,
      rotation: deckRotation * 0.14,
      extraDrop: visual.supportFailure * 3,
    },
    {
      key: 'mideast',
      x: 392 + jointGap * 0.55,
      y: deckBaseline - 4 + collapseDrop,
      width: 146,
      rotation: deckRotation * 0.82 + visual.supportFailure * 9,
      extraDrop: collapseDrop,
    },
    {
      key: 'east',
      x: 548 + jointGap * 0.28,
      y: deckBaseline + visual.supportFailure * 8 + collapseDrop * 0.18,
      width: 122,
      rotation: -deckRotation * 0.28 + visual.supportFailure * 4,
      extraDrop: collapseDrop * 0.18,
    },
  ]

  const piers = [
    { key: 'p1', x: 144, y: 202, width: 30, height: 122, rotation: -pierTilt * 0.16, settle: 0 },
    { key: 'p2', x: 298, y: 196, width: 32, height: 144, rotation: pierTilt * 0.22, settle: visual.supportFailure * 8 },
    { key: 'p3', x: 466, y: 198 + visual.supportFailure * 14, width: 34, height: 138, rotation: -pierTilt * 0.46 - collapseDrop * 0.03, settle: visual.supportFailure * 16 },
    { key: 'p4', x: 606, y: 206, width: 28, height: 118, rotation: pierTilt * 0.14, settle: visual.supportFailure * 4 },
  ]

  return (
    <div className="relative overflow-hidden rounded-[32px] border border-white/10 bg-[linear-gradient(180deg,#07111d_0%,#091524_35%,#0c1626_100%)] p-6 shadow-[0_28px_80px_rgba(15,23,42,0.34)]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_10%,rgba(56,189,248,0.12),transparent_28%),radial-gradient(circle_at_82%_12%,rgba(139,92,246,0.12),transparent_24%),linear-gradient(90deg,rgba(148,163,184,0.05)_1px,transparent_1px),linear-gradient(rgba(148,163,184,0.05)_1px,transparent_1px)] bg-[size:auto,auto,32px_32px,32px_32px]" />
      <motion.div className="pointer-events-none absolute inset-0" animate={{ opacity: [0.38, 0.52 + visual.stressGlow * 0.3, 0.38] }} transition={{ duration: reducedMotion ? 0.2 : 3.2, repeat: Infinity, ease: 'easeInOut' }}>
        <div className="absolute inset-x-20 top-12 h-32 rounded-full bg-sky-400/10 blur-3xl" />
        <div
          className="absolute inset-x-24 bottom-12 h-28 rounded-full blur-3xl"
          style={{ background: `rgba(249, 115, 22, ${tintOpacity})` }}
        />
      </motion.div>

      <div className="relative flex flex-col gap-5 border-b border-white/10 pb-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-2xl">
          <p className="font-mono text-[11px] uppercase tracking-[0.34em] text-sky-200/70">Structural state</p>
          <h3 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-white">{title}</h3>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            {caption ?? visual.summary}
          </p>
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

      <motion.div className="relative mt-6" animate={replayControls}>
        <svg viewBox="0 0 760 390" className="w-full overflow-visible">
          <defs>
            <linearGradient id="bridgeDeckFill" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#e2e8f0" stopOpacity="0.92" />
              <stop offset="50%" stopColor="#67e8f9" stopOpacity="0.76" />
              <stop offset="100%" stopColor="#f97316" stopOpacity={0.22 + visual.emergencyTint * 0.32} />
            </linearGradient>
            <linearGradient id="bridgePierFill" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#dbeafe" stopOpacity="0.88" />
              <stop offset="100%" stopColor="#64748b" stopOpacity="0.82" />
            </linearGradient>
            <radialGradient id="bridgeDustFill" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(255,237,213,0.9)" />
              <stop offset="100%" stopColor="rgba(249,115,22,0)" />
            </radialGradient>
          </defs>

          <motion.ellipse
            cx="384"
            cy="338"
            rx="292"
            ry={16 + visual.supportFailure * 8}
            fill="rgba(2,6,23,0.76)"
            animate={{ opacity: 0.42 + visual.stressGlow * 0.24, scaleX: 1 + visual.waveAmplitude * 0.01 }}
            transition={spring}
          />

          <motion.g
            animate={
              reducedMotion
                ? { x: 0, y: 0 }
                : {
                    x: [0, waveTravel * 2.4, 0, -waveTravel * 1.6, 0],
                    y: [0, -waveTravel * 2.8, 0, waveTravel * 1.5, 0],
                  }
            }
            transition={
              reducedMotion
                ? { duration: 0.2 }
                : { duration: 5.6 - visual.waveAmplitude * 0.35, repeat: Infinity, ease: 'easeInOut' }
            }
          >
            {Array.from({ length: 4 }).map((_, index) => (
              <motion.path
                key={`wave-${index}`}
                d={`M ${74 - index * 20} ${94 + index * 26} C ${192 - index * 10} ${36 + index * 12}, ${430 + index * 4} ${42 + index * 8}, ${688 + index * 20} ${120 + index * 10}`}
                fill="none"
                stroke="rgba(103,232,249,0.55)"
                strokeWidth={1.8 - index * 0.18}
                strokeDasharray="6 12"
                strokeOpacity={Math.max(0.08, 0.3 + visual.stressGlow * 0.34 - index * 0.08)}
                animate={reducedMotion ? { opacity: 0.26 } : { pathLength: [0.84, 1, 0.84], opacity: [0.22, 0.34 + visual.stressGlow * 0.26, 0.22] }}
                transition={reducedMotion ? { duration: 0.2 } : { duration: 3.2 + index * 0.24, repeat: Infinity, ease: 'easeInOut' }}
              />
            ))}

            {piers.map((pier) => (
              <motion.rect
                key={pier.key}
                x={pier.x}
                y={pier.y + pier.settle}
                width={pier.width}
                height={pier.height}
                rx="14"
                fill="url(#bridgePierFill)"
                stroke={`rgba(255,255,255,${0.18 + visual.crackOpacity * 0.12})`}
                strokeWidth="1.3"
                transform={`rotate(${pier.rotation} ${pier.x + pier.width / 2} ${pier.y + pier.height / 2})`}
                animate={{ x: pier.x, y: pier.y + pier.settle, rotate: pier.rotation, scaleY: 1 - visual.supportFailure * (pier.key === 'p3' ? 0.12 : 0.04) }}
                transition={spring}
              />
            ))}

            <motion.path
              d={`M88 ${deckBaseline + 2} C 210 ${deckBaseline - 44}, 304 ${deckBaseline - 48}, 386 ${deckBaseline - 6} S 574 ${deckBaseline + 30}, 678 ${deckBaseline + 12}`}
              fill="none"
              stroke="rgba(103,232,249,0.18)"
              strokeWidth="12"
              strokeLinecap="round"
              animate={{ opacity: 0.18 + visual.stressGlow * 0.18 }}
              transition={spring}
            />

            {segments.map((segment) => (
              <motion.rect
                key={segment.key}
                x={segment.x}
                y={segment.y + segment.extraDrop}
                width={segment.width}
                height="28"
                rx="12"
                fill="url(#bridgeDeckFill)"
                stroke={`rgba(255,255,255,${0.14 + visual.crackOpacity * 0.16})`}
                strokeWidth="1.2"
                transform={`rotate(${segment.rotation} ${segment.x + segment.width / 2} ${segment.y + segment.extraDrop + 14})`}
                animate={{ x: segment.x, y: segment.y + segment.extraDrop, rotate: segment.rotation }}
                transition={spring}
              />
            ))}

            <motion.path
              d={`M90 ${deckBaseline + 12} H676`}
              stroke={`rgba(241,245,249,${0.68 - visual.collapseOffset * 0.004})`}
              strokeWidth="4"
              strokeLinecap="round"
              animate={{ opacity: 0.72 - visual.debrisOpacity * 0.24 }}
              transition={spring}
            />

            {cracks.map((crack) => (
              <motion.path
                key={crack.key}
                d={crack.path}
                fill="none"
                stroke={crack.key === 'crack-0' ? '#fb923c' : '#f97373'}
                strokeWidth={crack.width}
                strokeLinecap="round"
                initial={false}
                animate={{ opacity: crack.opacity }}
                transition={spring}
              />
            ))}

            {visual.jointGap > 3 ? (
              <motion.rect
                x={384}
                y={deckBaseline - 24}
                width={Math.max(3, visual.jointGap * 0.42)}
                height={34 + visual.supportFailure * 10}
                fill="rgba(2,6,23,0.78)"
                animate={{ opacity: 0.22 + visual.supportFailure * 0.42 }}
                transition={spring}
              />
            ) : null}

            {visual.deckBreak ? (
              <motion.path
                d={`M420 ${deckBaseline + 8} L430 ${deckBaseline + 26}`}
                stroke="#fbbf24"
                strokeWidth="3.2"
                strokeLinecap="round"
                animate={{ opacity: 0.5 + visual.crackOpacity * 0.32 }}
                transition={spring}
              />
            ) : null}

            {dust.map((puff) => (
              <motion.circle
                key={puff.key}
                cx={puff.x}
                cy={puff.y}
                r={12}
                fill="url(#bridgeDustFill)"
                animate={
                  reducedMotion
                    ? { opacity: visual.debrisOpacity * 0.24, scale: 0.6 + visual.debrisOpacity * puff.scale }
                    : {
                        opacity: [0, visual.debrisOpacity * 0.34, 0],
                        scale: [0.4, 0.82 + visual.debrisOpacity * puff.scale, 1.24 + visual.debrisOpacity * puff.scale],
                        y: [0, -10 - puff.scale * 3, -18 - puff.scale * 6],
                      }
                }
                transition={{
                  duration: reducedMotion ? 0.2 : 2.8 + puff.delay,
                  repeat: reducedMotion ? 0 : Infinity,
                  repeatDelay: reducedMotion ? 0 : 0.42,
                  delay: puff.delay,
                  ease: 'easeOut',
                }}
              />
            ))}
          </motion.g>
        </svg>
      </motion.div>

      <div className="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_220px]">
        <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-4 py-4 text-sm leading-7 text-slate-300">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">Dynamic structural summary</p>
          <p className="mt-3">{visual.summary}</p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-[22px] border border-white/10 bg-white/[0.04] px-3 py-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-slate-400">Deck sag</p>
            <p className="mt-2 text-2xl font-semibold text-white">{range(visual.deckSag, 0, 99).toFixed(1)}</p>
          </div>
          <div className="rounded-[22px] border border-white/10 bg-white/[0.04] px-3 py-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-slate-400">Support drift</p>
            <p className="mt-2 text-2xl font-semibold text-white">{range(visual.pierTilt, 0, 99).toFixed(1)}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
