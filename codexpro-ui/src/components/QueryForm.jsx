import React, { useState } from 'react';
import axios from 'axios';
import ChunkViewer from './ChunkViewer';

export default function QueryForm({ setResult }) {
  const [question, setQuestion] = useState('');
  const [chunks, setChunks] = useState([]);
  const [showChunks, setShowChunks] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setShowChunks(false); // reset visibility
    try {
      const res = await axios.post('http://localhost:8000/ask', { question });
      setResult(res.data); // in case you're also displaying a summary elsewhere
      setChunks(res.data.chunks); // assuming res.data is the list of chunks
    } catch (err) {
      console.error(err);
      alert('❌ Query failed');
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <h2>🤖 Ask a Question</h2>
        <input
          type="text"
          placeholder="e.g. What does generator file do?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          required
        />
        <button type="submit">Ask</button>
      </form>

      {chunks.length > 0 && (
        <button onClick={() => setShowChunks(!showChunks)} style={{ marginTop: '10px' }}>
          {showChunks ? 'Hide Chunks' : 'View Chunks'}
        </button>
      )}

      {showChunks && <ChunkViewer chunks={chunks} />}
    </>
  );
}
