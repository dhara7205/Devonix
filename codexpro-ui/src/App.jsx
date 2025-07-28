import React, { useState } from 'react';
import EmbedForm from './components/EmbedForm';
import QueryForm from './components/QueryForm';
import ChunkViewer from './components/ChunkViewer';

function App() {
  const [mode, setMode] = useState(null); // null, 'embed', or 'query'
  const [result, setResult] = useState(null);

  const handleBack = () => {
    setMode(null);
    setResult(null);
  };

  return (
    <div style={{ padding: '30px', textAlign: 'center' }}>
      <h1>🧠 CodexPro Interface</h1>

      {mode === null && (
        <>
          <p>Select an option to get started:</p>
          <button onClick={() => setMode('embed')} style={{ margin: '10px' }}>Embed Code</button>
          <button onClick={() => setMode('query')} style={{ margin: '10px' }}>Ask a Question</button>
        </>
      )}

      {mode === 'embed' && (
        <>
          <button onClick={handleBack} style={{ float: 'left' }}>⬅ Back</button>
          <EmbedForm onSuccess={() => setMode('query')} />
        </>
      )}

      {mode === 'query' && (
        <>
          <button onClick={handleBack} style={{ float: 'left' }}>⬅ Back</button>
          <QueryForm setResult={setResult} />
          {result && (
            <div style={{ marginTop: '30px', textAlign: 'left' }}>
              <h2>💬 Gemini Answer:</h2>
              <p>{result.answer}</p>
              {result.length > 0 && <ChunkViewer chunks={result} />}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
