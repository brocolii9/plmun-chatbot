/* PLMun Chatbot — Frontend integration with FastAPI backend */

const API = "";

function saveSession(data) {
  localStorage.setItem("plmun_token", data.access_token);
  localStorage.setItem("plmun_kind", data.kind);
  localStorage.setItem("plmun_name", data.full_name || "");
}
function getToken() { return localStorage.getItem("plmun_token"); }
function clearSession() { localStorage.clear(); }

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + getToken(),
  };
}

async function apiFetch(path, options = {}) {
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    options.auth ? authHeaders() : {},
    options.headers || {}
  );
  const res = await fetch(API + path, Object.assign({}, options, { headers }));
  if (res.status === 401) {
    clearSession();
    window.location.href = "/sign_in.html";
    return null;
  }
  return res;
}

function showMessage(el, msg, kind) {
  if (!el) return;
  el.textContent = msg;
  el.classList.remove("success", "error");
  el.classList.add(kind || "error");
}

function initLoginPage() {
  const form = document.getElementById("loginForm");
  if (!form) return;
  const msgEl = document.getElementById("loginMessage");

  if (!document.getElementById("guestLink")) {
    const para = document.createElement("p");
    para.className = "create-account";
    para.innerHTML = 'Or <a href="#" id="guestLink">continue as guest</a>';
    const anchor = form.querySelector(".create-account");
    (anchor ? anchor.parentNode : form).insertBefore(para, anchor || null);

    document.getElementById("guestLink").addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        const res = await fetch("/api/auth/guest", { method: "POST" });
        const data = await res.json();
        saveSession(data);
        window.location.href = "/main_page.html";
      } catch (_) {
        showMessage(msgEl, "Could not start guest session.", "error");
      }
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        showMessage(msgEl, data.detail || "Invalid email or password.", "error");
        return;
      }
      saveSession(data);
      window.location.href = "/main_page.html";
    } catch (_) {
      showMessage(msgEl, "Network error. Please try again.", "error");
    }
  });
}

function initSignupPage() {
  const form = document.getElementById("signupForm");
  if (!form) return;
  const msgEl = document.getElementById("signupMessage");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const full_name = document.getElementById("fullname").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirm_password = document.getElementById("confirm-password").value;

    if (password !== confirm_password) {
      showMessage(msgEl, "Passwords do not match.", "error");
      return;
    }
    if (password.length < 8) {
      showMessage(msgEl, "Password must be at least 8 characters.", "error");
      return;
    }

    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name, email, password, confirm_password }),
      });
      const data = await res.json();
      if (!res.ok) {
        let m = "Registration failed.";
        if (typeof data.detail === "string") m = data.detail;
        else if (Array.isArray(data.detail) && data.detail.length) m = data.detail[0].msg;
        showMessage(msgEl, m, "error");
        return;
      }
      saveSession(data);
      window.location.href = "/main_page.html";
    } catch (_) {
      showMessage(msgEl, "Network error. Please try again.", "error");
    }
  });
}

