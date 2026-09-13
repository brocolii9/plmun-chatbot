// ---------- Shared admin shell ----------
// Verifies admin token, redirects to login if missing/expired,
// populates admin name, wires logout.

function adminToken() {
  return localStorage.getItem("plmun_admin_token");
}

async function adminFetch(path, options = {}) {
  const token = adminToken();
  if (!token) {
    window.location.href = "/admin/login";
    return null;
  }
  const headers = Object.assign(
    { "Content-Type": "application/json", Authorization: "Bearer " + token },
    options.headers || {}
  );
  const res = await fetch(path, Object.assign({}, options, { headers }));
  if (res.status === 401 || res.status === 403) {
    localStorage.removeItem("plmun_admin_token");
    window.location.href = "/admin/login";
    return null;
  }
  return res;
}

async function initAdminShell() {
  const token = adminToken();
  if (!token) {
    window.location.href = "/admin/login";
    return;
  }

  const res = await adminFetch("/api/admin/me");
  if (!res) return;
  const me = await res.json();

  const nameEl = document.getElementById("adminName");
  const sidebarEl = document.getElementById("sidebarName");
  if (nameEl) nameEl.textContent = me.full_name + " (" + me.role + ")";
  if (sidebarEl) sidebarEl.textContent = me.full_name;

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.removeItem("plmun_admin_token");
      localStorage.removeItem("plmun_admin_name");
      localStorage.removeItem("plmun_admin_role");
      window.location.href = "/admin/login";
    });
  }
}