import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  base: './',
  server: {
    host: true,
    port: 9988
  },
  preview: {
    host: true,
    port: 9988
  }
});
