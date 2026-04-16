export const revealTransition = {
  duration: 0.7,
  ease: [0.22, 1, 0.36, 1] as const,
}

export const softSpring = {
  type: 'spring' as const,
  stiffness: 120,
  damping: 18,
  mass: 0.8,
}
