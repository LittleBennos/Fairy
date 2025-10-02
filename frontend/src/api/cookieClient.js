import axios from 'axios';

/**
 * Enhanced API client with httpOnly cookie authentication support.
 * This provides better security than localStorage/sessionStorage.
 */

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // CRITICAL: Enable sending cookies with requests
});

// Store CSRF token in memory (not localStorage for security)
let csrfToken = null;

/**
 * Get CSRF token from cookie
 */
const getCsrfTokenFromCookie = () => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; csrftoken=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
};

/**
 * Get CSRF token from the server
 */
export const getCsrfToken = async () => {
  try {
    // First try to get from cookie
    csrfToken = getCsrfTokenFromCookie();
    if (csrfToken) {
      return csrfToken;
    }

    // If not in cookie, fetch from server
    const response = await apiClient.get('/auth/csrf/');
    csrfToken = response.data.csrfToken;
    return csrfToken;
  } catch (error) {
    console.error('Failed to get CSRF token:', error);
    throw error;
  }
};

/**
 * Initialize the client (get CSRF token)
 */
export const initializeAuth = async () => {
  await getCsrfToken();
};

// Request interceptor to add CSRF token
apiClient.interceptors.request.use(
  async (config) => {
    // Add CSRF token for non-safe methods
    if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(config.method.toUpperCase())) {
      if (!csrfToken) {
        await getCsrfToken();
      }
      config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Try to refresh the token
      try {
        await apiClient.post('/auth/refresh/');
        // Retry original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login only if not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        // Re-throw the error so the calling code can handle it
        return Promise.reject(refreshError);
      }
    }

    // Handle 403 CSRF failure
    if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
      // Get new CSRF token and retry
      if (!originalRequest._csrfRetry) {
        originalRequest._csrfRetry = true;
        await getCsrfToken();
        return apiClient(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Authentication API methods
 */
export const authAPI = {
  /**
   * Login with username and password
   */
  login: async (username, password) => {
    const response = await apiClient.post('/auth/cookie/login/', {
      username,
      password
    });
    return response.data;
  },

  /**
   * Logout the current user
   */
  logout: async () => {
    const response = await apiClient.post('/auth/cookie/logout/');
    return response.data;
  },

  /**
   * Register a new user
   */
  register: async (userData) => {
    const response = await apiClient.post('/auth/register/', userData);
    return response.data;
  },

  /**
   * Get current user info
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me/');
    return response.data;
  },

  /**
   * Change password
   */
  changePassword: async (oldPassword, newPassword) => {
    const response = await apiClient.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword
    });
    return response.data;
  },

  /**
   * Refresh access token
   */
  refreshToken: async () => {
    const response = await apiClient.post('/auth/cookie/refresh/');
    return response.data;
  }
};

export default apiClient;