import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import basicSsl from '@vitejs/plugin-basic-ssl'
// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(),tailwindcss(),basicSsl()],
  server: {
    host: true ,// Memastikan web bisa diakses lewat WiFi
    proxy: {
      // Mengarahkan semua request '/api' ke backend FastAPI
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        secure: false // Abaikan error SSL antara Vite dan FastAPI
      }
    }
  }
})
