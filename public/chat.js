/* Alpha Stack chat — BYOK, streams Claude responses with tool-use visualization. */

const $ = (id) => document.getElementById(id);
const KEY_STORAGE = 'alpha_stack_key';
const MODEL_STORAGE = 'alpha_stack_model';
const HISTORY_STORAGE = 'alpha_stack_history';

let messages = []; // wire-format messages for the API
let busy = false;

const toast = (msg, ms = 2400) => {
  const t = $('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), ms);
};

// ── Init ───────────────────────────────────────────────────────────────
async function init() {
  // Restore key
  const savedKey = localStorage.getItem(KEY_STORAGE);
  if (savedKey) $('api-key').value = savedKey;

  // Load models
  try {
    const r = await fetch('/api/chat/models');
    const data = await r.json();
    const sel = $('model-select');
    sel.innerHTML = data.models
      .map((m) => `<option value="${m.id}">${m.name} — ${m.tagline}</option>`)
      .join('');
    const savedModel = localStorage.getItem(MODEL_STORAGE);
    if (savedModel) sel.value = savedModel;
    sel.onchange = () => localStorage.setItem(MODEL_STORAGE, sel.value);
  } catch {
    /* offline ok */
  }

  $('btn-save-key').onclick = saveKey;
  $('btn-clear-key').onclick = clearKey;
  $('btn-send').onclick = sendMessage;
  $('btn-new-chat').onclick = newChat;
  $('input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  document.querySelectorAll('.example-prompt').forEach((b) => {
    b.onclick = () => {
      $('input').value = b.dataset.prompt;
      $('input').focus();
    };
  });

  // Restore prior conversation if any
  try {
    const hist = JSON.parse(localStorage.getItem(HISTORY_STORAGE) || '[]');
    if (hist.length) {
      messages = hist;
      renderHistory();
    }
  } catch {
    /* ignore corrupted history */
  }
}

function saveKey() {
  const k = $('api-key').value.trim();
  if (!k) {
    localStorage.removeItem(KEY_STORAGE);
    toast('Key cleared');
    return;
  }
  if (!k.startsWith('sk-ant-')) {
    toast('Key must start with sk-ant-');
    return;
  }
  localStorage.setItem(KEY_STORAGE, k);
  toast('Key saved (in your browser only)');
}

function clearKey() {
  $('api-key').value = '';
  localStorage.removeItem(KEY_STORAGE);
  toast('Key cleared');
}

function newChat() {
  messages = [];
  localStorage.removeItem(HISTORY_STORAGE);
  $('messages').innerHTML = `
    <div class="welcome">
      <div class="welcome-icon">◆</div>
      <h2>New conversation.</h2>
      <p>Ask another question — the calculators are ready.</p>
    </div>
  `;
}

// ── Sending ────────────────────────────────────────────────────────────
async function sendMessage() {
  if (busy) return;
  const input = $('input');
  const text = input.value.trim();
  if (!text) return;
  const key = localStorage.getItem(KEY_STORAGE) || $('api-key').value.trim();
  if (!key) {
    toast('Add your Anthropic API key first (sidebar).');
    $('api-key').focus();
    return;
  }

  // Clear welcome panel
  const welcome = document.querySelector('.welcome');
  if (welcome) welcome.remove();

  input.value = '';
  busy = true;
  $('btn-send').disabled = true;
  $('btn-send').textContent = '…';

  // Render user message
  renderUserMessage(text);
  messages.push({ role: 'user', content: text });

  // Render assistant bubble that we'll stream into
  const bubble = renderAssistantBubble();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Anthropic-Key': key,
      },
      body: JSON.stringify({ messages, model: $('model-select').value }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      bubble.text.textContent = `Error: ${err.detail || res.statusText}`;
      bubble.text.classList.add('error');
      return;
    }

    await readSSE(res, bubble);
  } catch (err) {
    bubble.text.textContent = `Network error: ${err.message}`;
    bubble.text.classList.add('error');
  } finally {
    busy = false;
    $('btn-send').disabled = false;
    $('btn-send').textContent = 'Send ↵';
    localStorage.setItem(HISTORY_STORAGE, JSON.stringify(messages));
  }
}

