const API_URL =
  "https://support-ai-ticket-management-team-18k9.onrender.com";

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = localStorage.getItem("access");

  const headers = new Headers(options.headers);

  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });
}