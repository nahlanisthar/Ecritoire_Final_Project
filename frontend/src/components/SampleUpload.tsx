import React, { useState } from 'react';
import { 
  Box, Paper, Typography, TextField, Button, Alert, List, 
  ListItem, ListItemText, IconButton, CircularProgress, Chip 
} from '@mui/material';
import { Delete as DeleteIcon, Upload as UploadIcon } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

interface WritingSample {
  id: number;
  title: string;
  content: string;
  uploaded_at: string;
  analyzed: boolean;
}

interface SampleUploadProps {
  onSamplesUpdated: () => void;
}

const SampleUpload: React.FC<SampleUploadProps> = ({ onSamplesUpdated }) => {
  const { token, logout } = useAuth();
  const [samples, setSamples] = useState<WritingSample[]>([]);
  const [newSample, setNewSample] = useState({ title: '', content: '' });
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleAuthError = async (response: Response) => {
    if (response.status === 401) {
      try {
        const err = await response.json();
        if (err.detail && err.detail.toLowerCase().includes("expired")) {
          logout();
          setMessage({ type: 'error', text: 'Session expired. Please log in again.' });
        } else {
          setMessage({ type: 'error', text: err.detail || 'Unauthorized' });
        }
      } catch {
        setMessage({ type: 'error', text: 'Unauthorized' });
      }
      return true;
    }
    return false;
  };

  const uploadSample = async () => {
    if (!newSample.title.trim() || !newSample.content.trim()) {
      setMessage({ type: 'error', text: 'Please provide both title and content' });
      return;
    }
    if (newSample.content.length < 50) {
      setMessage({ type: 'error', text: 'Content must be at least 50 characters long' });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/samples/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newSample)
      });

      if (await handleAuthError(response)) return;

      if (response.ok) {
        setNewSample({ title: '', content: '' });
        setMessage({ type: 'success', text: 'Writing sample uploaded successfully!' });
        loadSamples();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Upload failed' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const loadSamples = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/samples/user`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (await handleAuthError(response)) return;

      if (response.ok) {
        const samplesData = await response.json();
        setSamples(samplesData);
      }
    } catch (error) {
      console.error('Failed to load samples:', error);
    }
  };

  const analyzeSamples = async () => {
    if (samples.length === 0) {
      setMessage({ type: 'error', text: 'Please upload at least 1 writing sample first' });
      return;
    }

    setAnalyzing(true);
    try {
      const response = await fetch(`http://localhost:8000/api/samples/analyze`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (await handleAuthError(response)) return;

      if (response.ok) {
        const result = await response.json();
        setMessage({
          type: 'success',
          text: `Analysis complete! Built style profile from ${result.style_profile.sample_count} samples.`
        });
        loadSamples();
        onSamplesUpdated();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Analysis failed' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Network error during analysis' });
    } finally {
      setAnalyzing(false);
    }
  };

  const deleteSample = async (sampleId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/samples/sample/${sampleId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (await handleAuthError(response)) return;

      if (response.ok) {
        setMessage({ type: 'success', text: 'Sample deleted successfully' });
        loadSamples();
      }
    } catch {
      setMessage({ type: 'error', text: 'Failed to delete sample' });
    }
  };

  React.useEffect(() => {
    loadSamples();
  }, []);

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom sx={{fontFamily: '"Sansita", sans-serif'}}>
        Upload Your Writing Samples
        </Typography>

        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          Upload 5+ diverse writing samples (emails, essays, stories, etc.) so Écritoire can learn your unique voice and style.
        </Typography>

        {message && (
          <Alert severity={message.type} sx={{ mb: 2 }}>
            {message.text}
          </Alert>
        )}

        <TextField
          fullWidth
          label="Sample Title"
          value={newSample.title}
          onChange={(e) => setNewSample({ ...newSample, title: e.target.value })}
          sx={{ mb: 2 }}
          placeholder="e.g., 'Email to colleague', 'Personal journal entry', 'Essay about travel'"
        />

        <TextField
          fullWidth
          multiline
          rows={8}
          label="Writing Content"
          value={newSample.content}
          onChange={(e) => setNewSample({ ...newSample, content: e.target.value })}
          sx={{ mb: 2 }}
          placeholder="Paste your writing here... (minimum 50 characters)"
          helperText={`${newSample.content.length} characters (minimum 50 required)`}
        />

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Button
            variant="contained"
            onClick={uploadSample}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <UploadIcon />}
          >
            {loading ? 'Uploading...' : 'Upload Sample'}
          </Button>

          <Button
            variant="outlined"
            color="secondary"
            onClick={analyzeSamples}
            disabled={analyzing || samples.length === 0}
            startIcon={analyzing ? <CircularProgress size={20} /> : null}
          >
            {analyzing ? 'Analyzing...' : `Analyze ${samples.length} Samples`}
          </Button>
        </Box>
      </Paper>

      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{fontFamily: '"Sansita", sans-serif'}}>
          Your Writing Samples ({samples.length})
        </Typography>

        {samples.length === 0 ? (
          <Typography color="textSecondary">
            No writing samples uploaded yet. Upload some samples to get started!
          </Typography>
        ) : (
          <List>
            {samples.map((sample) => (
              <ListItem key={sample.id} sx={{ border: '1px solid #eee', mb: 1, borderRadius: 1 }}>
                <ListItemText
                  primary={sample.title}
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        {sample.content.length} characters • {new Date(sample.uploaded_at).toLocaleDateString()}
                      </Typography>
                      <Chip
                        label={sample.analyzed ? "Analyzed" : "Not analyzed"}
                        color={sample.analyzed ? "success" : "default"}
                        size="small"
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  }
                />
                <IconButton onClick={() => deleteSample(sample.id)} color="error">
                  <DeleteIcon />
                </IconButton>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Box>
  );
};

export default SampleUpload;
