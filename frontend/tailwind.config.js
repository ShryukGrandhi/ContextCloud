/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'glass': {
          '50': 'rgba(255, 255, 255, 0.1)',
          '100': 'rgba(255, 255, 255, 0.2)',
          '200': 'rgba(255, 255, 255, 0.3)',
        },
        'neon': {
          'blue': '#00d4ff',
          'purple': '#b347d9',
          'green': '#00ff88',
          'pink': '#ff6b9d',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.5)' },
          '100%': { boxShadow: '0 0 30px rgba(0, 212, 255, 0.8)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        }
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}
