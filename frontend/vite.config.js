import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
  server: {
    proxy: {
      '/api': { target: 'http://web:8000', changeOrigin: true },
      '/ws':  { target: 'ws://web:8000',   ws: true }
    }
  },
  build: { outDir: 'dist', sourcemap: false }
})
