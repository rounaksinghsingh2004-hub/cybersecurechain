import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            '/api': 'http://localhost:8000',
            '/ws': { target: 'ws://localhost:8000', ws: true }
        }
    },
    build: {
        cssMinify: false
    },
    define: {
        'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '')
    }
});
