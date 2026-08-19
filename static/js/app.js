/* BarberBook common UI helpers */

function toast(msg, type = '') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = 'toast' + (type ? ' ' + type : '');
  el.hidden = false;
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => { el.hidden = true; }, 3500);
}

function formatMoney(n) {
  const num = typeof n === 'number' ? n : parseFloat(n || 0);
  return '$' + num.toFixed(2);
}

function formatStatus(s) {
  return `<span class="pill pill-${s}">${s.replace('_', ' ')}</span>`;
}

function placeholderAvatar(name = '') {
  const initials = name.split(' ').map(x => x[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'BB';
  return `data:image/svg+xml;utf8,${encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'>
      <rect width='400' height='400' fill='#14110f'/>
      <text x='50%' y='54%' text-anchor='middle' dominant-baseline='middle' font-size='150' font-family='Playfair Display, Georgia, serif' fill='#c9a24a' font-weight='700'>${initials}</text>
    </svg>`)}`;
}

function serviceIcon(cat) {
  return ({
    haircut: '✂️', beard: '🧔', shave: '🪒', combo: '💈', kids: '🧒', styling: '💆‍♂️',
  })[cat] || '✂️';
}

function stars(rating) {
  const r = Math.round(parseFloat(rating || 0));
  return '★'.repeat(r) + '<span style="color:#ddd">' + '★'.repeat(5 - r) + '</span>';
}

function dayNames(arr) {
  const names = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  return (arr || []).map(d => names[d]).join(', ') || 'None';
}

function refreshNavbar() {
  const user = BB.getUser();
  const isAuth = !!user;
  const isAdmin = !!(user && (user.role === 'admin' || user.is_staff));
  document.querySelectorAll('.auth-only').forEach(el => el.hidden = !isAuth);
  document.querySelectorAll('.guest-only').forEach(el => el.hidden = isAuth);
  document.querySelectorAll('.admin-only').forEach(el => el.hidden = !isAdmin);
  if (isAuth) document.querySelectorAll('.user-name').forEach(el => el.textContent = user.username);
}

document.addEventListener('click', async (e) => {
  if (e.target && e.target.id === 'logoutBtn') {
    await BB.logout(); BB.clearTokens();
    toast('Logged out', 'success');
    setTimeout(() => { window.location.href = '/'; }, 400);
  }
});

document.addEventListener('DOMContentLoaded', refreshNavbar);

function requireAuth(redirect = '/login/') {
  if (!BB.getUser()) {
    toast('Please sign in first', 'error');
    setTimeout(() => { window.location.href = redirect + '?next=' + encodeURIComponent(location.pathname + location.search); }, 500);
    return false;
  }
  return true;
}

function requireAdmin() {
  const u = BB.getUser();
  if (!u || (u.role !== 'admin' && !u.is_staff)) {
    toast('Admin access required', 'error');
    setTimeout(() => { window.location.href = '/'; }, 500);
    return false;
  }
  return true;
}
