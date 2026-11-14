/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        page: '#0a0a0b',
        card: '#111113',
        cardBorder: '#222226',
        cardHover: '#161619',
        brand: {
          DEFAULT: '#ff6a1a',
          hover: '#e55a10',
          muted: '#ff6a1a20',
          glow: '#ff6a1a40'
        },
        safe: {
          DEFAULT: '#2ee6a6',
          bg: '#2ee6a615',
          border: '#2ee6a630'
        },
        caution: {
          DEFAULT: '#f59e0b',
          bg: '#f59e0b15',
          border: '#f59e0b30'
        },
        toxic: {
          DEFAULT: '#ef4444',
          bg: '#ef444415',
          border: '#ef444430'
        },
        muted: '#8a8a93',
        subtle: '#2a2a2f'
      },
      fontFamily: {
        sans: ['"Space Grotesk"', '"Outfit"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      }
    },
  },
  plugins: [],
}

