import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Card, CardContent, LinearProgress, Chip, Alert, CircularProgress, List, ListItem, ListItemText, ListItemIcon, Divider } from '@mui/material';
import { TrendingUp, Psychology, Timeline, AutoAwesome, CheckCircle, Edit, Cancel, Description } from '@mui/icons-material';
import axios from 'axios';

interface StyleProfile {
  user_id: number;
  vocabulary_level: string;
  formality_preference: string;
  sentence_complexity: number;
  sample_count: number;
  emotional_patterns: any;
  word_preferences: any;
  created_at: string;
  updated_at: string;
}

interface UserStats {
  total_generations: number;
  accepted: number;
  modified: number;
  rejected: number;
  acceptance_rate: number;
  modification_rate: number;
}

interface UserStatsResponse {
  success: boolean;
  stats: UserStats;
}

interface WritingSample {
  id: number;
  title: string;
  content: string;
  uploaded_at: string;
  analyzed: boolean;
}

interface DashboardProps {
  samplesUpdated: number;
}

const Dashboard: React.FC<DashboardProps> = ({ samplesUpdated }) => {
  const [styleProfile, setStyleProfile] = useState<StyleProfile | null>(null);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [samples, setSamples] = useState<WritingSample[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, [samplesUpdated]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Loading style profile
      try {
        const profileResponse = await axios.get<StyleProfile>('http://localhost:8000/api/samples/profile');
        setStyleProfile(profileResponse.data);
      } catch (profileError) {
        setStyleProfile(null);
      }

      // Loading user stats
      try {
        const statsResponse = await axios.get<UserStatsResponse>('http://localhost:8000/api/generate/stats');
        if (statsResponse.data.success) {
          setUserStats(statsResponse.data.stats);
        }
      } catch (statsError) {
        setUserStats(null);
      }

      // Loading samples
      try {
        const samplesResponse = await axios.get<WritingSample[]>('http://localhost:8000/api/samples/user');
        setSamples(samplesResponse.data);
      } catch (samplesError) {
        setSamples([]);
      }

    } catch (err: any) {
      setError('Failed to load dashboard data');
    }

    setLoading(false);
  };

  const getAcceptanceRateColor = (rate: number) => {
    if (rate >= 70) return 'success';
    if (rate >= 40) return 'warning';
    return 'error';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', mt: 2, display: 'grid', gap: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, fontFamily: '"Sansita", sans-serif' }}>
        Writing Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center' }}>
            <AutoAwesome sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" color="primary">{userStats?.total_generations || 0}</Typography>
            <Typography variant="body2" color="textSecondary">Total Generations</Typography>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center' }}>
            <CheckCircle sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" color="success.main">{userStats?.acceptance_rate?.toFixed(1) || 0}%</Typography>
            <Typography variant="body2" color="textSecondary">Acceptance Rate</Typography>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Psychology sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" color="info.main">{samples.length}</Typography>
            <Typography variant="body2" color="textSecondary">Writing Samples</Typography>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Timeline sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
            <Typography variant="h4" color="warning.main">{samples.filter(s => s.analyzed).length}</Typography>
            <Typography variant="body2" color="textSecondary">Samples Analyzed</Typography>
          </CardContent>
        </Card>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3 }}>
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, fontFamily: '"Sansita", sans-serif' }}>
            <Psychology color="primary" />
            Your Writing Style Profile
          </Typography>

          {styleProfile ? (
            <Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2, mb: 3 }}>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">Formality Preference</Typography>
                  <Chip label={styleProfile.formality_preference.charAt(0).toUpperCase() + styleProfile.formality_preference.slice(1)} color="primary" variant="outlined" />
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">Vocabulary Level</Typography>
                  <Chip label={styleProfile.vocabulary_level.charAt(0).toUpperCase() + styleProfile.vocabulary_level.slice(1)} color="secondary" variant="outlined" />
                </Box>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>Average Sentence Length</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((styleProfile.sentence_complexity / 25) * 100, 100)}
                    sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                    color={
                      styleProfile.sentence_complexity < 12 ? 'success' :
                        styleProfile.sentence_complexity < 20 ? 'warning' : 'error'
                    }
                  />
                  <Typography variant="body2">{styleProfile.sentence_complexity.toFixed(1)} words</Typography>
                </Box>
              </Box>

              <Typography variant="body2" color="textSecondary">
                Profile built from {styleProfile.sample_count} writing samples
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Last updated: {formatDate(styleProfile.updated_at)}
              </Typography>
            </Box>
          ) : (
            <Alert severity="info">
              No style profile available. Upload and analyze writing samples to build your profile.
            </Alert>
          )}
        </Paper>

        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, fontFamily: '"Sansita", sans-serif' }}>
            <TrendingUp color="primary" />
            Generation Stats
          </Typography>

          {userStats ? (
            <Box>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Acceptance Rate</Typography>
                  <Typography variant="body2" fontWeight="bold">{userStats.acceptance_rate.toFixed(1)}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={userStats.acceptance_rate}
                  color={getAcceptanceRateColor(userStats.acceptance_rate)}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Modification Rate</Typography>
                  <Typography variant="body2" fontWeight="bold">{userStats.modification_rate.toFixed(1)}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={userStats.modification_rate}
                  color="info"
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <List dense>
                <ListItem>
                  <ListItemIcon><CheckCircle color="success" fontSize="small" /></ListItemIcon>
                  <ListItemText primary="Accepted" secondary={`${userStats.accepted} generations`} />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Edit color="info" fontSize="small" /></ListItemIcon>
                  <ListItemText primary="Modified" secondary={`${userStats.modified} generations`} />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Cancel color="error" fontSize="small" /></ListItemIcon>
                  <ListItemText primary="Rejected" secondary={`${userStats.rejected} generations`} />
                </ListItem>
              </List>
            </Box>
          ) : (
            <Alert severity="info">
              No generation statistics available yet. Start generating content to see your stats.
            </Alert>
          )}
        </Paper>
      </Box>

      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, fontFamily: '"Sansita", sans-serif' }}>
          <Description color="primary" />
          Your Writing Samples
        </Typography>

        {samples.length > 0 ? (
          <List>
            {samples.slice(0, 5).map((sample, index) => (
              <React.Fragment key={sample.id}>
                <ListItem>
                  <ListItemText
                    primary={sample.title}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {sample.content.length} characters • Uploaded {formatDate(sample.uploaded_at)}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Chip label={sample.analyzed ? "Analyzed" : "Not analyzed"} color={sample.analyzed ? "success" : "default"} size="small" />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
                {index < Math.min(samples.length - 1, 4) && <Divider />}
              </React.Fragment>
            ))}
          </List>
        ) : (
          <Alert severity="info">
            No writing samples uploaded yet. Upload samples to build your writing profile.
          </Alert>
        )}

        {samples.length > 5 && (
          <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
            Showing 5 of {samples.length} samples
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default Dashboard;