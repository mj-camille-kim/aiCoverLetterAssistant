import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  root: 'app',
  server: {
    port: 5173,
    proxy: {
      // 백엔드 API만 프록시 (프론트 소스 app/api/analyze.js는 Vite가 서빙하도록 제외)
      '/api/auth': 'http://localhost:3000',
      '/api/getUserExp': 'http://localhost:3000',
      '/api/insertExp': 'http://localhost:3000',
      '/api/userExp': 'http://localhost:3000'
    }
  }
});