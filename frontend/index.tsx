import { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState({ ttft: 0, total: 0, tokens: 0 });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');
    
    const startTime = Date.now();
    let firstTokenTime = 0;

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let result = '';

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.type === 'metadata') {
              if (!firstTokenTime) firstTokenTime = Date.now() - startTime;
              setMetrics({ 
                ttft: firstTokenTime, 
                total: data.processing_time_ms,
                tokens: 0 
              });
            }

            if (data.type === 'response') {
              result += data.content;
              setResponse(result);
            }
          }
        }
      }

      const totalTime = Date.now() - startTime;
      setMetrics(m => ({ ...m, total: totalTime }));
    } catch (error) {
      setResponse(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto', fontFamily: 'monospace', background: '#1e1e1e', color: '#d4d4d4', minHeight: '100vh' }}>
      <h1 style={{ color: '#4ec9b0' }}>Reality Transformer</h1>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query..."
          style={{ 
            width: '100%', 
            padding: '12px', 
            fontSize: '16px', 
            background: '#252526',
            border: '1px solid #3e3e42',
            color: '#d4d4d4',
            borderRadius: '4px'
          }}
        />
        <button 
          type="submit" 
          disabled={loading}
          style={{ 
            marginTop: '12px', 
            padding: '12px 24px', 
            fontSize: '16px',
            background: '#0e639c',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Processing...' : 'Run'}
        </button>
      </form>

      {metrics.ttft > 0 && (
        <div style={{ marginTop: '20px', padding: '12px', background: '#252526', borderRadius: '4px' }}>
          <strong>Metrics:</strong> TTFT: {metrics.ttft}ms | Total: {metrics.total}ms
        </div>
      )}

      {response && (
        <div style={{ marginTop: '20px' }}>
          <strong style={{ color: '#4ec9b0' }}>Response:</strong>
          <pre style={{ 
            background: '#252526', 
            padding: '16px', 
            borderRadius: '4px',
            overflow: 'auto',
            marginTop: '8px'
          }}>
            {response}
          </pre>
        </div>
      )}
    </div>
  );
}