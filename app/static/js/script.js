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

    // Voice preference: 'default' | 'female' | 'male'
  let voicePreference = localStorage.getItem("plmun_voice_pref") || "default";

    // ---------- Developer mode ----------
  // Toggle with ?debug=1 in URL, or press Ctrl+Shift+D on the page
  let devMode = new URLSearchParams(window.location.search).get("debug") === "1";

  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "d") {
      e.preventDefault();
      devMode = !devMode;
      document.querySelectorAll(".dev-meta").forEach((el) => {
        el.style.display = devMode ? "block" : "none";
      });
      const toast = document.createElement("div");
      toast.textContent = devMode ? "Developer mode: ON" : "Developer mode: OFF";
      toast.style.cssText = "position:fixed;bottom:20px;right:20px;background:#0a8f60;color:white;padding:10px 16px;border-radius:10px;font-size:13px;z-index:9999;font-family:inherit;box-shadow:0 6px 20px rgba(0,0,0,0.2)";
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 1800);
    }
  });


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

   function addBubble(sender, text, meta, intent, lang) {
    const wrap = document.createElement("div");
    wrap.className = "message " + (sender === "student" ? "user" : "bot");

    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = sender === "student" ? "\u{1F9D1}" : "\u{1F916}";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    // Store intent + lang for TTS
    if (sender === "bot") {
      if (intent) bubble.dataset.intent = intent;
      if (lang)   bubble.dataset.lang = lang;
    }

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    chatMessages.appendChild(wrap);

    if (meta) {
      const m = document.createElement("div");
      m.className = "dev-meta";
      m.style.cssText = "font-size:11px;color:#6b7d75;margin-top:4px;margin-left:48px;display:" + (devMode ? "block" : "none");
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
      const detectedLang = /\b(paano|ano|mga|ng|sa|ako|kailangan|gusto|saan|para|kumuha|hakbang|bayad|sagot|tanong|mag|ngayon)\b/i.test(text) ? "fil" : "en";
      const audioIntent = data.intent_matched || (data.out_of_scope ? "referral" : null);
      addBubble("bot", data.reply, meta, audioIntent, detectedLang);
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

    // ---------- Voice preference buttons (in Settings modal) ----------
  function applyVoiceButtonState() {
    document.querySelectorAll(".voice-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.voice === voicePreference);
    });
    const help = document.getElementById("voiceHelp");
    if (help) {
      help.textContent =
        voicePreference === "default"
          ? "Default uses the pre-recorded voice."
          : voicePreference === "female"
          ? "Female voice (may not be available on all systems)."
          : "Male voice (may not be available on all systems).";
    }
  }
  applyVoiceButtonState();

  document.querySelectorAll(".voice-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      voicePreference = btn.dataset.voice;
      localStorage.setItem("plmun_voice_pref", voicePreference);
      applyVoiceButtonState();
      console.log("[Voice] preference set to:", voicePreference);
    });
  });

  const voiceBtn = document.getElementById("voiceButton");
  const speakBtn = document.getElementById("speakButton");
    if (voiceBtn) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      voiceBtn.addEventListener("click", () => {
        alert("Voice input is not supported in this browser. Please use Chrome or Edge.");
      });
    } else {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      let listening = false;

      // Detect language: if user typed Tagalog before, use fil-PH; else en-PH
      function pickLang() {
        const lastUser = chatMessages.querySelector(".message.user .bubble");
        if (lastUser) {
          const filMarkers = /\b(paano|ano|mga|ng|sa|ako|kailangan|gusto|saan|para|kumuha|mag|ngayon)\b/i;
          if (filMarkers.test(lastUser.textContent)) return "fil-PH";
        }
        return "en-PH";
      }

      voiceBtn.addEventListener("click", () => {
        if (listening) {
          recognition.stop();
          return;
        }
        recognition.lang = pickLang();
        try {
          recognition.start();
        } catch (e) {
          // Already started — ignore
        }
      });

      recognition.onstart = () => {
        listening = true;
        voiceBtn.classList.add("is-listening");
        chatInput.placeholder = "Listening... speak now";
      };

      recognition.onresult = (event) => {
        let interim = "";
        let final = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) final += transcript;
          else interim += transcript;
        }
        chatInput.value = final || interim;
      };

      recognition.onend = () => {
        listening = false;
        voiceBtn.classList.remove("is-listening");
        chatInput.placeholder = "Type your question here...";

        // Auto-send if we captured text
        const text = chatInput.value.trim();
        if (text) {
          sendMessage();
        }
      };

      recognition.onerror = (event) => {
        listening = false;
        voiceBtn.classList.remove("is-listening");
        chatInput.placeholder = "Type your question here...";
        if (event.error === "not-allowed") {
          alert("Microphone access was denied. Please allow mic access in your browser settings.");
        }
      };
    }
  }

  // ---------- TTS (Read Aloud) ----------
    // ---------- TTS (Read Aloud) with toggle ----------
  // ---------- TTS (Read Aloud) with improved voice selection ----------
  // ---------- TTS with pre-recorded audio + Web Speech fallback ----------
    // ---------- TTS with gender preference ----------
  if (speakBtn) {
    let currentAudio = null;

    let cachedVoices = [];
    function loadVoices() { cachedVoices = window.speechSynthesis.getVoices(); }
    loadVoices();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    const FEMALE_NAMES = ["zira", "hazel", "susan", "samantha", "victoria", "karen",
                          "moira", "tessa", "fiona", "maria", "catherine", "linda",
                          "michelle", "clara", "emma", "ava", "allison", "serena",
                          "joanna", "salli", "kendra", "kimberly", "nicole",
                          "blessica", "rosa", "female", "woman", "girl"];
    const MALE_NAMES   = ["david", "mark", "george", "james", "daniel", "alex",
                          "fred", "tom", "rishi", "ramil", "male", "man", "guy",
                          "paul", "ryan", "christopher", "eric",
                          "matthew", "brian", "aaron", "joseph", "william",
                          "justin", "kevin", "richard"];

    function guessGender(voice) {
      const n = (voice.name || "").toLowerCase();
      if (FEMALE_NAMES.some(k => n.includes(k))) return "female";
      if (MALE_NAMES.some(k => n.includes(k))) return "male";
      return "unknown";
    }

    function findVoice(lang, genderPref) {
      let voices = window.speechSynthesis.getVoices();
      if (!voices.length) voices = cachedVoices;
      if (!voices.length) return null;

      const langMatches = voices.filter(v => {
        if (lang === "fil") {
          return v.lang === "fil-PH" || v.lang === "tl-PH"
              || v.lang === "en-PH" || v.lang.startsWith("en");
        }
        return v.lang === "en-PH" || v.lang === "en-US" || v.lang.startsWith("en");
      });

      const pool = langMatches.length ? langMatches : voices;

      if (genderPref === "female" || genderPref === "male") {
        const matched = pool.find(v => guessGender(v) === genderPref);
        if (matched) return matched;
      }

      if (lang === "fil") return pool.find(v => v.lang === "en-PH") || pool[0];
      return pool.find(v => v.lang === "en-US") || pool[0];
    }

    function stopAll() {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
      }
      window.speechSynthesis.cancel();
      speakBtn.classList.remove("is-listening");
      speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
    }

    function speakWithWebSpeech(text, lang, genderPref) {
      const utter = new SpeechSynthesisUtterance(text);
      const voice = findVoice(lang, genderPref);
      console.log("[TTS] speakWithWebSpeech → genderPref:", genderPref, "| voice:", voice ? voice.name : "NONE");
      if (voice) utter.voice = voice;

      utter.lang = lang === "fil" ? "fil-PH" : "en-US";
      utter.rate = 0.9;
      utter.pitch = genderPref === "female" ? 1.1 : 0.9;
      utter.volume = 1.0;

      utter.onstart = () => {
        speakBtn.classList.add("is-listening");
        speakBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
      };
      utter.onended = () => stopAll();
      utter.onerror = () => stopAll();

      window.speechSynthesis.speak(utter);
    }

    speakBtn.addEventListener("click", async () => {
      if (currentAudio || window.speechSynthesis.speaking) {
        stopAll();
        return;
      }

      const botBubbles = chatMessages.querySelectorAll(".message.bot .bubble");
      if (!botBubbles.length) return;
      const lastBubble = botBubbles[botBubbles.length - 1];
      const text = lastBubble.textContent;
      const intent = lastBubble.dataset.intent;
      const lang = lastBubble.dataset.lang || "en";

      console.log("[TTS] Clicked. voicePreference =", voicePreference, "| lang =", lang, "| intent =", intent);

      if (voicePreference !== "default") {
        console.log("[TTS] Using gender:", voicePreference);
        speakWithWebSpeech(text, lang, voicePreference);
        return;
      }

      console.log("[TTS] Using default MP3");
      if (intent) {
        const audioPath = `/audio/${intent}_${lang}.mp3`;
        try {
          const audio = new Audio(audioPath);
          currentAudio = audio;

          audio.onplay = () => {
            speakBtn.classList.add("is-listening");
            speakBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
          };
          audio.onended = () => stopAll();
          audio.onerror = () => {
            console.log("[TTS] MP3 not found, fallback to Web Speech");
            currentAudio = null;
            speakWithWebSpeech(text, lang, "default");
          };

          await audio.play();
          return;
        } catch (err) {
          currentAudio = null;
        }
      }

      speakWithWebSpeech(text, lang, "default");
    });
  }


  loadSuggestions();
  loadRecent();
  if (chatInput) chatInput.focus();
}

document.addEventListener("DOMContentLoaded", () => {
  initLoginPage();
  initSignupPage();
  initChatPage();
});