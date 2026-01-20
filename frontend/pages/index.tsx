import React, { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResponse('');
    
    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const reader = res.body?.getReader();
      if (!reader) return;
      
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'response') {
              setResponse(data.content);
            }
          }
        }
      }
    } catch (error) {
      setResponse(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 40, maxWidth: 800, margin: '0 auto' }}>
      <h1>Reality Transformer</h1>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query..."
          style={{ width: '100%', padding: 12, fontSize: 16 }}
        />
        <button type="submit" disabled={loading} style={{ marginTop: 12, padding: 12 }}>
          {loading ? 'Processing...' : 'Run'}
        </button>
      </form>

      {response && (
        <pre style={{ background: '#f5f5f5', padding: 16, marginTop: 20 }}>
          {response}
        </pre>
      )}
    </div>
  );
}