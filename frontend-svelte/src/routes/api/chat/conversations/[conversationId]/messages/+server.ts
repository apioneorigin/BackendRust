/**
 * SSE Proxy Endpoint for Chat Messages
 *
 * SvelteKit-native server endpoint that proxies SSE streams from the backend.
 * This eliminates the need for direct backend connections and works consistently
 * in both development and production environments.
 *
 * Benefits:
 * - No buffering issues (native streaming)
 * - Consistent behavior in dev/prod
 * - Auth via HttpOnly cookies (more secure)
 * - All requests go through SvelteKit
 */

import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export const POST: RequestHandler = async ({ request, params, cookies }) => {
	const { conversationId } = params;
	const token = cookies.get('auth_token');

	if (!token) {
		return new Response(JSON.stringify({ error: 'Unauthorized' }), {
			status: 401,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	// Parse request body
	let body;
	try {
		body = await request.json();
	} catch {
		return new Response(JSON.stringify({ error: 'Invalid request body' }), {
			status: 400,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	// Forward request to backend
	const backendResponse = await fetch(
		`${BACKEND_URL}/api/chat/conversations/${conversationId}/messages`,
		{
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${token}`
			},
			body: JSON.stringify(body)
		}
	);

	if (!backendResponse.ok) {
		const errorData = await backendResponse.text();
		return new Response(errorData, {
			status: backendResponse.status,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	// Check if response is SSE
	const contentType = backendResponse.headers.get('content-type') || '';

	if (contentType.includes('text/event-stream')) {
		// Stream SSE response directly
		const stream = backendResponse.body;

		if (!stream) {
			return new Response(JSON.stringify({ error: 'No response body' }), {
				status: 500,
				headers: { 'Content-Type': 'application/json' }
			});
		}

		// Return streaming response with proper SSE headers
		return new Response(stream, {
			status: 200,
			headers: {
				'Content-Type': 'text/event-stream',
				'Cache-Control': 'no-cache, no-transform',
				'Connection': 'keep-alive',
				'X-Accel-Buffering': 'no'
			}
		});
	}

	// Non-SSE response (fallback)
	const data = await backendResponse.text();
	return new Response(data, {
		status: backendResponse.status,
		headers: {
			'Content-Type': contentType || 'application/json'
		}
	});
};
