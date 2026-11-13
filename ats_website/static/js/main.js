/* ── ATS PRO Main JavaScript ───────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {

  // ── Sidebar Toggle ──────────────────────────────────────────────
  const sidebar = document.getElementById('sidebar');
  const mainLayout = document.getElementById('mainLayout');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  let sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';

  function applySidebarState() {
    if (!sidebar) return;
    if (window.innerWidth <= 768) return;  // Mobile handled separately
    sidebar.style.width = sidebarCollapsed ? '64px' : '';
    if (mainLayout) mainLayout.style.marginLeft = sidebarCollapsed ? '64px' : '';
  }

  sidebarToggle?.addEventListener('click', () => {
    if (window.innerWidth <= 768) return;
    sidebarCollapsed = !sidebarCollapsed;
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed);
    applySidebarState();
  });

  mobileMenuBtn?.addEventListener('click', () => {
    sidebar?.classList.add('open');
    sidebarOverlay?.classList.add('show');
    document.body.style.overflow = 'hidden';
  });

  sidebarOverlay?.addEventListener('click', () => {
    sidebar?.classList.remove('open');
    sidebarOverlay?.classList.remove('show');
    document.body.style.overflow = '';
  });

  // ── User Dropdown ───────────────────────────────────────────────
  const userMenuBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');

  userMenuBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    userDropdown?.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    userDropdown?.classList.remove('show');
  });

  // ── Auto-dismiss Flash Alerts ───────────────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(20px)';
      alert.style.transition = 'all 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // ── Password Toggle ─────────────────────────────────────────────
  document.querySelectorAll('.pwd-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input');
      const icon = btn.querySelector('i');
      if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
        icon?.classList.toggle('fa-eye');
        icon?.classList.toggle('fa-eye-slash');
      }
    });
  });

  // ── Password Strength Meter ─────────────────────────────────────
  const pwdInput = document.getElementById('password');
  const strengthBar = document.getElementById('pwdStrength');
  const strengthFill = document.getElementById('strengthFill');
  const strengthLabel = document.getElementById('strengthLabel');

  if (pwdInput && strengthBar) {
    pwdInput.addEventListener('input', () => {
      const pwd = pwdInput.value;
      if (!pwd) { strengthBar.style.display = 'none'; return; }
      strengthBar.style.display = 'block';
      let strength = 0;
      if (pwd.length >= 8) strength++;
      if (/[A-Z]/.test(pwd)) strength++;
      if (/[0-9]/.test(pwd)) strength++;
      if (/[^A-Za-z0-9]/.test(pwd)) strength++;
      const levels = [
        { pct: '25%', color: '#FF6B6B', label: 'Weak' },
        { pct: '50%', color: '#FFB347', label: 'Fair' },
        { pct: '75%', color: '#6C63FF', label: 'Good' },
        { pct: '100%', color: '#00D4AA', label: 'Strong' },
      ];
      const lvl = levels[strength - 1] || levels[0];
      if (strengthFill) { strengthFill.style.width = lvl.pct; strengthFill.style.background = lvl.color; }
      if (strengthLabel) { strengthLabel.textContent = lvl.label; strengthLabel.style.color = lvl.color; }
    });
  }

  // ── Score bars animate on load ──────────────────────────────────
  const fills = document.querySelectorAll('.score-bar-fill, .breakdown-fill');
  fills.forEach(el => {
    const target = el.style.width;
    el.style.width = '0%';
    requestAnimationFrame(() => {
      el.style.transition = 'width 1s ease';
      el.style.width = target;
    });
  });

  // ── Global Search ───────────────────────────────────────────────
  const globalSearch = document.getElementById('globalSearch');
  globalSearch?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && globalSearch.value.trim()) {
      window.location.href = '/jobs?search=' + encodeURIComponent(globalSearch.value.trim());
    }
  });

  // ── Table Row Click → Navigate ──────────────────────────────────
  document.querySelectorAll('.data-table tbody tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => window.location.href = row.dataset.href);
  });

  // ── Confirm delete forms ────────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

  // ── Enumerate filter fix (Jinja2 doesn't have enumerate built-in) ──
  // This is handled server-side via a custom filter or loop index.

  console.log('%cATS PRO v1.0 — Loaded ✓', 'color: #6C63FF; font-weight: bold; font-size: 14px;');
});
