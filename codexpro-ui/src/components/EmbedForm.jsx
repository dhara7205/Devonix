import React, { useState } from 'react';
import axios from 'axios';

export default function EmbedForm({ onSuccess }) {
  const [folderPath, setFolderPath] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/embed', { folder_path: folderPath });
      alert('✅ Embedding successful');
      onSuccess();
    } catch (err) {
      console.error(err);
      alert('❌ Embedding failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>🔍 Embed Codebase</h2>
      <input
        type="text"
        placeholder="Enter folder path"
        value={folderPath}
        onChange={(e) => setFolderPath(e.target.value)}
        required
      />
      <button type="submit">Start Embedding</button>
    </form>
  );
}
