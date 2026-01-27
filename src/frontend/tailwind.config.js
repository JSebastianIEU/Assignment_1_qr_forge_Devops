import forms from '@tailwindcss/forms'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        accent: { 500: '#8b5cf6', 600: '#7c3aed' },
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      boxShadow: {
        glass: '0 12px 28px rgba(15, 23, 42, 0.14)',
        'glass-sm': '0 8px 18px rgba(15, 23, 42, 0.10)',
        'card-sm': '0 4px 12px rgba(15, 23, 42, 0.08)',
      },
      borderRadius: {
        glass: '16px',
        xl: '16px',
        '2xl': '20px',
      },
      blur: {
        glass: '16px',
        '2xl': '24px',
      },
      backdropBlur: {
        glass: '14px',
        '2xl': '22px',
      },
      container: {
        center: true,
        padding: {
          DEFAULT: '1.25rem',
          sm: '1.5rem',
          lg: '2rem',
          xl: '2.5rem',
        },
        screens: {
          '2xl': '1320px',
        },
      },
    },
  },
  plugins: [forms],
}
