import axios from "axios";

// Build backend base URL: prefer explicit env, then same host:8000
const explicit = process.env.REACT_APP_API_URL;
const inferred = `${window.location.protocol}//${window.location.hostname}:8000`;
const baseURL = explicit || inferred;

const api = axios.create({ baseURL });

// Attach JWT automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Optional: handle 401s globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/";
    }
    return Promise.reject(err);
  }
);

export default api;
