import React, { useState } from 'react';
import EmbedForm from './components/EmbedForm';
import QueryForm from './components/QueryForm';
import ChunkViewer from './components/ChunkViewer';

function App() {
  const [mode, setMode] = useState(null); // null, 'embed', 'query'
  const [result, setResult] = useState(null);

  const handleBack = () => {
    setMode(null);
    setResult(null);
  };

  return (
    <div className="container p-4 text-center">
      <h1 className="mb-4">🧠 CodexPro Interface</h1>

      {mode === null && (
        <>
          <p className="mb-3">Select an option to get started:</p>
          <button onClick={() => setMode('embed')} className="me-2">Embed Code</button>
          <button onClick={() => setMode('query')}>Ask a Question</button>
        </>
      )}

      {mode === 'embed' && (
        <>
          <button onClick={handleBack} className="mb-3 float-start">⬅ Back</button>
          <EmbedForm onSuccess={() => setMode('query')} />
        </>
      )}

      {mode === 'query' && (
        <>
          <button onClick={handleBack} className="mb-3 float-start">⬅ Back</button>
          <QueryForm setResult={setResult} />
          {result && (
            <div className="mt-4 text-start">
              <h2 className="text-info">💬 Gemini Answer:</h2>
              <div className="answer-box">
                {result.answer}
              </div>
              {result.length > 0 && (
                <details className="mt-3">
                  <summary style={{ cursor: 'pointer' }}>📄 View Chunks</summary>
                  <ChunkViewer chunks={result} />
                </details>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
