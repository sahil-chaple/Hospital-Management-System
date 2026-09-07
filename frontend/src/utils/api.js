const API_BASE = '/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('hms_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('hms_token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Something went wrong' }));
    throw new Error(error.detail || 'Something went wrong');
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export default {
  login: (email, password) => {
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);
    return request('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });
  },

  register: (userData) => request('/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  }),

  getMe: () => request('/me'),

  logout: () => request('/logout', { method: 'POST' }),

  getPatients: (search = '') => request(`/patients?search=${encodeURIComponent(search)}`),
  getPatient: (id) => request(`/patients/${id}`),
  createPatient: (data) => request('/patients', { method: 'POST', body: JSON.stringify(data) }),
  updatePatient: (id, data) => request(`/patients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePatient: (id) => request(`/patients/${id}`, { method: 'DELETE' }),

  getDoctors: (search = '') => request(`/doctors?search=${encodeURIComponent(search)}`),
  getDoctor: (id) => request(`/doctors/${id}`),
  createDoctor: (data) => request('/doctors', { method: 'POST', body: JSON.stringify(data) }),
  updateDoctor: (id, data) => request(`/doctors/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteDoctor: (id) => request(`/doctors/${id}`, { method: 'DELETE' }),

  getAppointments: () => request('/appointments'),
  getAppointment: (id) => request(`/appointments/${id}`),
  createAppointment: (data) => request('/appointments', { method: 'POST', body: JSON.stringify(data) }),
  updateAppointment: (id, data) => request(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteAppointment: (id) => request(`/appointments/${id}`, { method: 'DELETE' }),

  getStats: () => request('/stats'),
  getAuditLogs: () => request('/audit-logs'),
};
