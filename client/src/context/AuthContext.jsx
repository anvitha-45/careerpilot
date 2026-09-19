import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('careerpilot_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('careerpilot_token'));
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/profile');
      setProfile(res.data);
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('careerpilot_token', access_token);
    localStorage.setItem('careerpilot_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    await fetchProfile();
    return userData;
  };

  const register = async (name, email, password) => {
    const res = await api.post('/auth/register', { name, email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('careerpilot_token', access_token);
    localStorage.setItem('careerpilot_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    await fetchProfile();
    return userData;
  };

  const loginWithGoogle = async (googleData) => {
    const res = await api.post('/auth/google', googleData);
    const { access_token, user: userData } = res.data;
    localStorage.setItem('careerpilot_token', access_token);
    localStorage.setItem('careerpilot_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    await fetchProfile();
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('careerpilot_token');
    localStorage.removeItem('careerpilot_user');
    setToken(null);
    setUser(null);
    setProfile(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, profile, loading, login, register, loginWithGoogle, logout, refreshProfile: fetchProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

