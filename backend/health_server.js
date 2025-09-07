// backend/health_server.js
require('dotenv').config();
const express = require('express');
const health = require('./routes/health');

const app = express();
app.use('/health', health);

const PORT = process.env.HEALTH_PORT || 5001;
app.listen(PORT, () => {
  console.log(`Health server listening on http://localhost:${PORT}/health/db`);
});
