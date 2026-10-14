import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',        // 新增：监听所有网卡，允许外部设备访问
    port: 5173,
    strictPort: true,       // 新增：端口被占用时直接报错，而不是悄悄换成5174
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
