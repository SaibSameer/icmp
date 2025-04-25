import React, { createContext, useContext, useState, useEffect } from 'react';
import { isLoggedIn, getStoredCredentials, logout } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState('');
  const [businessId, setBusinessId] = useState('');
  const [businessApiKey, setBusinessApiKey] = useState('');

  useEffect(() => {
    // Check if user is logged in on component mount
    const loggedIn = isLoggedIn();
    if (loggedIn) {
      const { userId, businessId, businessApiKey } = getStoredCredentials();
      setUserId(userId);
      setBusinessId(businessId);
      setBusinessApiKey(businessApiKey);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogout = () => {
    logout();
    setUserId('');
    setBusinessId('');
    setBusinessApiKey('');
    setIsAuthenticated(false);
  };

  const value = {
    isAuthenticated,
    userId,
    businessId,
    businessApiKey,
    setUserId,
    setBusinessId,
    setBusinessApiKey,
    setIsAuthenticated,
    handleLogout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};