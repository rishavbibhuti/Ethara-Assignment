/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef4ff',
          100: '#d9e6ff',
          500: '#3b6ff6',
          600: '#2f5fe0',
          700: '#264dbb',
        },
      },
    },
  },
  plugins: [],
}
