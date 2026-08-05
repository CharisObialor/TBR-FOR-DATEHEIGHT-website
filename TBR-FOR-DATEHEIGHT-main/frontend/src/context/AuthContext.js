import React, { createContext, useState, useContext, useEffect, useCallback, useRef } from 'react';
import { authAPI } from '../lib/api';

const AuthContext = createContext(null);
const USER_CACHE_KEY = 'cached_user';
const LAST_ACTIVE_KEY = 'last_active_timestamp';
const SESSION_DURATION_MS = 30 * 60 * 1000;

const recordActivity = () => {
  localStorage.setItem(LAST_ACTIVE_KEY, Date.now().toString());
};

const getInactiveDuration = () => {
  const stored = localStorage.getItem(LAST_ACTIVE_KEY);
  if (!stored) return 0;
  return Date.now() - parseInt(stored, 10);
};

const isSessionExpired = () => getInactiveDuration() >= SESSION_DURATION_MS;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

function getCachedUser() {
  if (isSessionExpired()) {
    localStorage.removeItem(USER_CACHE_KEY);
    localStorage.removeItem(LAST_ACTIVE_KEY);
    return null;
  }
  try {
    const raw = localStorage.getItem(USER_CACHE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    localStorage.removeItem(USER_CACHE_KEY);
  }
  return null;
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(getCachedUser);
  const [loading, setLoading] = useState(() => !getCachedUser());
  const idleCheckRef = useRef(null);
  const activityRef = useRef(null);

  const doLogout = useCallback(async () => {
    localStorage.removeItem(USER_CACHE_KEY);
    localStorage.removeItem(LAST_ACTIVE_KEY);
    setUser(null);
    try {
      await authAPI.logout();
    } catch {
      // ignore
    }
  }, []);

  const fetchUser = useCallback(async () => {
    try {
      const res = await authAPI.getMe();
      const userData = res.data;
      localStorage.setItem(USER_CACHE_KEY, JSON.stringify(userData));
      recordActivity();
      setUser(userData);
    } catch {
      localStorage.removeItem(USER_CACHE_KEY);
      setUser(null);
    }
  }, []);

  useEffect(() => {
    if (isSessionExpired()) {
      localStorage.removeItem(USER_CACHE_KEY);
      setLoading(false);
      return;
    }
    fetchUser().finally(() => setLoading(false));
  }, [fetchUser]);

  useEffect(() => {
    const handler = () => { doLogout(); };
    window.addEventListener('auth:unauthorized', handler);
    return () => window.removeEventListener('auth:unauthorized', handler);
  }, [doLogout]);

  useEffect(() => {
    if (!user) return;

    recordActivity();

    const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];
    const handleActivity = () => recordActivity();
    events.forEach((e) => window.addEventListener(e, handleActivity, { passive: true }));
    activityRef.current = handleActivity;

    const handleVisibility = () => {
      if (document.visibilityState === 'visible' && isSessionExpired()) {
        doLogout();
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);

    idleCheckRef.current = setInterval(() => {
      if (isSessionExpired()) {
        doLogout();
      }
    }, 30_000);

    return () => {
      events.forEach((e) => window.removeEventListener(e, handleActivity));
      document.removeEventListener('visibilitychange', handleVisibility);
      if (idleCheckRef.current) clearInterval(idleCheckRef.current);
    };
  }, [user, doLogout]);

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password });
    const { user: userData, pending_invite } = response.data;
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(userData));
    recordActivity();
    setUser(userData);
    return { user: userData, pendingInvite: pending_invite };
  };

  const googleLogin = async (credential) => {
    const response = await authAPI.googleLogin({ credential });
    const { user: userData } = response.data;
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(userData));
    recordActivity();
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    localStorage.removeItem(USER_CACHE_KEY);
    localStorage.removeItem(LAST_ACTIVE_KEY);
    setUser(null);
    try {
      await authAPI.logout();
    } catch {
      // ignore
    }
  };

  const isAuthenticated = () => !!user;

  const hasRole = (...roles) => user && roles.includes(user.role);

  const hasPermission = (key) => {
    if (!user) return false;
    if (user.role === 'super_admin') return true;
    return !!(user.permissions && user.permissions[key]);
  };

  const hasAnyPermission = (keys) => {
    if (!user) return false;
    if (user.role === 'super_admin') return true;
    return keys.some(k => user.permissions && user.permissions[k]);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        googleLogin,
        logout,
        isAuthenticated,
        hasRole,
        hasPermission,
        hasAnyPermission,
        fetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
