import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Link
} from '@mui/material';
import { useAuth } from '../context/AuthContext';

const AuthForm: React.FC = () => {
  const { login, signup } = useAuth();
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleTabChange = (event: React.SyntheticEvent, newValue: 'login' | 'signup') => {
    setActiveTab(newValue);
    setError('');
    setFormData({ email: '', password: '', confirmPassword: '' });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validateForm = (): string | null => {
    if (!formData.email || !formData.password) {
      return 'Please fill in all fields';
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      return 'Please enter a valid email address';
    }

    if (formData.password.length < 6) {
      return 'Password must be at least 6 characters long';
    }

    if (activeTab === 'signup' && formData.password !== formData.confirmPassword) {
      return 'Passwords do not match';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (activeTab === 'login') {
        await login(formData.email, formData.password);
      } else {
        await signup(formData.email, formData.password);
      }
    } catch (error: any) {
      setError(error.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundImage: 'url("/images/image_4.jpeg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
        p: 2
      }}
    >
      <Paper
        elevation={10}
        sx={{
          p: 4,
          maxWidth: 400,
          width: '100%',
          borderRadius: 3,
          backgroundColor: 'rgba(255, 255, 255, 0.20)',
          backdropFilter: 'blur(10px)'
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <Typography variant="h4"
            sx={{
              flexGrow: 1,
              fontWeight: 'bold',
              fontFamily: '"Javanese Text", serif',
              color: '#f7e093ff'
            }}>
            ÉCRITOIRE
          </Typography>
          <Typography variant="body2" color='white'>
            Your Personal AI Writing Assistant
          </Typography>
        </Box>

        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            mb: 3,
            '& .MuiTab-root': {
              color: '#4f3201ff',
            },
            '& .MuiTabs-indicator': {
              backgroundColor: 'white',
            },
            '& .MuiTab-root.Mui-selected': {
              color: 'white',
            }
          }}
        >
          <Tab label="Login" value="login" />
          <Tab label="Sign Up" value="signup" />
        </Tabs>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            name="email"
            type="email"
            label="Email Address"
            value={formData.email}
            onChange={handleInputChange}
            margin="normal"
            required
            autoComplete="email"
            autoFocus
            sx={{
              '& .MuiOutlinedInput-root': {
                color: 'black',
                '& fieldset': {
                  borderColor: 'white',
                },
                '&:hover fieldset': {
                  borderColor: 'white',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'white',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'white',
              },
              '& .MuiInputLabel-root.Mui-focused': {
                color: 'white',
              },
            }}
          />

          <TextField
            fullWidth
            name="password"
            type="password"
            label="Password"
            value={formData.password}
            onChange={handleInputChange}
            margin="normal"
            required
            autoComplete={activeTab === 'login' ? 'current-password' : 'new-password'}
            helperText={activeTab === 'signup' ? 'Must be at least 6 characters' : ''}
            FormHelperTextProps={{
              sx: {
                color: 'white', 
              },
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: 'black',
                '& fieldset': {
                  borderColor: 'white',
                },
                '&:hover fieldset': {
                  borderColor: 'white',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'white',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'white',
              },
              '& .MuiInputLabel-root.Mui-focused': {
                color: 'white',
              },
            }}
          />

          {activeTab === 'signup' && (
            <TextField
              fullWidth
              name="confirmPassword"
              type="password"
              label="Confirm Password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              margin="normal"
              required
              autoComplete="new-password"
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'black',
                  '& fieldset': {
                    borderColor: 'white',
                  },
                  '&:hover fieldset': {
                    borderColor: 'white',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'white',
                  },
                },
                '& .MuiInputLabel-root': {
                  color: 'white',
                },
                '& .MuiInputLabel-root.Mui-focused': {
                  color: 'white',
                },
              }}
            />
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={loading}
            sx={{
              mt: 3,
              mb: 2,
              py: 1.5,
              background: '#E2D2B9',
              color: 'black',
              '&:hover': {
                background: '#4f3201ff',
                color: 'white'
              }
            }}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              activeTab === 'login' ? 'Login' : 'Create Account'
            )}
          </Button>
        </form>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2" color="white">
            {activeTab === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <Link
              component="button"
              type="button"
              onClick={() => handleTabChange({} as React.SyntheticEvent, activeTab === 'login' ? 'signup' : 'login')}
              sx={{ textDecoration: 'underline', cursor: 'pointer', color: '#000000', }}
            >
              {activeTab === 'login' ? 'Sign up here' : 'Sign in here'}
            </Link>
          </Typography>
        </Box>

        {activeTab === 'signup' && (
          <Box sx={{ mt: 3 }}>
            <Alert
              severity="info"
              sx={{
                fontSize: '0.875rem',
                background: 'rgba(255, 255, 255, 0.15)',
                color: 'white',
                '& .MuiAlert-icon': {
                  color: '#EEC954', 
                },
              }}
            >
              By creating an account, you agree to upload writing samples to help Écritoire learn your unique writing style.
            </Alert>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default AuthForm;