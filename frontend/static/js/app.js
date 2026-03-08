const API_BASE = "";

// ── DOM refs ──────────────────────────────────────
const messagesEl   = document.getElementById("messages");
const messagesWrap = document.getElementById("messages-wrap");
const input        = document.getElementById("user-input");
const sendBtn      = document.getElementById("send-btn");
const emptyState   = document.getElementById("empty-state");
const newChatBtn   = document.getElementById("new-chat-btn");

const history = [];

// ── Auto-resize textarea ──────────────────────────
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 200) + "px";
  sendBtn.disabled = input.value.trim() === "";
});

// ── Send on Enter (Shift+Enter = newline) ─────────
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) submitMessage();
  }
});

sendBtn.addEventListener("click", submitMessage);

// ── Suggestion chips ──────────────────────────────
document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => {
    input.value = chip.textContent.trim();
    input.dispatchEvent(new Event("input"));
    input.focus();
  });
});

// ── New chat — clear everything ───────────────────
newChatBtn.addEventListener("click", () => {
  history.length = 0;
  messagesEl.innerHTML = "";
  messagesEl.appendChild(emptyState);
  emptyState.style.display = "flex";
  setLoading(false);
  input.value = "";
  input.style.height = "auto";
  input.focus();
});

// ── Helpers ───────────────────────────────────────
function scrollBottom() {
  messagesWrap.scrollTop = messagesWrap.scrollHeight;
}

function setLoading(on) {
  sendBtn.disabled = on || input.value.trim() === "";
  input.disabled   = on;
}

function hideEmptyState() {
  if (emptyState && emptyState.parentNode) {
    emptyState.style.display = "none";
    emptyState.remove();
  }
}

function createRow(role) {
  const row = document.createElement("div");
  row.classList.add("message-row", role);

  const avatarEl = document.createElement("div");
  avatarEl.className = "msg-avatar";
  avatarEl.textContent = role === "user" ? "U" : "AI";

  const body = document.createElement("div");
  body.className = "msg-body";

  const name = document.createElement("div");
  name.className = "msg-name";
  name.textContent = role === "user" ? "You" : "RAG AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  body.appendChild(name);
  body.appendChild(bubble);
  row.appendChild(avatarEl);
  row.appendChild(body);
  messagesEl.appendChild(row);
  scrollBottom();

  return { row, bubble, body };
}

function addUserMessage(text) {
  hideEmptyState();
  const { bubble } = createRow("user");
  bubble.textContent = text;
  scrollBottom();
}

function createAssistantRow() {
  hideEmptyState();
  const { bubble, body } = createRow("assistant");

  const dots = document.createElement("div");
  dots.className = "typing-dots";
  dots.innerHTML = "<span></span><span></span><span></span>";
  bubble.appendChild(dots);
  scrollBottom();

  return { bubble, body, dots };
}

function appendContext(body, chunks) {
  const toggle = document.createElement("button");
  toggle.className = "context-toggle";
  toggle.innerHTML = `
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path d="M1 3h10M1 6h7M1 9h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    ${chunks.length} source${chunks.length !== 1 ? "s" : ""}
  `;

  const panel = document.createElement("div");
  panel.className = "context-panel";

  chunks.forEach((chunk, i) => {
    const el = document.createElement("div");
    el.className = "context-chunk";
    const meta  = chunk.metadata || {};
    const label = meta.source
      ? `${meta.source}  ·  page ${meta.page ?? "?"}`
      : `Chunk ${i + 1}`;
    el.innerHTML = `<strong>${label}</strong>${chunk.content}`;
    panel.appendChild(el);
  });

  toggle.addEventListener("click", () => {
    panel.classList.toggle("visible");
    const open = panel.classList.contains("visible");
    toggle.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M1 3h10M1 6h7M1 9h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      ${open ? "Hide sources" : chunks.length + " source" + (chunks.length !== 1 ? "s" : "")}
    `;
  });

  body.appendChild(toggle);
  body.appendChild(panel);
}

// ── Core send ─────────────────────────────────────
function submitMessage() {
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";
  input.style.height = "auto";
  sendBtn.disabled = true;
  sendMessage(msg);
}

async function sendMessage(message) {
  addUserMessage(message);
  const { bubble, body, dots } = createAssistantRow();
  setLoading(true);

  let fullAnswer = "";

  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer    = "";
    let firstToken = true;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const payload = line.slice(6).trim();
        if (payload === "[DONE]") continue;

        try {
          const data = JSON.parse(payload);

          if (data.type === "token") {
            if (firstToken) {
              dots.remove();
              firstToken = false;
            }
            fullAnswer += data.content;
            bubble.textContent = fullAnswer;
            scrollBottom();

          } else if (data.type === "context") {
            appendContext(body, data.content);
          }
        } catch {
          // ignore malformed SSE lines
        }
      }
    }

    if (firstToken) {
      dots.remove();
      bubble.textContent = "(No response)";
    }

    history.push({ role: "user",      content: message });
    history.push({ role: "assistant", content: fullAnswer });

  } catch (err) {
    dots.remove();
    bubble.textContent = `Error: ${err.message}`;
  } finally {
    setLoading(false);
    sendBtn.disabled = input.value.trim() === "";
  }
}