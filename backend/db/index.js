// backend/db/index.js
require('dotenv').config();
const { Pool } = require('pg');

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error('DATABASE_URL is not set in environment');
}

// Pool config — tune if needed for production
const pool = new Pool({
  connectionString,
  // optional: max, idleTimeoutMillis, connectionTimeoutMillis
  // max: 20,
  // idleTimeoutMillis: 30000,
  // connectionTimeoutMillis: 2000,
});

pool.on('error', (err) => {
  console.error('Unexpected idle client error', err);
  // optionally exit process in production
});

async function query(text, params) {
  const start = Date.now();
  const res = await pool.query(text, params);
  const duration = Date.now() - start;
  // small debug logging for dev
  console.debug('db query', { text, duration, rows: res.rowCount });
  return res;
}

module.exports = {
  pool,
  query
};
