import { motion, useReducedMotion } from 'framer-motion'
import { softSpring } from '../../animations/motion'
import type { DashboardAssessment } from '../../types/research'

interface BridgeStateVisualProps {
  assessment: DashboardAssessment
  title?: string
  caption?: string
  className?: string
}

const stageNotes = [
  'Intact structural posture with only ambient sway.',
  'Hairline cracking and low-amplitude vibration suggest slight damage.',
  'Joint displacement and pier stress indicate moderate damage progression.',
  'Deck sag, leaning piers, and heavy cracking indicate extensive damage.',
  'Collapse behavior is active: broken supports, dropped deck, dust, and emergency tint.',
]

function number(value: number, digits = 2) {
  return value.toFixed(digits)
}

export function BridgeStateVisual({
  assessment,
  title = 'Bridge state digital twin',
  caption,
  className = '',
}: BridgeStateVisualProps) {
  const reducedMotion = useReducedMotion()
  const visual = assessment.visual
  const ambientDuration = reducedMotion ? 0 : Math.max(2.8, 6.4 - visual.waveAmp * 2.2)
  const deckBaseline = 178 + visual.deckSag * 0.34
  const jointGap = visual.deckOffset * 12 + visual.collapse * 38
  const fractureOpacity = 0.14 + visual.fracture * 0.86
  const waveOpacity = 0.08 + visual.waveAmp * 0.55
  const urgencyGlow = 0.08 + visual.urgencyPulse * 0.35

  const segments = [
    {
      key: 'west',
      x: 92 - visual.deckOffset * 4,
      y: deckBaseline - visual.fracture * 2,
      width: 144,
      rotate: -1.5 * visual.columnLean,
      drop: 0,
    },
    {
      key: 'midwest',
      x: 246 - visual.deckOffset * 3,
      y: deckBaseline - 3,
      width: 138,
      rotate: visual.columnLean * 1.1,
      drop: visual.fracture * 5,
    },
    {
      key: 'mideast',
      x: 398 + jointGap * 0.52,
      y: deckBaseline + visual.fracture * 4 + visual.collapse * 54,
      width: 138,
      rotate: visual.columnLean * 7 + visual.collapse * 18,
      drop: visual.collapse * 58,
    },
    {
      key: 'east',
      x: 552 + jointGap * 0.36,
      y: deckBaseline + visual.fracture * 2 + visual.collapse * 18,
      width: 122,
      rotate: -visual.columnLean * 3 + visual.collapse * 6,
      drop: visual.collapse * 18,
    },
  ]

  const piers = [
    {
      key: 'p1',
      x: 150,
      y: 194 + visual.groundShift * 18,
      width: 32,
      height: 120,
      rotate: -visual.columnLean * 5,
      opacity: 0.96,
      collapseScale: 1 - visual.collapse * 0.14,
    },
    {
      key: 'p2',
      x: 302,
      y: 194 + visual.groundShift * 10,
      width: 34,
      height: 142,
      rotate: visual.columnLean * 7,
      opacity: 0.92,
      collapseScale: 1 - visual.collapse * 0.36,
    },
    {
      key: 'p3',
      x: 468,
      y: 194 + visual.groundShift * 24,
      width: 34,
      height: 132,
      rotate: -visual.columnLean * 10 - visual.collapse * 12,
      opacity: 0.88,
      collapseScale: 1 - visual.collapse * 0.55,
    },
    {
      key: 'p4',
      x: 608,
      y: 194 + visual.groundShift * 14,
      width: 30,
      height: 114,
      rotate: visual.columnLean * 6,
      opacity: 0.84,
      collapseScale: 1 - visual.collapse * 0.18,
    },
  ]

  const dustPuffs = Array.from({ length: 8 }).map((_, index) => ({
    key: `dust-${index}`,
    x: 420 + index * 18,
    y: 296 - index * 2,
    scale: 0.5 + index * 0.18,
    delay: index * 0.12,
  }))

  return (
    <div
      className={`relative overflow-hidden rounded-[2rem] border border-line bg-[linear-gradient(180deg,rgba(16,26,42,0.98),rgba(9,15,24,0.98))] shadow-glow ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_80%_18%,rgba(125,211,252,0.14),transparent_24%),radial-gradient(circle_at_18%_0%,rgba(255,156,105,0.08),transparent_26%)]" />
      <div className="relative flex flex-col gap-4 border-b border-line px-5 py-5 sm:px-7">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-2xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.34em] text-seismic/75">
              synchronized bridge state
            </p>
            <h3 className="mt-3 font-display text-2xl font-semibold tracking-[-0.04em] text-ink">
              {title}
            </h3>
            <p className="mt-3 text-sm leading-7 text-muted">
              {caption ??
                'The bridge responds directly to the current dashboard mode and state. Intrinsic mode shifts baseline distress, event mode raises hazard-driven damage, and prioritization adds urgency without faking structural collapse.'}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full border border-line bg-white/6 px-3 py-2 font-mono text-[11px] uppercase tracking-[0.24em] text-muted">
              {assessment.mode}
            </span>
            <span className="rounded-full border border-seismic/20 bg-seismic/10 px-3 py-2 font-mono text-[11px] uppercase tracking-[0.24em] text-seismic">
              {assessment.stageLabel}
            </span>
            <span className="rounded-full border border-line bg-white/6 px-3 py-2 font-mono text-[11px] uppercase tracking-[0.24em] text-muted">
              score {number(assessment.headlineScore)}
            </span>
          </div>
        </div>
      </div>

      <div className="relative px-4 pb-5 pt-3 sm:px-6">
        <svg viewBox="0 0 760 420" className="w-full">
          <defs>
            <linearGradient id="deckFill" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ecf4ff" stopOpacity="0.92" />
              <stop offset="55%" stopColor="#7dd3fc" stopOpacity="0.82" />
              <stop offset="100%" stopColor="#ff9c69" stopOpacity={0.25 + visual.emergencyTint * 0.4} />
            </linearGradient>
            <linearGradient id="pierFill" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#d7e5f5" stopOpacity="0.92" />
              <stop offset="100%" stopColor="#6d7e93" stopOpacity="0.88" />
            </linearGradient>
            <radialGradient id="dustFill" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(255,216,186,0.9)" />
              <stop offset="100%" stopColor="rgba(255,156,105,0)" />
            </radialGradient>
          </defs>

          <motion.g
            animate={
              reducedMotion
                ? { x: 0, y: 0 }
                : {
                    x: [0, visual.waveAmp * 2.2, 0, -visual.waveAmp * 1.6, 0],
                    y: [0, -visual.waveAmp * 2.4, 0, visual.waveAmp * 1.4, 0],
                  }
            }
            transition={
              reducedMotion
                ? { duration: 0.2 }
                : {
                    duration: ambientDuration,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }
            }
          >
            {Array.from({ length: 5 }).map((_, index) => (
              <motion.path
                key={`wave-${index}`}
                d={`M ${72 - index * 24} ${84 + index * 26} C ${208 - index * 6} ${30 + index * 8}, ${420 + index * 4} ${54 + index * 10}, ${676 + index * 18} ${132 + index * 8}`}
                fill="none"
                stroke="rgba(125,211,252,0.6)"
                strokeWidth={1.6 - index * 0.16}
                strokeDasharray="6 12"
                strokeOpacity={waveOpacity - index * 0.08}
                animate={
                  reducedMotion
                    ? { pathLength: 1 }
                    : { pathLength: [0.78, 1, 0.78], opacity: [waveOpacity, waveOpacity + 0.08, waveOpacity] }
                }
                transition={
                  reducedMotion
                    ? { duration: 0.2 }
                    : {
                        duration: 3.4 - visual.waveAmp * 1.2 + index * 0.18,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }
                }
              />
            ))}

            <motion.ellipse
              cx="384"
              cy="336"
              rx="280"
              ry={16 + visual.collapse * 8}
              fill="rgba(11,17,27,0.82)"
              animate={{ opacity: 0.48 + urgencyGlow, scaleX: 1 + visual.urgencyPulse * 0.03 }}
              transition={softSpring}
            />

            <motion.path
              d="M86 318 H682"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="10"
              strokeLinecap="round"
              animate={{ x: visual.groundShift * 10 }}
              transition={softSpring}
            />

            {piers.map((pier) => (
              <motion.rect
                key={pier.key}
                x={pier.x}
                y={pier.y}
                width={pier.width}
                height={pier.height}
                rx="14"
                fill="url(#pierFill)"
                stroke={`rgba(255,255,255,${0.2 + visual.fracture * 0.12})`}
                strokeWidth="1.5"
                opacity={pier.opacity}
                transform={`rotate(${pier.rotate} ${pier.x + pier.width / 2} ${pier.y + pier.height / 2})`}
                animate={{
                  y: pier.y,
                  scaleY: pier.collapseScale,
                }}
                transition={softSpring}
              />
            ))}

            <motion.path
              d={`M88 ${deckBaseline + 2} C 214 ${deckBaseline - 42}, 300 ${deckBaseline - 48}, 392 ${deckBaseline - 4} S 578 ${deckBaseline + 36}, 676 ${deckBaseline + 12}`}
              fill="none"
              stroke="rgba(73,182,255,0.22)"
              strokeWidth="12"
              strokeLinecap="round"
              animate={{ opacity: 0.18 + visual.waveAmp * 0.3 }}
              transition={softSpring}
            />

            {segments.map((segment) => (
              <motion.rect
                key={segment.key}
                x={segment.x}
                y={segment.y + segment.drop}
                width={segment.width}
                height="28"
                rx="12"
                fill="url(#deckFill)"
                stroke={`rgba(255,255,255,${0.18 + visual.fracture * 0.12})`}
                strokeWidth="1.2"
                transform={`rotate(${segment.rotate} ${segment.x + segment.width / 2} ${segment.y + segment.drop + 14})`}
                animate={{
                  x: segment.x,
                  y: segment.y + segment.drop,
                  rotate: segment.rotate,
                }}
                transition={softSpring}
              />
            ))}

            <motion.path
              d={`M92 ${deckBaseline + 12} H674`}
              stroke={`rgba(236,244,255,${0.68 - visual.collapse * 0.18})`}
              strokeWidth="4"
              strokeLinecap="round"
              animate={{ opacity: 0.72 - visual.collapse * 0.3 }}
              transition={softSpring}
            />

            <motion.path
              d={`M373 ${deckBaseline - 20} L366 ${deckBaseline + 8} L382 ${deckBaseline + 20} L370 ${deckBaseline + 46}`}
              fill="none"
              stroke="#ff9c69"
              strokeWidth="4.2"
              strokeLinecap="round"
              strokeOpacity={fractureOpacity}
              animate={{ opacity: fractureOpacity }}
              transition={softSpring}
            />
            <motion.path
              d={`M404 ${deckBaseline - 8} L392 ${deckBaseline + 16} L406 ${deckBaseline + 34}`}
              fill="none"
              stroke="#f97373"
              strokeWidth="3.6"
              strokeLinecap="round"
              strokeOpacity={fractureOpacity * 0.85}
              animate={{ opacity: fractureOpacity * 0.85 }}
              transition={softSpring}
            />

            {visual.stage >= 3 && (
              <>
                <motion.path
                  d={`M304 ${deckBaseline + 14} L292 ${deckBaseline + 44}`}
                  stroke="#ffb35f"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  animate={{ opacity: 0.35 + visual.fracture * 0.4 }}
                  transition={softSpring}
                />
                <motion.path
                  d={`M476 ${deckBaseline + 10} L486 ${deckBaseline + 38}`}
                  stroke="#ffb35f"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  animate={{ opacity: 0.35 + visual.fracture * 0.4 }}
                  transition={softSpring}
                />
              </>
            )}

            {dustPuffs.map((puff) => (
              <motion.circle
                key={puff.key}
                cx={puff.x}
                cy={puff.y}
                r={14}
                fill="url(#dustFill)"
                initial={false}
                animate={
                  reducedMotion
                    ? { opacity: visual.dust * 0.2, scale: 0.6 + visual.dust * puff.scale }
                    : {
                        opacity: [0, visual.dust * 0.2, 0],
                        scale: [0.4, 0.8 + visual.dust * puff.scale, 1.2 + visual.dust * puff.scale],
                        y: [0, -8 - puff.scale * 4, -14 - puff.scale * 6],
                      }
                }
                transition={{
                  duration: reducedMotion ? 0.2 : 2.8 + puff.delay,
                  repeat: reducedMotion ? 0 : Infinity,
                  repeatDelay: reducedMotion ? 0 : 0.4,
                  delay: puff.delay,
                  ease: 'easeOut',
                }}
              />
            ))}
          </motion.g>
        </svg>

        <div className="mt-4 grid gap-3 lg:grid-cols-[0.7fr_0.3fr]">
          <div className="rounded-[1.4rem] border border-line bg-white/5 px-4 py-4 text-sm leading-6 text-muted">
            {stageNotes[visual.stage]}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-[1.4rem] border border-line bg-white/5 px-3 py-3">
              <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
                structural
              </p>
              <p className="mt-2 font-display text-2xl text-ink">{number(visual.structuralSeverity)}</p>
            </div>
            <div className="rounded-[1.4rem] border border-line bg-white/5 px-3 py-3">
              <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
                urgency
              </p>
              <p className="mt-2 font-display text-2xl text-ink">{number(visual.urgencyPulse)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
