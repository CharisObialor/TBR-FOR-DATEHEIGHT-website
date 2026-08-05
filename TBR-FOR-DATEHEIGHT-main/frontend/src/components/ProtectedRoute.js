import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Preloader } from './ui/preloader';

const ProtectedRoute = ({ children, roles = [] }) => {
  const { isAuthenticated, hasRole, loading } = useAuth();

  if (loading) {
    return <Preloader fullPage message="Verifying access..." />;
  }

  if (!isAuthenticated()) {
    return <Navigate to="/portal/login" replace />;
  }

  if (roles.length > 0 && !hasRole(...roles)) {
    return <Navigate to="/portal/dashboard" replace />;
  }

  return children;
};

export default ProtectedRoute;
