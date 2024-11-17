import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import tailwindcss from 'tailwindcss';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      src: '/src',
      components: '/src/components',
      assets: '/src/assets',
      pages: '/src/pages',
      styles: '/src/styles',
      stores: '/src/stores',
    },
  },
  css: {
    postcss: {
      plugins: [tailwindcss()],
    },
  },
});
