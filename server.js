import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';

const root = process.cwd();
const dataDir = join(root, 'data');
const dataFile = join(dataDir, 'invoices.json');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8' };
const seed = { clients: [{ id: 'lucia-leon', name: 'Lucia Leon', email: 'lucia@studioleo.com' }], invoices: [] };
async function database() { await mkdir(dataDir, { recursive: true }); if (!existsSync(dataFile)) await writeFile(dataFile, JSON.stringify(seed, null, 2)); return JSON.parse(await readFile(dataFile, 'utf8')); }
async function save(data) { await writeFile(dataFile, JSON.stringify(data, null, 2)); }
function reply(res, status, payload) { res.writeHead(status, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(payload)); }
function readBody(req) { return new Promise((resolve, reject) => { let body = ''; req.on('data', c => body += c); req.on('end', () => { try { resolve(JSON.parse(body || '{}')); } catch { reject(new Error('Invalid JSON')); } }); }); }
function cleanInvoice(input) { const items = Array.isArray(input.items) ? input.items.map(i => ({ description: String(i.description || '').trim(), quantity: Number(i.quantity) || 0, rate: Number(i.rate) || 0 })).filter(i => i.description && i.quantity > 0) : []; const subtotal = items.reduce((total, i) => total + i.quantity * i.rate, 0); return { clientName: String(input.clientName || '').trim(), clientEmail: String(input.clientEmail || '').trim(), issueDate: input.issueDate, dueDate: input.dueDate, terms: String(input.terms || 'Due in 14 days'), notes: String(input.notes || ''), termsText: String(input.termsText || ''), items, subtotal, total: subtotal }; }
const server = createServer(async (req, res) => { try {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === '/api/health') return reply(res, 200, { ok: true });
  if (url.pathname === '/api/invoices' && req.method === 'GET') { const db = await database(); return reply(res, 200, db.invoices); }
  if (url.pathname === '/api/invoices' && req.method === 'POST') { const invoice = cleanInvoice(await readBody(req)); if (!invoice.clientName || !invoice.clientEmail || !invoice.dueDate || !invoice.items.length) return reply(res, 422, { error: 'Client details, due date, and at least one item are required.' }); const db = await database(); const record = { ...invoice, id: crypto.randomUUID(), number: `INV-${new Date().getFullYear()}-${String(db.invoices.length + 1).padStart(3, '0')}`, status: 'sent', createdAt: new Date().toISOString() }; db.invoices.unshift(record); await save(db); return reply(res, 201, record); }
  const match = url.pathname.match(/^\/api\/invoices\/([^/]+)\/status$/);
  if (match && req.method === 'PATCH') { const { status } = await readBody(req); if (!['draft', 'sent', 'paid', 'overdue'].includes(status)) return reply(res, 422, { error: 'Invalid status.' }); const db = await database(); const invoice = db.invoices.find(i => i.id === match[1]); if (!invoice) return reply(res, 404, { error: 'Invoice not found.' }); invoice.status = status; await save(db); return reply(res, 200, invoice); }
  const file = url.pathname === '/' ? 'index.html' : normalize(url.pathname).replace(/^([.][.][\\/])+/,''); const full = join(root, file); if (!full.startsWith(root) || !existsSync(full)) { res.writeHead(404); return res.end('Not found'); } res.writeHead(200, { 'Content-Type': types[extname(full)] || 'application/octet-stream' }); res.end(await readFile(full));
} catch (error) { reply(res, 500, { error: error.message || 'Server error' }); } });
server.listen(process.env.PORT || 3000, () => console.log('Vanta is running at http://localhost:3000'));
