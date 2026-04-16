/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#070b13',
        basin: '#0d1420',
        trench: '#111b2c',
        panel: '#101a2a',
        panelGlow: '#162338',
        ink: '#eff4fb',
        muted: '#9db0c8',
        line: 'rgba(173, 196, 223, 0.18)',
        grid: 'rgba(123, 159, 197, 0.12)',
        ocean: '#49b6ff',
        seismic: '#7dd3fc',
        ember: '#ff9c69',
        hazard: '#f97373',
        signal: '#ffd166',
        moss: '#66d1a6',
      },
      fontFamily: {
        sans: ['"Manrope"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', '"Manrope"', 'ui-sans-serif', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        panel: '0 24px 80px rgba(0, 0, 0, 0.32)',
        float: '0 0 0 1px rgba(115, 149, 189, 0.12), 0 20px 50px rgba(5, 10, 18, 0.38)',
        glow: '0 0 0 1px rgba(125, 211, 252, 0.12), 0 0 80px rgba(73, 182, 255, 0.18)',
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.75rem',
      },
      backgroundImage: {
        grid: 'linear-gradient(rgba(123,159,197,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(123,159,197,0.12) 1px, transparent 1px)',
        seismic: 'radial-gradient(circle at center, rgba(73,182,255,0.14), transparent 55%)',
      },
    },
  },
  plugins: [],
}
