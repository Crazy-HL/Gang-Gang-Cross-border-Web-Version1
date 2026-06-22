import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#F8FAFC',
        'ink-2': '#F1F5F9',
        panel: '#FFFFFF',
        'panel-2': '#E2E8F0',
        gold: '#3B82F6',
        ember: '#F97316',
        danger: '#FFEDD5',
        success: '#DBEAFE'
      },
      boxShadow: {
        glow: '0 18px 45px rgba(59, 130, 246, 0.18)'
      }
    }
  },
  plugins: []
}

export default config
