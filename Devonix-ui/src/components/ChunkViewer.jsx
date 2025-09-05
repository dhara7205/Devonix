import React from 'react';

export default function ChunkViewer({ chunks }) {
  if (!chunks || chunks.length === 0) return null;

  return (
    <div>
      <h2>📚 Retrieved Chunks</h2>
      {chunks.map((chunk, idx) => (
        <pre key={idx} className='answer-box'>
          <strong>File:</strong> {chunk.rel_path || chunk.file} <br />
          <strong>Symbol:</strong> {chunk.qualified_name || chunk.name} <br />
          <strong>Score:</strong> {chunk.score?.toFixed(4)} <br />
          <code>{chunk.content}</code>
        </pre>
      ))}
    </div>
  );
}
