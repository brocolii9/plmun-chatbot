/* PLMun Chatbot — MOBILE UI logic
   Only loaded on mobile.html
   Works alongside script.js — uses the same DOM IDs where possible.
*/

(function () {
  "use strict";

  // ============================================================
  // POPULAR SERVICES
  // ============================================================
  const POPULAR = [
    { icon: "fa-graduation-cap", title: "Enrollment",         prompt: "How do I enroll?" },
    { icon: "fa-star",           title: "Scholarships",       prompt: "What scholarships are available?" },
    { icon: "fa-file-lines",     title: "Academic Records",   prompt: "How do I request a document?" },
    { icon: "fa-calendar-days",  title: "Class Schedule",     prompt: "Where can I see my class schedule?" },
    { icon: "fa-heart-pulse",    title: "Health Services",    prompt: "Where can I get medical assistance?" },
    { icon: "fa-comments",       title: "Guidance",           prompt: "How can I talk to a counselor?" }
  ];

  function renderPopular() {
    const grid = document.getElementById("popularServicesGrid");
    const dots = document.getElementById("popularServicesDots");
    if (!grid) return;

    grid.innerHTML = "";
    POPULAR.slice(0, 4).forEach((svc) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "m-ps-card";
      card.innerHTML = `
        <span class="m-ps-icon"><i class="fa-solid ${svc.icon}"></i></span>
        <span class="m-ps-title">${svc.title}</span>
      `;
      card.addEventListener("click", () => {
        const input = document.getElementById("chatInput");
        const form = document.getElementById("chatForm");
        if (input && form) {
          input.value = svc.prompt;
          form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
        }
        hidePopular();
      });
      grid.appendChild(card);
    });

    if (dots) {
      dots.innerHTML = "";
      for (let i = 0; i < 3; i++) {
        const d = document.createElement("span");
        d.className = "dot" + (i === 0 ? " is-active" : "");
        dots.appendChild(d);
      }
    }
  }

  function hidePopular() {
    const el = document.getElementById("popularServices");
    if (el) el.classList.add("is-hidden");
  }

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
  // BOTTOM NAV — History opens drawer
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
  // HIDE POPULAR AFTER FIRST USER MESSAGE
  // ============================================================
  function watchFirstMessage() {
    const form = document.getElementById("chatForm");
    if (!form) return;
    form.addEventListener("submit", hidePopular, true);
  }

  // ============================================================
  // VOICE BUTTON — bind to script.js logic via existing #voiceButton id
  // script.js binds to #voiceButton which exists here.
  // ============================================================
  // (no extra code needed — script.js handles it)

  // ============================================================
  // BOOT
  // ============================================================
  document.addEventListener("DOMContentLoaded", () => {
    renderPopular();
    initDrawer();
    initAboutSheet();
    initBottomNav();
    watchFirstMessage();
  });
})();

  // ============================================================
  // FORCE VIEWPORT HEIGHT (fixes Capacitor WebView mismatch)
  // ============================================================
  function setAppHeight() {
    const h = window.innerHeight;
    document.documentElement.style.setProperty("--app-height", h + "px");
    document.body.style.height = h + "px";
    document.body.style.overflow = "hidden";
  }
  setAppHeight();
  window.addEventListener("resize", setAppHeight);
  window.addEventListener("orientationchange", () => setTimeout(setAppHeight, 100));