import axios from 'axios';
import useSWR, { mutate } from 'swr';
import useSWRMutation from 'swr/mutation';
import { toast } from 'sonner';

const baseUrl = process.env.REACT_APP_BACKEND_URL || '';
const API_URL = baseUrl ? `${baseUrl}/api` : '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 30000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalize: backend error_handlers.py returns {"error": "..."} but most
    // frontend code reads data.detail — copy error → detail when missing.
    if (error.response?.data?.error && !error.response.data.detail) {
      error.response.data.detail = error.response.data.error;
    }
    const isLoginRequest = error.config?.url?.endsWith('/auth/login');
    if (error.response?.status === 401 && !isLoginRequest) {
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    if (error.response?.status === 429) {
      const retryAfter = error.response.data?.retry_after_seconds || 60;
      toast.error(`Too many requests. Please wait ${retryAfter} seconds.`);
    }
    if (error.response?.status === 403) {
      const path = window.location.pathname;
      if (!path.startsWith('/portal/admin/')) {
        window.dispatchEvent(new CustomEvent('auth:navigate', { detail: '/error/403' }));
      }
    }
    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    if (error.code === 'ECONNABORTED') {
      toast.error('Request timed out. Please check your connection.');
    }
    return Promise.reject(error);
  }
);

export default api;

// ── In-memory API cache with TTL ──────────────────────────────────────────────
const apiCache = new Map();
const DEFAULT_TTL = 30_000; // 30 seconds

function getCacheKey(url, params) {
  return params ? `${url}?${JSON.stringify(params)}` : url;
}

export function clearCache(pattern) {
  if (!pattern) { apiCache.clear(); return; }
  for (const key of apiCache.keys()) {
    if (key.startsWith(pattern)) apiCache.delete(key);
  }
}

function cachedRequest(method, url, config = {}) {
  const key = getCacheKey(url, config.params);
  const ttl = config.ttl ?? DEFAULT_TTL;

  if (method === 'get' || method === 'GET') {
    const entry = apiCache.get(key);
    if (entry && Date.now() - entry.timestamp < ttl) {
      return Promise.resolve({ ...entry.response });
    }
  }

  return api[method](url, config).then(res => {
    if (method === 'get' || method === 'GET') {
      apiCache.set(key, { response: res, timestamp: Date.now(), ttl });
    }
    return res;
  });
}

export function prefetch(url, params = null, ttl = DEFAULT_TTL) {
  const key = getCacheKey(url, params);
  if (apiCache.has(key)) return Promise.resolve(apiCache.get(key).response);
  return api.get(url, { params }).then(res => {
    apiCache.set(key, { response: res, timestamp: Date.now(), ttl });
    return res;
  }).catch(() => {});
}

// Wrapped API methods with caching
export const cachedApi = {
  get: (url, config) => cachedRequest('get', url, config),
  post: (url, data, config) => {
    clearCache(url.split('/').slice(0, -1).join('/'));
    return api.post(url, data, config);
  },
  patch: (url, data, config) => {
    clearCache(url.split('/').slice(0, -1).join('/'));
    return api.patch(url, data, config);
  },
  delete: (url, config) => {
    clearCache(url.split('/').slice(0, -1).join('/'));
    return api.delete(url, config);
  },
};

// SWR fetcher using axios
const fetcher = async (url) => {
  const res = await api.get(url);
  return res.data;
};

const fetcherWithParams = ([url, params]) => api.get(url, { params }).then(r => r.data);

// Generic SWR hooks
export function useAPI(url, params = null) {
  const key = params ? [url, params] : url;
  return useSWR(key, params ? fetcherWithParams : fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 5000,
  });
}

export function usePaginatedAPI(url, page = 1, limit = 20) {
  return useSWR(
    [url, { page, limit }],
    fetcherWithParams,
    { revalidateOnFocus: false, dedupingInterval: 5000 }
  );
}

export function useMutation(url, options = {}) {
  return useSWRMutation(url, async (url, { arg }) => {
    const method = options.method || 'post';
    const res = await api[method](url, arg);
    return res.data;
  });
}

