import api from "./axios";

// The backend URL the browser should be sent to for the Google OAuth flow.
// This must be a real full-page navigation (not an axios call) because
// Google redirects the browser itself, not a JS fetch.
const API_BASE_URL = "https://ai-productivity-assistant-rszk.onrender.com";

export const getGoogleLoginUrl = () => `${API_BASE_URL}/auth/login`;

export const getMe = async () => {
  const response = await api.get("/auth/me");
  return response.data;
};
