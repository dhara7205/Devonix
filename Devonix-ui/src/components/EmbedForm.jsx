import React, { useState } from 'react';
import axios from 'axios';

export default function EmbedForm() {
  const [folderPath, setFolderPath] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/embed', { folder_path: folderPath });
      alert('✅ Embedding successful');
      setFolderPath('');
    } catch (err) {
      console.error(err);
      alert('❌ Embedding failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
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
