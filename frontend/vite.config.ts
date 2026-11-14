import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/health': 'http://127.0.0.1:8000',
      '/analyze': 'http://127.0.0.1:8000',
      '/rewrite': 'http://127.0.0.1:8000',
      '/conversations': 'http://127.0.0.1:8000',
      '/insights': 'http://127.0.0.1:8000',
      '/samples': 'http://127.0.0.1:8000',
      '/api': 'http://127.0.0.1:8000'
    }
  }
})

