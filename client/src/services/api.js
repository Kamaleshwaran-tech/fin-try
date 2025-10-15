// Centralized API service using Axios
// Reads base URL from VUE_APP_API_BASE_URL or defaults to localhost:5000
import axios from 'axios';

const baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000';

const http = axios.create({
  baseURL,
  timeout: 20000,
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error?.response?.data?.message || error.message || 'Network error';
    return Promise.reject(new Error(message));
  }
);

export const api = {
  extract(payload) {
    // payload: { date_from, date_to, sources: [], keyword }
    return http.post('/extract', payload);
  },
  analyze(payload) {
    // payload: { articles: [...]} or { date_from, ... }
    return http.post('/analyze', payload);
  },
  visualize(params) {
    // params: { date_from, date_to, sources, keyword }
    return http.get('/visualize', { params });
  },
};

export default api;
