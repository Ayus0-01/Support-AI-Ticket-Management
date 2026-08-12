import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

console.log("API URL:", import.meta.env.VITE_API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");

  const publicEndpoints = [
    "/api/auth/login/",
    "/api/auth/register/",
  ];
  

  const isPublicEndpoint = publicEndpoints.includes(config.url || "");

  if (token && !isPublicEndpoint) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;