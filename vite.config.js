import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    outDir: resolve(import.meta.dirname, 'static/dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(import.meta.dirname, 'frontend/main.js'),
      output: {
        entryFileNames: 'main.js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
        format: 'es'
      }
    }
  }
});
