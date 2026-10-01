/* PLMun Chatbot — MOBILE UI logic
   Only loaded on mobile.html
   Automatically upgrades bubbles created by script.js to mobile styles.
*/

(function () {
  "use strict";

  // ============================================================
  // DRAWER
  // ============================================================
  function initDrawer() {
    const menuBtn = document.getElementById("mobileMenuBtn");
    const drawer = document.getElementById("drawer");
    const backdrop = document.getElementById("drawerBackdrop");
    const closeBtn = document.getElementById("drawerClose");

    function open() {
      if (drawer) drawer.classList.add("is-open");
      if (backdrop) backdrop.classList.add("is-open");
    }
    function close() {
      if (drawer) drawer.classList.remove("is-open");
      if (backdrop) backdrop.classList.remove("is-open");
    }

    if (menuBtn) menuBtn.addEventListener("click", open);
    if (backdrop) backdrop.addEventListener("click", close);
    if (closeBtn) closeBtn.addEventListener("click", close);
  }

  // ============================================================
  // ABOUT SHEET
  // ============================================================
  function initAboutSheet() {
    const navAbout = document.getElementById("navAbout");
    const sheet = document.getElementById("aboutSheet");
    const backdrop = document.getElementById("sheetBackdrop");
    const closeBtn = document.getElementById("sheetClose");

    function open() {
      if (sheet) sheet.classList.add("is-open");
      if (backdrop) backdrop.classList.add("is-open");
    }
    function close() {
      if (sheet) sheet.classList.remove("is-open");
      if (backdrop) backdrop.classList.remove("is-open");
    }

    if (navAbout) navAbout.addEventListener("click", open);
    if (backdrop) backdrop.addEventListener("click", close);
    if (closeBtn) closeBtn.addEventListener("click", close);
  }

  // ============================================================
  // BOTTOM NAV
  // ============================================================
  function initBottomNav() {
    const tabs = document.querySelectorAll(".m-nav-tab");
    const navHistory = document.getElementById("navHistory");
    const drawer = document.getElementById("drawer");
    const drawerBackdrop = document.getElementById("drawerBackdrop");

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("is-active"));
        tab.classList.add("is-active");
      });
    });

    if (navHistory) {
      navHistory.addEventListener("click", () => {
        if (drawer) drawer.classList.add("is-open");
        if (drawerBackdrop) drawerBackdrop.classList.add("is-open");
      });
    }
  }

  // ============================================================
  // BUBBLE UPGRADER — converts script.js bubbles to mobile classes
  // script.js creates: <div class="message bot|user"><span class="avatar">…</span><div class="bubble">…</div></div>
  // Mobile needs:      <div class="m-message m-bot|m-user"><span class="m-avatar …">…</span><div class="m-bubble-wrap"><div class="m-bubble …">…</div></div></div>
  // ============================================================
  function upgradeBubble(node) {
    if (!node || node.nodeType !== 1) return;
    if (node.classList.contains("m-message")) return;       // already upgraded
    if (!node.classList.contains("message")) return;         // not a bubble

    const isUser = node.classList.contains("user");

    // 1. Swap the row classes
    node.classList.remove("message", "user", "bot");
    node.classList.add("m-message", isUser ? "m-user" : "m-bot");

    // 2. Upgrade the avatar (bot only) — remove user avatar entirely
    const avatar = node.querySelector(".avatar");
    if (avatar) {
      if (isUser) {
        avatar.remove();
      } else {
        avatar.classList.remove("avatar");
        avatar.classList.add("m-avatar", "m-avatar-bot");
        // ensure it uses the robot icon
        if (!avatar.querySelector("i")) {
          avatar.innerHTML = '<i class="fa-solid fa-robot"></i>';
        }
      }
    }

    // 3. Wrap the bubble
    const bubble = node.querySelector(".bubble");
    if (bubble) {
      bubble.classList.remove("bubble");
      bubble.classList.add("m-bubble", isUser ? "m-bubble-user" : "m-bubble-bot");

      // Wrap in .m-bubble-wrap if not already
      const parent = bubble.parentElement;
      if (!parent.classList.contains("m-bubble-wrap")) {
        const wrap = document.createElement("div");
        wrap.className = "m-bubble-wrap";
        parent.insertBefore(wrap, bubble);
        wrap.appendChild(bubble);
      }
    }

    // 4. Fix alignment: bot left, user right
    node.style.alignSelf = isUser ? "flex-end" : "flex-start";
  }

  function initBubbleUpgrader() {
    const chatMessages = document.getElementById("chatMessages");
    if (!chatMessages) return;

    // Upgrade existing bubbles (including the welcome one if it uses .message)
    chatMessages.querySelectorAll(".message").forEach(upgradeBubble);

    // Watch for new bubbles added by script.js
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((m) => {
        m.addedNodes.forEach((n) => {
          if (n.nodeType === 1) upgradeBubble(n);
        });
      });
    });
    observer.observe(chatMessages, { childList: true, subtree: true });
  }

  // ============================================================
  // BOOT
  // ============================================================
  document.addEventListener("DOMContentLoaded", () => {
    initDrawer();
    initAboutSheet();
    initBottomNav();
    initBubbleUpgrader();
  });
})();