function initChatPage() {
  const chatForm = document.getElementById("chatForm");
  if (!chatForm) return;

  if (!getToken()) {
    window.location.href = "/sign_in.html";
    return;
  }

  const chatInput = document.getElementById("chatInput");
  const chatMessages = document.getElementById("chatMessages");
  const quickOptions = document.getElementById("quickOptions");
  const newChatBtn = document.getElementById("newChatBtn");
  const logoutLink = document.getElementById("logoutLink");
  const sidebar = document.getElementById("supportSidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const mobileTrigger = document.getElementById("mobileSidebarTrigger");
  const settingsTrigger = document.getElementById("settingsTrigger");
  const settingsModal = document.getElementById("settingsModal");
  const closeSettings = document.getElementById("closeSettings");
  const zoomRange = document.getElementById("zoomRange");
  const zoomInBtn = document.getElementById("zoomInBtn");
  const zoomOutBtn = document.getElementById("zoomOutBtn");
  const zoomValue = document.getElementById("zoomValue");

  let conversationId = null;
  let firstUserMessageSent = false;

  function addBubble(sender, text, meta) {
    const wrap = document.createElement("div");
    wrap.className = "message " + (sender === "student" ? "user" : "bot");

    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = sender === "student" ? "\u{1F9D1}" : "\u{1F916}";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    chatMessages.appendChild(wrap);

    if (meta) {
      const m = document.createElement("div");
      m.style.cssText = "font-size:11px;color:#6b7d75;margin-top:4px;margin-left:48px";
      m.textContent = meta;
      chatMessages.appendChild(m);
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function clearMessages() { chatMessages.innerHTML = ""; }

  async function loadSuggestions() {
    if (firstUserMessageSent) return;
    const res = await apiFetch("/api/chat/suggestions");
    if (!res) return;
    const data = await res.json();
    if (!quickOptions) return;
    quickOptions.innerHTML = "";
    quickOptions.classList.remove("is-hidden");
    data.suggestions.forEach((s) => {
      const btn = document.createElement("button");
      btn.className = "quick-btn";
      btn.type = "button";
      btn.textContent = s;
      btn.addEventListener("click", () => {
        chatInput.value = s;
        sendMessage();
      });
      quickOptions.appendChild(btn);
    });
  }

  function hideSuggestions() {
    if (quickOptions) quickOptions.classList.add("is-hidden");
  }

  async function loadRecent() {
    const res = await apiFetch("/api/chat/conversations", { auth: true });
    if (!res) return;
    const list = await res.json();
    const recentsList = document.querySelector(".recents-list");
    const emptyState = document.getElementById("recentsEmptyState");
    if (!recentsList) return;

    recentsList.innerHTML = "";

    if (!list.length) {
      if (emptyState) {
        emptyState.classList.add("is-visible");
        recentsList.appendChild(emptyState);
      }
      return;
    }

    list.slice(0, 8).forEach((c) => {
      const li = document.createElement("li");
      li.className = "recent-item";
      const icon = document.createElement("i");
      icon.className = "fa-solid fa-message";
      const span = document.createElement("span");
      span.textContent = c.title || ("Chat #" + c.id);
      li.appendChild(icon);
      li.appendChild(span);
      li.addEventListener("click", () => openConversation(c.id));
      recentsList.appendChild(li);
    });
  }

  async function openConversation(id) {
    const res = await apiFetch("/api/chat/conversations/" + id, { auth: true });
    if (!res || !res.ok) return;
    const data = await res.json();

    conversationId = data.id;
    firstUserMessageSent = data.messages.length > 0;
    hideSuggestions();
    clearMessages();

    if (!data.messages.length) {
      addBubble("bot", "Hello! I'm your PLMun student support assistant.");
    } else {
      data.messages.forEach((m) => addBubble(m.sender, m.text));
    }
  }

  async function newChat() {
    const res = await apiFetch("/api/chat/conversations", { method: "POST", auth: true });
    if (!res || !res.ok) return;
    const conv = await res.json();
    conversationId = conv.id;
    firstUserMessageSent = false;
    clearMessages();
    addBubble("bot", "Hello! I'm your PLMun student support assistant. You can ask me about enrollment, grades, documents, or payments.");
    loadSuggestions();
    loadRecent();
  }

  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";
    addBubble("student", text);
    firstUserMessageSent = true;
    hideSuggestions();

    try {
      const res = await apiFetch("/api/chat/message", {
        method: "POST",
        auth: true,
        body: JSON.stringify({ message: text, conversation_id: conversationId }),
      });
      if (!res) return;
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        addBubble("bot", "Sorry, something went wrong: " + (err.detail || "unknown error"));
        return;
      }
      const data = await res.json();
      conversationId = data.conversation_id;

      let meta = null;
      if (data.intent_matched) {
        meta = "intent: " + data.intent_matched + " - confidence: " + (data.confidence_score * 100).toFixed(1) + "%";
      } else if (data.out_of_scope) {
        meta = "out of scope - referred to Registrar";
      }
      addBubble("bot", data.reply, meta);
      loadRecent();
    } catch (_) {
      addBubble("bot", "Network error. Please try again.");
    }
  }

  chatForm.addEventListener("submit", (e) => { e.preventDefault(); sendMessage(); });
  if (newChatBtn) newChatBtn.addEventListener("click", newChat);
  if (logoutLink) {
    logoutLink.addEventListener("click", (e) => {
      e.preventDefault();
      clearSession();
      window.location.href = "/sign_in.html";
    });
  }

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("is-collapsed");
    });
  }
  if (mobileTrigger && sidebar) {
    mobileTrigger.addEventListener("click", () => {
      sidebar.classList.toggle("is-open");
    });
  }

  function openSettings() {
    if (settingsModal) {
      settingsModal.classList.add("is-open");
      settingsModal.setAttribute("aria-hidden", "false");
    }
  }
  function closeSettingsModal() {
    if (settingsModal) {
      settingsModal.classList.remove("is-open");
      settingsModal.setAttribute("aria-hidden", "true");
    }
  }
  if (settingsTrigger) settingsTrigger.addEventListener("click", openSettings);
  if (closeSettings) closeSettings.addEventListener("click", closeSettingsModal);
  if (settingsModal) {
    settingsModal.addEventListener("click", (e) => {
      if (e.target === settingsModal) closeSettingsModal();
    });
  }

  function applyZoom(val) {
    val = Math.max(80, Math.min(140, val));
    document.documentElement.style.fontSize = (val / 100) * 16 + "px";
    if (zoomValue) zoomValue.textContent = val + "%";
    if (zoomRange) zoomRange.value = val;
  }
  if (zoomRange) {
    zoomRange.addEventListener("input", () => applyZoom(parseInt(zoomRange.value, 10)));
    applyZoom(parseInt(zoomRange.value, 10));
  }
  if (zoomInBtn) zoomInBtn.addEventListener("click", () => applyZoom(parseInt(zoomRange.value, 10) + 10));
  if (zoomOutBtn) zoomOutBtn.addEventListener("click", () => applyZoom(parseInt(zoomRange.value, 10) - 10));

  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".lang-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  const voiceBtn = document.getElementById("voiceButton");
  const speakBtn = document.getElementById("speakButton");
  if (voiceBtn) voiceBtn.addEventListener("click", () => alert("Voice input is Phase 2 (P1) - not part of this build."));
  if (speakBtn) speakBtn.addEventListener("click", () => alert("Text-to-speech is Phase 2 (P1) - not part of this build."));

  loadSuggestions();
  loadRecent();
  if (chatInput) chatInput.focus();
}

document.addEventListener("DOMContentLoaded", () => {
  initLoginPage();
  initSignupPage();
  initChatPage();
});