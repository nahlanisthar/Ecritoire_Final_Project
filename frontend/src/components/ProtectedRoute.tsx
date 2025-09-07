import React from 'react';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import AuthForm from './AuthForm';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <AuthForm />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;