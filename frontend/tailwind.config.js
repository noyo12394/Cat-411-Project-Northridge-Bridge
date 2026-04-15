/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#f4f7fb',
        ink: '#102033',
        muted: '#5b6b80',
        line: '#d9e1ea',
        panel: '#ffffff',
        ocean: '#1f5fbf',
        sky: '#4ea3ff',
        teal: '#0f766e',
        violet: '#5664f5',
        signal: '#ffb547',
        danger: '#e15d50',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Sora"', '"Plus Jakarta Sans"', 'ui-sans-serif', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        panel: '0 20px 60px rgba(16, 32, 51, 0.08)',
        float: '0 18px 40px rgba(31, 95, 191, 0.14)',
        soft: '0 10px 30px rgba(16, 32, 51, 0.06)',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      backgroundImage: {
        grid: 'linear-gradient(rgba(31, 95, 191, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(31, 95, 191, 0.08) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
}
