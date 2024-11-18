/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        point: {
          1: '#005AA9',
          2: '#005AA9CC',
          3: '#0075C9',
        },
        primary: '#000',
        secondary: '#929292',
      },
    },
  },
  plugins: [],
};
