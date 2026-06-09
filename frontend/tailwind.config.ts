import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#090B10',
        'ink-2': '#111827',
        panel: '#141A24',
        'panel-2': '#1E2633',
        gold: '#FBBF24',
        ember: '#F97316',
        danger: '#EF4444',
        success: '#22C55E'
      },
      boxShadow: {
        glow: '0 0 40px rgba(251, 191, 36, 0.18)'
      }
    }
  },
  plugins: []
}

export default config
