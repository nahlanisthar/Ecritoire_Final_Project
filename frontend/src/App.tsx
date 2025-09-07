import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Button, Box, Tabs, Tab, Paper, IconButton } from '@mui/material';
import { Edit as EditIcon, Dashboard as DashboardIcon, Upload as UploadIcon, Logout as LogoutIcon } from '@mui/icons-material';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import WritingInterface from './components/WritingInterface';
import Dashboard from './components/Dashboard';
import SampleUpload from './components/SampleUpload';

// Navigation components
function NavigationTabs() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    navigate(newValue);
  };

  const getCurrentTab = () => {
    const path = location.pathname;
    if (path === '/dashboard') return '/dashboard';
    if (path === '/upload') return '/upload';
    return '/';
  };

  return (
    <Paper elevation={2} sx={{ mb: 3, background: "black" }}>
      <Tabs
        value={getCurrentTab()}
        onChange={handleTabChange}
        centered
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          '& .MuiTab-root': {
            color: '#E2D2B9',          
          },
          '& .Mui-selected': {
            color: '#EEC954 !important', 
          },
          '& .MuiTabs-indicator': {
            backgroundColor: '#EEC954', 
          },
        }}
      >
        <Tab
          value="/"
          label="Writing Studio"
          icon={<EditIcon />}
          iconPosition="start"
        />
        <Tab
          value="/upload"
          label="Upload Samples"
          icon={<UploadIcon />}
          iconPosition="start"
        />
        <Tab
          value="/dashboard"
          label="Dashboard"
          icon={<DashboardIcon />}
          iconPosition="start"
        />
      </Tabs>
    </Paper>
  );
}

// Main app content with navigation
function AppContent() {
  const { user, logout } = useAuth();
  const [samplesUpdated, setSamplesUpdated] = useState(0);

  const handleSamplesUpdated = () => {
    setSamplesUpdated(prev => prev + 1);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="App">
      <AppBar position="static" sx={{ mb: 4, background: 'black' }}>
        <Toolbar>
          <Typography
            variant="h5"
            component="div"
            sx={{
              flexGrow: 1,
              fontWeight: 'bold',
              fontFamily: '"Javanese Text", serif',
              color: '#EEC954'
            }}
          >
            ÉCRITOIRE
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" color="inherit" sx={{ opacity: 0.9 }}>
              Welcome, {user?.email}
            </Typography>
            <Button
              color="inherit"
              onClick={handleLogout}
              startIcon={<LogoutIcon />}
              sx={{
                opacity: 0.9,
                '&:hover': { opacity: 1 },
                color: '#EEC954'
              }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mb: 4, background: 'white' }}>
        <NavigationTabs />

        <Routes>
          <Route
            path="/"
            element={
              <WritingInterface
                samplesUpdated={samplesUpdated}
              />
            }
          />
          <Route
            path="/upload"
            element={
              <SampleUpload
                onSamplesUpdated={handleSamplesUpdated}
              />
            }
          />
          <Route
            path="/dashboard"
            element={
              <Dashboard
                samplesUpdated={samplesUpdated}
              />
            }
          />
        </Routes>
      </Container>
    </div>
  );
}

// Main App component
function App() {
  return (
    <AuthProvider>
      <Router>
        <ProtectedRoute>
          <AppContent />
        </ProtectedRoute>
      </Router>
    </AuthProvider>
  );
}

export default App;