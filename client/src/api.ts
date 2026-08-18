import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

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

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config as
      | (typeof error.config & { _retry?: boolean })
      | undefined;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refresh");

      if (!refreshToken) {
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(
          `${API_URL}/api/auth/refresh/`,
          {
            refresh: refreshToken,
          }
        );

        const newAccessToken = response.data.access;

        localStorage.setItem(
          "access",
          newAccessToken
        );

        originalRequest.headers.Authorization =
          `Bearer ${newAccessToken}`;

        return api(originalRequest);

      } catch (refreshError) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;