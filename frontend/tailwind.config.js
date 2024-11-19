/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    screens: {
      mobile: '640px',
      tablet: '768px',
      desktop: '1024px',
    },
    extend: {
      width: {
        base: 'calc(100% - 2.5rem)',
        'base-mobile': 'calc(100% - 120px)',
      },
      maxWidth: {
        main: '768px',
      },
      colors: {
        point: {
          1: 'var(--color-point-1)',
          2: 'var(--color-point-2)',
          3: 'var(--color-point-3)',
        },
        primary: '#000',
        secondary: '#929292',
        third: '#F4F4F4',
      },
    },
  },
  plugins: [],
};
