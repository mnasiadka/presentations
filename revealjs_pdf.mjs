// Print a reveal.js deck to PDF with the locally installed Chrome, using
// the slide size from reveal.js's print stylesheet (16:9, no margins).
// No npm dependencies: talks to Chrome over the DevTools protocol.
//
// Usage: node revealjs_pdf.mjs <index.html> <out.pdf> [--steps]
//   --steps   one page per fragment (click), instead of one per slide

import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME = process.env.CHROME ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const [input, output, ...flags] = process.argv.slice(2);
if (!input || !output) {
  console.error('usage: node revealjs_pdf.mjs <index.html> <out.pdf> [--steps]');
  process.exit(2);
}
const steps = flags.includes('--steps');
const url = pathToFileURL(resolve(input)).href +
  `?print-pdf&pdfSeparateFragments=${steps}`;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run',
  '--remote-debugging-port=0',
  `--user-data-dir=${mkdtempSync(join(tmpdir(), 'revealjs-pdf-'))}`,
  'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });

// Chrome prints the DevTools websocket URL on stderr once it is ready.
const browserWs = await new Promise((res, rej) => {
  let buf = '';
  chrome.stderr.on('data', (d) => {
    buf += d;
    const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if (m) res(m[1]);
  });
  chrome.on('exit', (c) => rej(new Error(`chrome exited (${c})`)));
});

const port = new URL(browserWs).port;
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const page = targets.find((t) => t.type === 'page');

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let nextId = 0;
const pending = new Map();
ws.addEventListener('message', (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { res, rej } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
  }
});
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++nextId;
  pending.set(id, { res, rej });
  ws.send(JSON.stringify({ id, method, params }));
});

try {
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Page.navigate', { url });

  // Wait until reveal.js has laid out the print view.
  for (let i = 0; ; i++) {
    const { result } = await send('Runtime.evaluate', {
      expression: "document.querySelectorAll('.pdf-page').length",
    });
    if (result.value > 0) break;
    if (i > 100) throw new Error('reveal.js print layout did not appear');
    await sleep(200);
  }
  await sleep(1000);  // fonts and transitions settle

  const { data } = await send('Page.printToPDF', {
    preferCSSPageSize: true,
    printBackground: true,
    displayHeaderFooter: false,
  });
  writeFileSync(output, Buffer.from(data, 'base64'));
  console.log(`wrote ${output}`);
} finally {
  ws.close();
  chrome.kill();
}
