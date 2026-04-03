/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        fresh: '#22c55e',
        rotten: '#ef4444',
        soil: '#1a1208',
        leaf: '#16a34a',
        bark: '#92400e',
        cream: '#fef9f0',
        moss: '#14532d',
      },
    },
  },
  plugins: [],
}
