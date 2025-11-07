/* ========================================
   CHAT - DATETIME
======================================== */
function updateDateTime() {
  const now = new Date();
  const d = String(now.getDate()).padStart(2, "0");
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const y = now.getFullYear();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const dtEl = document.getElementById("datetime");
  if (dtEl) dtEl.textContent = `${d}/${m}/${y} ${hh}:${mm}`;
}
updateDateTime();
setInterval(updateDateTime, 60000);

/* ========================================
     CHAT - TABS
  ======================================== */
const tabs = document.querySelectorAll(".tab");
let activeTab = "nacional";
tabs.forEach((t) =>
  t.addEventListener("click", () => {
    tabs.forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    activeTab = t.dataset.tab;
    loadMessages(activeTab);
  })
);

/* ========================================
     CHAT - AVATAR PICKER (removed)
  ======================================== */
let selectedAvatar = ""; // avatars removed; keep empty

/* ========================================
     CHAT - FUNCIONES
  ======================================== */
function appendMessage(m) {
  const container = document.getElementById("messages");
  const wrap = document.createElement("div");
  wrap.className = "message";
  const icon = document.createElement("div");
  icon.className = "icon";
  // Avatars removed — optionally show a sender initial circle
  if (m.sender) {
    const initial = document.createElement('div');
    initial.className = 'avatar-initial';
    initial.textContent = m.sender.charAt(0).toUpperCase();
    icon.appendChild(initial);
  }
  const txt = document.createElement("div");
  txt.className = "text";
  const senderHTML = m.sender
    ? `<div style="font-weight:600;margin-bottom:4px">${escapeHtml(
        m.sender
      )}</div>`
    : "";
  txt.innerHTML = `${senderHTML}<div style="font-size:11px;color:#666;margin-bottom:4px">${
    m.timestamp || ""
  }</div><div>${escapeHtml(m.text)}</div>`;
  wrap.appendChild(icon);
  wrap.appendChild(txt);
  container.appendChild(wrap);
  container.scrollTop = container.scrollHeight;
}

async function loadMessages(tab) {
  try {
    const res = await fetch("/messages/?tab=" + encodeURIComponent(tab));
    if (!res.ok) throw new Error("No se pudieron cargar mensajes");
    const data = await res.json();
    const messagesEl = document.getElementById("messages");
    if (messagesEl) messagesEl.innerHTML = "";
    data.messages.forEach((m) => appendMessage(m));
  } catch (e) {
    console.error(e);
  }
}

async function sendMessage() {
  const input = document.getElementById("msgInput");
  const text = input?.value.trim();
  if (!text) return;

  // Obtener CSRF token (usando la función global de main.js)
  const token =
    typeof getCSRFToken === "function"
      ? getCSRFToken()
      : typeof csrftoken !== "undefined"
      ? csrftoken
      : null;

  try {
    const res = await fetch("/messages/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": token,
      },
      body: JSON.stringify({
        text: text,
        tab: activeTab,
        avatar: selectedAvatar,
        sender: window.currentUsername || "",
      }),
    });
    if (!res.ok) {
      const textErr = await res.text().catch(() => null);
      throw new Error("Server error: " + (textErr || res.status));
    }
    const data = await res.json();
    appendMessage(data.message);
    if (input) input.value = "";
  } catch (err) {
    alert("No se pudo enviar el mensaje.");
    console.error(err);
  }
}

const sendBtn = document.getElementById("sendBtn");
const msgInput = document.getElementById("msgInput");
if (sendBtn) sendBtn.addEventListener("click", sendMessage);
if (msgInput)
  msgInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

/* Chat close button */
const closeChatBtn = document.getElementById("close-chat");
if (closeChatBtn) {
  closeChatBtn.addEventListener('click', () => {
    const overlay = document.getElementById('chatOverlay');
    if (overlay) overlay.style.display = 'none';
  });
}

/* Toggle chat open/close with button */
const toggleChatBtn = document.getElementById('toggle-chat');
if (toggleChatBtn) {
  toggleChatBtn.addEventListener('click', () => {
    const overlay = document.getElementById('chatOverlay');
    if (!overlay) return;
    if (overlay.style.display === 'none' || getComputedStyle(overlay).display === 'none') {
      overlay.style.display = 'flex';
    } else {
      overlay.style.display = 'none';
    }
  });
}

// Disable input if user not logged in
if (!window.currentUsername || window.currentUsername.trim() === '') {
  const input = document.getElementById('msgInput');
  const send = document.getElementById('sendBtn');
  if (input) { input.disabled = true; input.placeholder = 'Inicia sesión para escribir mensajes'; }
  if (send) { send.disabled = true; }
  // Optionally open login modal on focus/click
  if (input) input.addEventListener('focus', () => { const loginModal = document.getElementById('loginModal'); if (loginModal) loginModal.style.display = 'block'; });
}

/* Cargar mensajes inicial */
loadMessages(activeTab);
