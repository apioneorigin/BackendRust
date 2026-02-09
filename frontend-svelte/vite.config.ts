import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, ''),
				configure: (proxy, options) => {
					// Handle SSE streaming - disable buffering
					proxy.on('proxyRes', (proxyRes, req, res) => {
						// Check if this is an SSE response
						const contentType = proxyRes.headers['content-type'] || '';
						if (contentType.includes('text/event-stream')) {
							// Disable buffering for SSE
							proxyRes.headers['cache-control'] = 'no-cache, no-transform';
							proxyRes.headers['x-accel-buffering'] = 'no';
							// Ensure chunked transfer
							delete proxyRes.headers['content-length'];
						}
					});
					// Handle errors
					proxy.on('error', (err, req, res) => {
						console.error('Proxy error:', err);
					});
				}
			}
		}
	}
});
