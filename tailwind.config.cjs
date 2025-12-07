/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx,jsx,js}'],
  theme: {
    extend: {
      colors: {
        dukeBlue: '#012169',
        dukeLightBlue: '#4B9CD3',
      },
    },
  },
  plugins: [],
};
