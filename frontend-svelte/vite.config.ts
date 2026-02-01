import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true,
				configure: (proxy) => {
					// Disable buffering for SSE streaming
					proxy.on('proxyRes', (proxyRes) => {
						// Prevent proxy from buffering the response
						proxyRes.headers['cache-control'] = 'no-cache';
						proxyRes.headers['x-accel-buffering'] = 'no';
					});
				}
			}
		}
	}
});
