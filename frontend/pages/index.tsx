import React, { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [webSearchData, setWebSearchData] = useState(true);
  const [webSearchInsights, setWebSearchInsights] = useState(true);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResponse('');

    const params = new URLSearchParams({
      prompt: query,
      web_search_data: webSearchData.toString(),
      web_search_insights: webSearchInsights.toString(),
    });

    try {
      const res = await fetch(`/api/run?${params.toString()}`, {
        method: 'GET',
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

        <div style={{ marginTop: 12, display: 'flex', gap: 24 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={webSearchData}
              onChange={(e) => setWebSearchData(e.target.checked)}
            />
            Get Data
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={webSearchInsights}
              onChange={(e) => setWebSearchInsights(e.target.checked)}
            />
            Mine Insights
          </label>
        </div>

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