import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { query } = req.body;

  if (!query) {
    return res.status(400).json({ error: 'Query is required' });
  }

  try {
    // Call Rust inference service
    const inferenceResponse = await fetch('http://localhost:8080/infer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        evidence: [
          { name: 'Consciousness', value: 0.8, confidence: 0.9 },
          { name: 'Maya', value: 0.3, confidence: 0.7 }
        ],
        targets: ['Karma', 'Grace', 'Transformation']
      }),
    });

    if (!inferenceResponse.ok) {
      throw new Error(`Inference service error: ${inferenceResponse.status}`);
    }

    const data = await inferenceResponse.json();

    // Stream response back to frontend
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Send metadata
    res.write(`data: ${JSON.stringify({
      type: 'metadata',
      processing_time_ms: data.processing_time_ms
    })}\n\n`);

    // Send results
    res.write(`data: ${JSON.stringify({
      type: 'response',
      content: JSON.stringify(data.posteriors, null, 2)
    })}\n\n`);

    // Send done signal
    res.write(`data: ${JSON.stringify({ type: 'done' })}\n\n`);

    res.end();
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ 
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
  }
}