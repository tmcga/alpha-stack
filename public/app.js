/* Alpha Stack web app — fetches tool registry from /api, renders forms, runs tools. */

let TOOLS = {};
let CATEGORIES = [];
let currentToolKey = null;
let lastResult = null;

const $ = (id) => document.getElementById(id);
const toast = (msg, ms = 2200) => {
  const t = $('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), ms);
};

// ── Bootstrap ───────────────────────────────────────────────────────────
async function init() {
  try {
    const res = await fetch('/api/tools');
    const data = await res.json();
    CATEGORIES = data.categories;
    // flatten + keep category info
    const grouped = data.tools;
    TOOLS = {};
    for (const cat of CATEGORIES) {
      if (!grouped[cat]) continue;
      for (const tool of grouped[cat]) {
        TOOLS[tool.key] = { ...tool, category: cat };
      }
    }
    renderSidebar();
    const params = new URLSearchParams(location.search);
    const initial = params.get('tool');
    if (initial && TOOLS[initial]) selectTool(initial, params);
  } catch (err) {
    $('sidebar').innerHTML = `<div style="padding: 20px; color: var(--red); font-size: 13px;">
      API unreachable.<br><span style="color: var(--text-mute); font-size: 11px;">${err.message}</span>
    </div>`;
  }
}

function renderSidebar() {
  const sb = $('sidebar');
  sb.innerHTML = '';
  const byCat = {};
  for (const key in TOOLS) {
    const t = TOOLS[key];
    if (!byCat[t.category]) byCat[t.category] = [];
    byCat[t.category].push({ key, ...t });
  }
  for (const cat of CATEGORIES) {
    if (!byCat[cat]) continue;
    const label = document.createElement('div');
    label.className = 'cat-label';
    label.textContent = cat;
    sb.appendChild(label);
    for (const tool of byCat[cat]) {
      const item = document.createElement('div');
      item.className = 'tool-item';
      item.dataset.key = tool.key;
      item.textContent = tool.name;
      item.onclick = () => selectTool(tool.key);
      sb.appendChild(item);
    }
  }
}

// ── Select / render ─────────────────────────────────────────────────────
function selectTool(key, urlParams = null) {
  if (!TOOLS[key]) return;
  currentToolKey = key;
  document.querySelectorAll('.tool-item').forEach((el) => {
    el.classList.toggle('active', el.dataset.key === key);
  });
  const tool = TOOLS[key];
  const params = tool.params;

  const main = $('main');
  main.innerHTML = `
    <h2>${tool.name}</h2>
    <div class="tool-desc">${describe(tool)}</div>

    <form id="param-form" class="form-grid"></form>

    <div class="actions">
      <button class="btn-sm primary" id="btn-run">Run</button>
      <button class="btn-sm" id="btn-example">Use example</button>
      <button class="btn-sm" id="btn-clear">Clear</button>
      <button class="btn-sm" id="btn-share" disabled>Share link</button>
      <button class="btn-sm" id="btn-copy" disabled>Copy result</button>
      <button class="btn-sm" id="btn-csv" disabled>Download CSV</button>
    </div>

    <div id="result-area"></div>
  `;

  const form = $('param-form');
  for (const p of params) {
    const grp = document.createElement('div');
    grp.className = 'form-group';
    grp.innerHTML = `
      <label for="p-${p.name}">${p.label}${p.required ? '<span class="req">*</span>' : ''}</label>
      <input id="p-${p.name}" name="${p.name}" type="text"
             placeholder="${p.hint || ''}"
             data-type="${p.type}"
             data-default="${p.default ?? ''}">
      ${p.hint ? `<div class="hint">Example: ${escapeHtml(p.hint)}</div>` : ''}
    `;
    form.appendChild(grp);
  }

  $('btn-run').onclick = runTool;
  $('btn-example').onclick = fillExample;
  $('btn-clear').onclick = clearForm;
  $('btn-share').onclick = shareLink;
  $('btn-copy').onclick = copyResult;
  $('btn-csv').onclick = downloadCsv;

  // Pre-fill from URL params if provided
  if (urlParams) {
    for (const p of params) {
      const v = urlParams.get(p.name);
      if (v !== null) $(`p-${p.name}`).value = v;
    }
    // Auto-run if any params provided
    const hasAny = params.some((p) => urlParams.has(p.name));
    if (hasAny) setTimeout(runTool, 50);
  }

  // Update URL without param noise
  if (!urlParams) {
    const newUrl = new URL(location);
    newUrl.search = `?tool=${encodeURIComponent(key)}`;
    history.replaceState(null, '', newUrl);
  }
}

function describe(tool) {
  const required = tool.params.filter((p) => p.required).length;
  const optional = tool.params.length - required;
  return `${required} required input${required === 1 ? '' : 's'}${optional ? `, ${optional} optional` : ''}.`;
}

function fillExample() {
  for (const p of TOOLS[currentToolKey].params) {
    const el = $(`p-${p.name}`);
    if (!el.value && p.hint) el.value = p.hint;
    else if (!el.value && p.default !== null && p.default !== undefined && p.default !== '') {
      el.value = p.default;
    }
  }
  toast('Example values filled — adjust and run');
}

function clearForm() {
  document.querySelectorAll('#param-form input').forEach((el) => (el.value = ''));
  $('result-area').innerHTML = '';
  lastResult = null;
  ['btn-share', 'btn-copy', 'btn-csv'].forEach((id) => ($(id).disabled = true));
}

// ── Run ─────────────────────────────────────────────────────────────────
async function runTool() {
  const tool = TOOLS[currentToolKey];
  const payload = {};
  const inputState = {};
  for (const p of tool.params) {
    const raw = $(`p-${p.name}`).value.trim();
    if (!raw) {
      if (p.required) {
        showError(`Missing required input: ${p.label}`);
        return;
      }
      continue;
    }
    inputState[p.name] = raw;
    payload[p.name] = coerce(raw, p.type);
  }

  const btn = $('btn-run');
  btn.disabled = true;
  btn.textContent = 'Running…';
  $('result-area').innerHTML = '';

  try {
    const res = await fetch(`/api/tools/${encodeURIComponent(currentToolKey)}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!data.ok) {
      showError(data.error || 'Unknown error');
    } else {
      lastResult = { tool: tool.name, inputs: inputState, result: data.result };
      renderResult(data.result, tool);
      ['btn-share', 'btn-copy', 'btn-csv'].forEach((id) => ($(id).disabled = false));
      // Encode inputs in URL for sharing
      const url = new URL(location);
      url.search = '';
      url.searchParams.set('tool', currentToolKey);
      for (const [k, v] of Object.entries(inputState)) url.searchParams.set(k, v);
      history.replaceState(null, '', url);
    }
  } catch (err) {
    showError(`Network error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Run';
  }
}

function coerce(raw, type) {
  if (type === 'float') return parseFloat(raw);
  if (type === 'int') return parseInt(raw, 10);
  if (type === 'list[float]') return raw.split(',').map((s) => parseFloat(s.trim()));
  if (type === 'list[list[float]]') return JSON.parse(raw);
  return raw;
}

function showError(msg) {
  $('result-area').innerHTML = `<div class="error-card">${escapeHtml(msg)}</div>`;
}

// ── Result rendering ────────────────────────────────────────────────────
function renderResult(result, tool) {
  const area = $('result-area');
  const card = document.createElement('div');
  card.className = 'result-card';
  card.innerHTML = `
    <div class="result-header">
      <h3>${tool.name} — Result</h3>
      <div class="meta">${new Date().toLocaleString()}</div>
    </div>
  `;

  if (result === null || result === undefined) {
    card.innerHTML += '<div class="result-raw">(no output)</div>';
    area.appendChild(card);
    return;
  }

  if (typeof result !== 'object' || Array.isArray(result)) {
    card.innerHTML += `<div class="result-raw">${escapeHtml(stringify(result))}</div>`;
    area.appendChild(card);
    return;
  }

  // Separate scalar fields from nested
  const scalars = {};
  const nested = {};
  for (const [k, v] of Object.entries(result)) {
    if (v === null || typeof v !== 'object') scalars[k] = v;
    else nested[k] = v;
  }

  // Render scalars as kv-grid (top 6 most likely headline metrics)
  const scalarEntries = Object.entries(scalars);
  if (scalarEntries.length) {
    const grid = document.createElement('div');
    grid.className = 'kv-grid';
    for (const [k, v] of scalarEntries) {
      const kv = document.createElement('div');
      kv.className = 'kv';
      kv.innerHTML = `
        <div class="label">${prettyKey(k)}</div>
        <div class="value ${valueClass(k, v)}">${formatValue(k, v)}</div>
      `;
      grid.appendChild(kv);
    }
    card.appendChild(grid);
  }

  // Render nested objects/arrays as tables
  for (const [k, v] of Object.entries(nested)) {
    const heading = document.createElement('h4');
    heading.style.cssText = 'font-size:13px;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.06em;margin:16px 0 8px;';
    heading.textContent = prettyKey(k);
    card.appendChild(heading);
    card.appendChild(renderNested(v));
  }

  area.appendChild(card);
}

function renderNested(v) {
  if (Array.isArray(v)) {
    if (v.length === 0) return text('(empty)');
    if (typeof v[0] === 'object' && v[0] !== null) {
      // list of dicts → table
      const cols = Array.from(new Set(v.flatMap((row) => Object.keys(row))));
      const tbl = document.createElement('table');
      tbl.className = 'result-table';
      tbl.innerHTML = `
        <thead><tr>${cols.map((c) => `<th>${prettyKey(c)}</th>`).join('')}</tr></thead>
        <tbody>
          ${v.map((row) => `<tr>${cols.map((c) => `<td>${formatValue(c, row[c])}</td>`).join('')}</tr>`).join('')}
        </tbody>
      `;
      return tbl;
    }
    // primitive array
    return text(v.map((x) => formatValue('', x)).join(', '));
  }
  if (typeof v === 'object') {
    const tbl = document.createElement('table');
    tbl.className = 'result-table';
    tbl.innerHTML = `
      <tbody>
        ${Object.entries(v)
          .map(([k, val]) => {
            if (typeof val === 'object' && val !== null) {
              return `<tr><td>${prettyKey(k)}</td><td style="text-align:left;">${escapeHtml(stringify(val))}</td></tr>`;
            }
            return `<tr><td>${prettyKey(k)}</td><td>${formatValue(k, val)}</td></tr>`;
          })
          .join('')}
      </tbody>
    `;
    return tbl;
  }
  return text(String(v));
}

function text(s) {
  const div = document.createElement('div');
  div.className = 'result-raw';
  div.textContent = s;
  return div;
}

function prettyKey(k) {
  return String(k)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatValue(key, v) {
  if (v === null || v === undefined) return '—';
  if (typeof v === 'boolean') return v ? 'Yes' : 'No';
  if (typeof v === 'string') return escapeHtml(v);
  if (typeof v !== 'number') return escapeHtml(String(v));

  const k = key.toLowerCase();
  // Percentage-likely keys
  if (
    /\b(rate|yield|return|growth|margin|pct|percent|prob|irr|wacc|cap_rate|dscr|ltv|tax)\b/.test(k) &&
    Math.abs(v) < 5
  ) {
    return (v * 100).toFixed(2) + '%';
  }
  // Multiple-likely keys (don't add x to plain "shares")
  if (/(multiple|moic|tvpi|dpi|rvpi|ratio)$/.test(k) || k === 'beta') {
    return v.toFixed(2) + 'x';
  }
  // Large currency
  if (Math.abs(v) >= 1e9) return '$' + (v / 1e9).toFixed(2) + 'B';
  if (Math.abs(v) >= 1e6) return '$' + (v / 1e6).toFixed(2) + 'M';
  if (Math.abs(v) >= 1e4) return v.toLocaleString(undefined, { maximumFractionDigits: 0 });
  // Small numbers — show decimals
  if (Math.abs(v) < 1) return v.toFixed(4);
  return v.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function valueClass(key, v) {
  if (typeof v !== 'number') return '';
  const k = key.toLowerCase();
  if (/(irr|return|alpha|excess|profit|gain)/.test(k)) return v > 0 ? 'positive' : v < 0 ? 'negative' : '';
  return '';
}

function stringify(v) {
  try {
    return JSON.stringify(v, null, 2);
  } catch {
    return String(v);
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Share / Copy / CSV ──────────────────────────────────────────────────
function shareLink() {
  navigator.clipboard.writeText(location.href);
  toast('Link copied to clipboard');
}

function copyResult() {
  if (!lastResult) return;
  const text = `${lastResult.tool}\n\nInputs:\n${JSON.stringify(lastResult.inputs, null, 2)}\n\nResult:\n${JSON.stringify(lastResult.result, null, 2)}`;
  navigator.clipboard.writeText(text);
  toast('Result copied to clipboard');
}

function downloadCsv() {
  if (!lastResult) return;
  const rows = [['Field', 'Value']];
  rows.push(['Tool', lastResult.tool]);
  rows.push(['Generated', new Date().toISOString()]);
  rows.push(['', '']);
  rows.push(['INPUTS', '']);
  for (const [k, v] of Object.entries(lastResult.inputs)) rows.push([k, String(v)]);
  rows.push(['', '']);
  rows.push(['RESULTS', '']);
  flattenForCsv(lastResult.result, '', rows);
  const csv = rows.map((r) => r.map(csvEscape).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${currentToolKey}-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function flattenForCsv(obj, prefix, rows) {
  if (obj === null || obj === undefined) return rows.push([prefix, '']);
  if (typeof obj !== 'object') return rows.push([prefix, String(obj)]);
  if (Array.isArray(obj)) {
    obj.forEach((v, i) => flattenForCsv(v, `${prefix}[${i}]`, rows));
    return;
  }
  for (const [k, v] of Object.entries(obj)) {
    flattenForCsv(v, prefix ? `${prefix}.${k}` : k, rows);
  }
}

function csvEscape(s) {
  s = String(s ?? '');
  if (s.includes(',') || s.includes('"') || s.includes('\n')) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}

init();