async function readSSE(res, bubble) {
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let assistantText = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx;
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const chunk = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const line = chunk.split('\n').find((l) => l.startsWith('data: '));
      if (!line) continue;
      let event;
      try {
        event = JSON.parse(line.slice(6));
      } catch {
        continue;
      }
      handleEvent(event, bubble, (t) => {
        assistantText += t;
      });
      bubble.container.scrollIntoView({ block: 'end', behavior: 'smooth' });
    }
  }

  // After stream end, sync the assistant message into our history
  // (use the rendered text since we don't have the full content blocks on client)
  if (assistantText) {
    messages.push({ role: 'assistant', content: assistantText });
  } else {
    // Tool-call-only turn with no text — keep history consistent by leaving it out
  }
}

function handleEvent(event, bubble, addText) {
  if (event.type === 'text_delta') {
    bubble.text.textContent += event.text;
    addText(event.text);
  } else if (event.type === 'tool_use_start') {
    bubble.addToolCall(event.name);
  } else if (event.type === 'tool_result') {
    bubble.fillToolResult(event.name, event.input, event.result);
  } else if (event.type === 'error') {
    const e = document.createElement('div');
    e.className = 'tool-error';
    e.textContent = event.error;
    bubble.container.appendChild(e);
  } else if (event.type === 'turn_end') {
    if (event.usage) {
      const meta = document.createElement('div');
      meta.className = 'turn-meta';
      meta.textContent = `${event.usage.input_tokens} in / ${event.usage.output_tokens} out`;
      bubble.container.appendChild(meta);
    }
  }
}

// ── Rendering ──────────────────────────────────────────────────────────
function renderUserMessage(text) {
  const div = document.createElement('div');
  div.className = 'msg msg-user';
  div.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
  $('messages').appendChild(div);
}

function renderAssistantBubble() {
  const div = document.createElement('div');
  div.className = 'msg msg-assistant';
  div.innerHTML = `<div class="msg-bubble"><div class="assistant-text"></div></div>`;
  $('messages').appendChild(div);
  const text = div.querySelector('.assistant-text');
  const bubble = div.querySelector('.msg-bubble');
  const toolCalls = new Map(); // name → element

  return {
    container: div,
    text,
    addToolCall(name) {
      const key = displayName(name);
      const card = document.createElement('div');
      card.className = 'tool-call';
      card.innerHTML = `
        <div class="tool-call-header"><span class="tc-icon">◇</span> Running <strong>${key}</strong>…</div>
      `;
      bubble.insertBefore(card, text);
      toolCalls.set(name, card);
    },
    fillToolResult(name, input, result) {
      const card = toolCalls.get(name) || (() => {
        const c = document.createElement('div');
        c.className = 'tool-call';
        bubble.insertBefore(c, text);
        return c;
      })();
      const isError = result && typeof result === 'object' && 'error' in result;
      card.innerHTML = `
        <div class="tool-call-header ${isError ? 'tc-error' : 'tc-ok'}">
          <span class="tc-icon">${isError ? '✕' : '✓'}</span>
          <strong>${displayName(name)}</strong>
          <button class="tc-toggle" type="button">show details</button>
        </div>
        <div class="tool-call-body" style="display:none;">
          <div class="tc-section-label">Inputs</div>
          <pre class="tc-pre">${escapeHtml(JSON.stringify(input, null, 2))}</pre>
          <div class="tc-section-label">${isError ? 'Error' : 'Result'}</div>
          <pre class="tc-pre">${escapeHtml(JSON.stringify(result, null, 2))}</pre>
        </div>
      `;
      const toggle = card.querySelector('.tc-toggle');
      const body = card.querySelector('.tool-call-body');
      toggle.onclick = () => {
        const open = body.style.display === 'block';
        body.style.display = open ? 'none' : 'block';
        toggle.textContent = open ? 'show details' : 'hide details';
      };
    },
  };
}

function renderHistory() {
  $('messages').innerHTML = '';
  for (const m of messages) {
    if (m.role === 'user') {
      const c = typeof m.content === 'string' ? m.content : '(structured)';
      renderUserMessage(c);
    } else if (m.role === 'assistant') {
      const c = typeof m.content === 'string' ? m.content : '';
      const b = renderAssistantBubble();
      b.text.textContent = c;
    }
  }
}

function displayName(claudeName) {
  return claudeName.replace(/^alpha_/, '').replace(/_/g, ' ');
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

init();