export function prefetchAPI(url, params = null) {
  const key = params ? [url, params] : url;
  mutate(key, fetcher(url));
}

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  verifyEmail: (data) => api.post('/auth/verify-email', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  verifyResetOtp: (data) => api.post('/auth/verify-reset-otp', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
  resendOtp: (data) => api.post('/auth/resend-otp', data),
  googleLogin: (data) => api.post('/auth/google', data),
  logout: () => api.post('/auth/logout'),
};

export const servicesAPI = {
  list: (category) => cachedApi.get('/services', { params: { category } }),
  get: (slug) => cachedApi.get(`/services/${slug}`),
  listAdmin: () => api.get('/admin/services'),
  create: (data) => api.post('/admin/services', data),
  update: (id, data) => api.patch(`/admin/services/${id}`, data),
  delete: (id) => api.delete(`/admin/services/${id}`),
  updatePricing: (id, tiers) => api.put(`/admin/services/${id}/pricing`, tiers),
};

export function useServices(category) {
  return useAPI('/services', category ? { category } : null);
}

export const ordersAPI = {
  create: (data) => api.post('/orders', data),
  bulkCreate: (data) => api.post('/orders/bulk', data),
  list: () => cachedApi.get('/orders'),
  get: (id) => cachedApi.get(`/orders/${id}`),
  update: (id, data) => api.patch(`/orders/${id}`, data),
  delete: (id) => api.delete(`/orders/${id}`),
};

export function useOrders(page = 1, limit = 20) {
  return usePaginatedAPI('/orders', page, limit);
}

export const paymentsAPI = {
  initialize: (data) => api.post('/payments/initialize', data),
  verify: (reference) => cachedApi.get(`/payments/verify/${reference}`),
  list: () => cachedApi.get('/payments'),
};

export const adminPaymentsAPI = {
  list: (params) => cachedApi.get('/admin/payments', { params }),
  get: (id) => api.get(`/admin/payments/${id}`),
  stats: (params) => cachedApi.get('/admin/payments/stats', { params }),
  refund: (data) => api.post('/admin/payments/refund', data),
  exportCsv: (params) => api.get('/admin/payments/export/csv', { params, responseType: 'blob' }),
  listRefunds: (params) => cachedApi.get('/admin/refunds', { params }),
};

export function usePayments(page = 1, limit = 20) {
  return usePaginatedAPI('/payments', page, limit);
}

export const walletAPI = {
  get: () => api.get('/wallet'),
  fund: (data) => api.post('/wallet/fund', data),
  verifyFund: (reference) => api.get(`/wallet/fund/verify/${reference}`),
  pay: (data) => api.post('/wallet/pay', data),
  transfer: (data) => api.post('/wallet/transfer', data),
  transactions: (params) => api.get('/wallet/transactions', { params }),
};

export const documentsAPI = {
  upload: (data) => api.post('/documents', data),
  list: (orderId) => api.get('/documents', { params: { order_id: orderId } }),
};

export const resourcesAPI = {
  list: (params) => api.get('/resources', { params }),
  get: (slug) => api.get(`/resources/${slug}`),
};

export const newsletterAPI = {
  subscribe: (data) => api.post('/newsletter/subscribe', data),
};

export function useResources(category, search) {
  const params = {};
  if (category) params.category = category;
  if (search) params.search = search;
  return useAPI('/resources', Object.keys(params).length ? params : null);
}

export const dashboardAPI = {
  getStats: () => cachedApi.get('/dashboard/stats'),
};

export function useDashboardStats() {
  return useAPI('/dashboard/stats');
}

export const aiAPI = {
  generateChecklist: (data) => api.post('/ai/checklist', data),
};

export const ticketsAPI = {
  create: (data) => api.post('/tickets', data),
  list: () => cachedApi.get('/tickets'),
  get: (id) => cachedApi.get(`/tickets/${id}`),
  update: (id, data) => api.patch(`/tickets/${id}`, data),
  addMessage: (id, data) => api.post(`/tickets/${id}/messages`, data),
};

export function useTickets(page = 1, limit = 20) {
  return usePaginatedAPI('/tickets', page, limit);
}

export function useTicket(id) {
  return useAPI(`/tickets/${id}`);
}

export const uploadAPI = {
  uploadTicketFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/ticket', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  uploadServiceDoc: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/service-doc', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const adminAPI = {
  getStats: () => cachedApi.get('/admin/stats'),
  listUsers: () => cachedApi.get('/admin/users'),
  getDeadlines: (days = 7) => cachedApi.get('/admin/deadlines', { params: { days } }),
  listTickets: (mine = true) => cachedApi.get('/admin/tickets', { params: { mine } }),
  listOrgs: (params) => cachedApi.get('/admin/orgs', { params }),
  getOrg: (id) => api.get(`/admin/orgs/${id}`),
  createOrg: (data) => api.post('/admin/orgs', data),
  updateOrg: (id, data) => api.patch(`/admin/orgs/${id}`, data),
  inviteToOrg: (orgId, data) => api.post(`/admin/orgs/${orgId}/invite`, data),
  assignHeadOfOps: (orgId, data) => api.post(`/admin/orgs/${orgId}/assign-head`, data),
  removeOrgMember: (orgId, data) => api.post(`/admin/orgs/${orgId}/remove-member`, data),
  regenerateOrgCode: (orgId) => api.post(`/admin/orgs/${orgId}/regenerate-code`),
  getPermSchema: () => api.get('/admin/permissions/schema'),
  getUserPermissions: (userId) => api.get(`/admin/users/${userId}/permissions`),
  setUserPermissions: (userId, permissions) => api.put(`/admin/users/${userId}/permissions`, { permissions }),
  patchUserPermissions: (userId, permissions) => api.patch(`/admin/users/${userId}/permissions`, { permissions }),
};

export function useAdminStats() {
  return useAPI('/admin/stats');
}

export const orderDocsAPI = {
  assign: (orderId, data) => api.post(`/orders/${orderId}/assign`, data),
  submitDocument: (orderId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/orders/${orderId}/submit-document`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  listDocuments: (orderId) => api.get(`/orders/${orderId}/documents`),
  review: (orderId, data) => api.post(`/orders/${orderId}/review`, data),
  remind: (orderId) => api.post(`/orders/${orderId}/remind`),
  assignReviewers: (orderId, reviewerIds) => api.post(`/orders/${orderId}/assign-reviewers`, { reviewer_ids: reviewerIds }),
  listAdminOrders: (mine = false, status = null) => cachedApi.get('/admin/orders', { params: { mine, ...(status ? { status } : {}) } }),
  listUnassigned: (page = 1, limit = 20) => cachedApi.get('/admin/orders/unassigned', { params: { page, limit } }),
  pickJob: (orderId) => api.post(`/admin/orders/${orderId}/pick`),
  getOrderOverview: (orderId) => cachedApi.get(`/admin/orders/${orderId}/overview`),
  getOrderTickets: (orderId) => cachedApi.get(`/admin/orders/${orderId}/tickets`),
};

export const orgAPI = {
  create: (data) => api.post('/org/create', data),
  join: (data) => api.post('/org/join', data),
  addMember: (data) => api.post('/org/add-member', data),
  getMyOrg: () => api.get('/org/my'),
  listMembers: () => api.get('/org/members'),
  getCode: () => api.get('/org/code'),
  regenerateCode: () => api.post('/org/regenerate-code'),
  leave: () => api.post('/org/leave'),
  removeMember: (userId) => api.post(`/org/remove-member/${userId}`),
  acceptInvite: (token) => api.post('/org/accept-invite', { token }),
  getInviteInfo: (token) => api.get(`/org/invite-info/${token}`),
};

export const workflowAPI = {
  getQueue: (params) => cachedApi.get('/workflow/queue', { params }),
  getKanban: () => cachedApi.get('/workflow/kanban'),
  updateStatus: (jobId, data) => api.patch(`/workflow/${jobId}/status`, data),
  getAudit: (jobId) => cachedApi.get(`/workflow/${jobId}/audit`),
  addComment: (jobId, data) => api.post(`/workflow/${jobId}/comment`, data),
  getAnalytics: () => cachedApi.get('/workflow/analytics'),
  getWorkload: () => cachedApi.get('/workflow/workload'),
  escalate: (jobId, data) => api.post(`/workflow/${jobId}/escalate`, data),
  listEscalations: (params) => cachedApi.get('/workflow/escalations', { params }),
  resolveEscalation: (escId, data) => api.patch(`/workflow/escalations/${escId}/resolve`, data),
  getReviewQueue: (params) => cachedApi.get('/workflow/review-queue', { params }),
  submitReview: (jobId, data) => api.post(`/workflow/${jobId}/review`, data),
  getOverview: () => cachedApi.get('/workflow/overview'),
  getTeamTasks: () => cachedApi.get('/workflow/team-tasks'),
};

export async function downloadFile(url, filename) {
  const response = await fetch(`${API_URL}${url}`, {
    credentials: 'include',
  });
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    toast.error(`Download failed (${response.status}): ${text}`);
    return;
  }
  const blob = await response.blob();
  const blobUrl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(blobUrl);
}
