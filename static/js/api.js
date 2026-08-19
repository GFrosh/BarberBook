/* BarberBook API client */
const BB = (() => {
  const BASE = '/api';

  function getTokens() { try { return JSON.parse(localStorage.getItem('bb_tokens') || 'null'); } catch { return null; } }
  function setTokens(t) { localStorage.setItem('bb_tokens', JSON.stringify(t)); }
  function clearTokens() { localStorage.removeItem('bb_tokens'); localStorage.removeItem('bb_user'); }
  function getUser() { try { return JSON.parse(localStorage.getItem('bb_user') || 'null'); } catch { return null; } }
  function setUser(u) { localStorage.setItem('bb_user', JSON.stringify(u)); }

  async function request(path, { method = 'GET', body, auth = false } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const t = getTokens();
      if (t?.access) headers['Authorization'] = `Bearer ${t.access}`;
    }
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${BASE}${path}`, opts);
    let data = null;
    const txt = await res.text();
    try { data = txt ? JSON.parse(txt) : null; } catch { data = txt; }
    if (!res.ok) {
      const err = new Error(typeof data === 'string' ? data : (data?.detail || 'Request failed'));
      err.status = res.status; err.data = data;
      throw err;
    }
    return data;
  }

  return {
    // auth
    register: (p) => request('/auth/register', { method: 'POST', body: p }),
    login:    (p) => request('/auth/login', { method: 'POST', body: p }),
    logout:   () => {
      const t = getTokens();
      return request('/auth/logout', { method: 'POST', auth: true, body: { refresh: t?.refresh } }).catch(()=>{});
    },
    me:       () => request('/auth/me', { auth: true }),

    // services
    listServices: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/services/${qs ? '?' + qs : ''}`);
    },
    getService: (id) => request(`/services/${id}/`),
    createService: (p) => request('/services/', { method: 'POST', auth: true, body: p }),
    updateService: (id, p) => request(`/services/${id}/`, { method: 'PUT', auth: true, body: p }),
    deleteService: (id) => request(`/services/${id}/`, { method: 'DELETE', auth: true }),

    // barbers
    listBarbers: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/barbers/${qs ? '?' + qs : ''}`);
    },
    getBarber: (id) => request(`/barbers/${id}/`),
    createBarber: (p) => request('/barbers/', { method: 'POST', auth: true, body: p }),
    updateBarber: (id, p) => request(`/barbers/${id}/`, { method: 'PUT', auth: true, body: p }),
    deleteBarber: (id) => request(`/barbers/${id}/`, { method: 'DELETE', auth: true }),
    barberSlots: (id, date, serviceId) =>
      request(`/barbers/${id}/slots?date=${date}&service=${serviceId}`),
    barberBusy: (id, date) => request(`/barbers/${id}/busy?date=${date}`),

    // appointments
    listAppointments: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/appointments/${qs ? '?' + qs : ''}`, { auth: true });
    },
    createAppointment: (p) => request('/appointments/', { method: 'POST', auth: true, body: p }),
    cancelAppointment: (id) => request(`/appointments/${id}/cancel/`, { method: 'POST', auth: true }),

    // admin
    adminAppointments: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/admin/appointments${qs ? '?' + qs : ''}`, { auth: true });
    },
    adminUpdateStatus: (id, status) =>
      request(`/admin/appointments/${id}/status`, { method: 'PATCH', auth: true, body: { status } }),
    adminStats: () => request('/admin/stats', { auth: true }),

    getTokens, setTokens, clearTokens, getUser, setUser,
  };
})();
