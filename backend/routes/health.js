// backend/routes/health.js
const express = require('express');
const router = express.Router();
const { query } = require('../db');

// GET /health/db
router.get('/db', async (req, res) => {
  try {
    // cheap query to verify DB connectivity
    const r = await query('SELECT 1 AS ok');
    if (r && r.rowCount === 1) return res.json({ ok: true, db: 'reachable' });
    return res.status(500).json({ ok: false, db: 'unexpected response' });
  } catch (err) {
    console.error('DB health check failed:', err);
    return res.status(500).json({ ok: false, error: err.message });
  }
});

module.exports = router;
