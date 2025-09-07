// backend/db/test_db.js
require('dotenv').config();
const { query, pool } = require('./index');

async function main() {
  try {
    const res = await query('SELECT id, email, provider, display_name, created_at FROM users LIMIT 5');
    console.log('rows:', res.rows);
  } catch (err) {
    console.error('DB test failed:', err);
  } finally {
    // close pool so Node exits
    await pool.end();
  }
}

main();
