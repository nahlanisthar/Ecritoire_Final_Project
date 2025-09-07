import React, { useState, useEffect } from 'react';
import { Box, TextField, Typography, Button, Alert, Paper, Card, CardContent, FormControl, InputLabel, Select, MenuItem, Chip, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tooltip } from '@mui/material';
import { Send as SendIcon, ThumbUp, ThumbDown, Edit as EditIcon, History as HistoryIcon, AutoAwesome as AIIcon } from '@mui/icons-material';
import axios from 'axios';

interface ApiHealthResponse {
  status: string;
  service?: string;
  version?: string;
}

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

interface GeneratedContent {
  success: boolean;
  generated_content: string;
  content_id: number;
  message: string;
}

interface FeedbackResponse {
  success: boolean;
  message: string;
}

interface GenerationHistory {
  id: number;
  prompt: string;
  generated_text: string;
  user_feedback: string | null;
  created_at: string;
  has_modifications: boolean;
}

interface WritingInterfaceProps {
  samplesUpdated: number;
}

const WritingInterface: React.FC<WritingInterfaceProps> = ({ samplesUpdated }) => {
  const [prompt, setPrompt] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [currentContentId, setCurrentContentId] = useState<number | null>(null);
  const [context, setContext] = useState('general');
  const [apiStatus, setApiStatus] = useState<string>('');
  const [styleProfile, setStyleProfile] = useState<StyleProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [history, setHistory] = useState<GenerationHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<'accepted' | 'rejected' | 'modified' | null>(null);

  useEffect(() => {
    const testAPI = async () => {
      try {
        const response = await axios.get<ApiHealthResponse>('http://localhost:8000/health');
        setApiStatus(`Connected: ${response.data.status}`);
      } catch (error) {
        setApiStatus('Backend not connected');
        console.error('API connection error:', error);
      }
    };

    testAPI();
  }, []);

  // Loading style profile when samples are updated
  useEffect(() => {
    loadStyleProfile();
    loadHistory();
  }, [samplesUpdated]);

  const loadStyleProfile = async () => {
    try {
      const response = await axios.get<StyleProfile>('http://localhost:8000/api/samples/profile');
      setStyleProfile(response.data);
    } catch (error) {
      console.log('No style profile found - user needs to upload samples');
      setStyleProfile(null);
    }
  };

  const loadHistory = async () => {
    try {
      interface HistoryResponse {
        success: boolean;
        history: GenerationHistory[];
      }

      const response = await axios.get<HistoryResponse>('http://localhost:8000/api/generate/history?limit=10');
      if (response.data.success) {
        setHistory(response.data.history);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const generateContent = async () => {
    if (!prompt.trim()) {
      setMessage({ type: 'error', text: 'Please enter a prompt' });
      return;
    }

    if (!styleProfile) {
      setMessage({
        type: 'error',
        text: 'Please upload and analyze writing samples first to enable personalized generation'
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.post<GeneratedContent>('http://localhost:8000/api/generate/content', {
        prompt: prompt,
        context: context
      });

      if (response.data.success) {
        setGeneratedContent(response.data.generated_content);
        setCurrentContentId(response.data.content_id);
        setEditedContent(response.data.generated_content);
        setFeedbackSubmitted(null); 
        setMessage({ type: 'success', text: response.data.message });
        loadHistory(); 
      }
    } catch (error: any) {
      console.error('Generation error:', error);
      let errorMsg = 'Generation failed';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data;
        } else if (error.response.data.detail) {
          errorMsg = error.response.data.detail;
        } else if (error.response.data.message) {
          errorMsg = error.response.data.message;
        }
      }
      
      setMessage({ type: 'error', text: errorMsg });
    }
    setLoading(false);
  };

  const submitFeedback = async (feedbackType: 'accepted' | 'rejected' | 'modified') => {
    if (!currentContentId) return;

    if (feedbackSubmitted === feedbackType) {
      setFeedbackSubmitted(null);
      setMessage({ type: 'info', text: 'Feedback cleared. You can select a different option.' });
      return;
    }

    try {
      setFeedbackSubmitted(feedbackType);

      const response = await axios.post<FeedbackResponse>('http://localhost:8000/api/generate/feedback', {
        content_id: currentContentId,
        feedback_type: feedbackType,
        modified_content: feedbackType === 'modified' ? editedContent : null
      });

      if (response.data.success) {
        setMessage({ type: 'success', text: response.data.message });
        loadHistory(); 

        if (feedbackType === 'modified') {
          setGeneratedContent(editedContent);
          setEditMode(false);
        }
      }
    } catch (error: any) {
      console.error('Feedback error:', error);
      setFeedbackSubmitted(null);
      let errorMsg = 'Failed to submit feedback';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data;
        } else if (error.response.data.detail) {
          errorMsg = error.response.data.detail;
        } else if (error.response.data.message) {
          errorMsg = error.response.data.message;
        }
      }
      
      setMessage({ type: 'error', text: errorMsg });
    }
  };

  const handlePromptChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(event.target.value);
  };

  const handleContextChange = (event: any) => {
    setContext(event.target.value);
  };

  const clearContent = () => {
    setGeneratedContent('');
    setCurrentContentId(null);
    setPrompt('');
    setEditMode(false);
    setFeedbackSubmitted(null);
    setMessage(null);
  };

  const startEditing = () => {
    setEditMode(true);
    setEditedContent(generatedContent);
  };

  const cancelEditing = () => {
    setEditMode(false);
    setEditedContent(generatedContent);
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', mt: 2, display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, flexGrow: 1, fontWeight: 'bold', fontFamily: '"Sansita", sans-serif', }}>
          Writing Studio
        </Typography>

        <Alert severity={apiStatus.includes('') ? 'success' : 'error'} sx={{ mb: 3 }}>
          Backend Status: {apiStatus}
        </Alert>

        {styleProfile ? (
          <Alert severity="success" sx={{ mb: 3 }}>
            Personal style loaded: {styleProfile.formality_preference} tone, {styleProfile.vocabulary_level} vocabulary
            ({styleProfile.sample_count} samples analyzed)
          </Alert>
        ) : (
          <Alert severity="warning" sx={{ mb: 3 }}>
            No writing style profile found. Upload samples first to enable personalized generation.
          </Alert>
        )}

        {message && (
          <Alert severity={message.type} sx={{ mb: 2 }}>
            {message.text}
          </Alert>
        )}

        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={prompt}
            onChange={handlePromptChange}
            placeholder="What would you like me to help you write? (e.g., 'Write an email to my team about the project update' or 'Help me write a creative story about time travel')"
            variant="outlined"
            sx={{ mb: 2 }}
            label="Writing Prompt"
          />

          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Context</InputLabel>
              <Select value={context} onChange={handleContextChange} label="Context">
                <MenuItem value="general">General</MenuItem>
                <MenuItem value="professional">Professional</MenuItem>
                <MenuItem value="creative">Creative</MenuItem>
                <MenuItem value="personal">Personal</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="contained"
              onClick={generateContent}
              disabled={loading || !prompt.trim() || !styleProfile}
              startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              size="large"
            >
              {loading ? 'Generating...' : 'Generate Content'}
            </Button>

            <Button variant="outlined" onClick={() => setShowHistory(true)} startIcon={<HistoryIcon />}>
              History
            </Button>
          </Box>
        </Box>

        {generatedContent && (
          <Paper elevation={2} sx={{ p: 3, mt: 3, backgroundColor: '#000000' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Generated Content</Typography>
              {!editMode && (
                <Tooltip title="Edit content">
                  <IconButton onClick={startEditing} color="primary">
                    <EditIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>

            {editMode ? (
              <Box>
                <TextField
                  fullWidth
                  multiline
                  rows={8}
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  variant="outlined"
                  sx={{ mb: 2 }}
                />
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    onClick={() => submitFeedback('modified')}
                    color="primary"
                  >
                    Save Changes
                  </Button>
                  <Button variant="outlined" onClick={cancelEditing}>
                    Cancel
                  </Button>
                </Box>
              </Box>
            ) : (
              <Box>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 3, lineHeight: 1.6 }}>
                  {generatedContent}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip
                    icon={<ThumbUp />}
                    label="Accept"
                    onClick={() => submitFeedback('accepted')}
                    color="success"
                    variant={feedbackSubmitted === 'accepted' ? 'filled' : 'outlined'}
                    clickable
                    sx={{
                      opacity: feedbackSubmitted && feedbackSubmitted !== 'accepted' ? 0.7 : 1,
                      cursor: 'pointer',
                      '&:hover': {
                        opacity: 1
                      }
                    }}
                  />

                  <Chip
                    icon={<ThumbDown />}
                    label="Reject"
                    onClick={() => submitFeedback('rejected')}
                    color="error"
                    variant={feedbackSubmitted === 'rejected' ? 'filled' : 'outlined'}
                    clickable
                    sx={{
                      opacity: feedbackSubmitted && feedbackSubmitted !== 'rejected' ? 0.7 : 1,
                      cursor: 'pointer',
                      '&:hover': {
                        opacity: 1
                      }
                    }}
                  />

                  <Chip
                    icon={<EditIcon />}
                    label="Edit"
                    onClick={startEditing}
                    color="primary"
                    variant="outlined"
                    clickable
                    sx={{
                      opacity: feedbackSubmitted ? 0.7 : 1,
                      cursor: 'pointer',
                      '&:hover': {
                        opacity: 1
                      }
                    }}
                  />
                </Box>
              </Box>
            )}

            <Button variant="text" onClick={clearContent} sx={{ mt: 2 }} size="small">
              Clear and Start New
            </Button>
          </Paper>
        )}
      </Paper>

      <Dialog open={showHistory} onClose={() => setShowHistory(false)} fullWidth maxWidth="md">
        <DialogTitle>Recent Generated Content</DialogTitle>
        <DialogContent dividers>
          {history.length === 0 ? (
            <Typography>No history found.</Typography>
          ) : (
            history.map((item) => (
              <Paper key={item.id} elevation={1} sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Prompt: {item.prompt}
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 1 }}>
                  {item.generated_text}
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                  Feedback: {item.user_feedback || 'None'} | Created: {new Date(item.created_at).toLocaleString()}
                </Typography>
              </Paper>
            ))
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistory(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Box>
        <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom sx={{fontFamily: '"Sansita", sans-serif'}}>
            Quick Tips
          </Typography>
          <Typography variant="body2" sx={{ mb: 2,  }}>
            • Be specific in your prompts for better results<br />
            • Use different contexts for different types of writing<br />
            • Provide feedback to improve future generations
          </Typography>
          <Typography variant="h6" gutterBottom sx={{fontFamily: '"Sansita", sans-serif'}}>
            Example prompts:
          </Typography>
          <Typography variant="body2" display="block" sx={{ mb: 1 }}>
            "Write a professional email declining a meeting"
          </Typography>
          <Typography variant="body2" display="block" sx={{ mb: 1 }}>
            "Help me write a creative story opening"
          </Typography>
          <Typography variant="body2" display="block">
            "Draft a personal message to thank someone"
          </Typography>
        </Paper>

        {styleProfile && (
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom sx={{fontFamily: '"Sansita", sans-serif'}}>
              Your Writing Style
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Chip label={`${styleProfile.formality_preference} tone`} size="small" />
              <Chip label={`${styleProfile.vocabulary_level} vocabulary`} size="small" />
              <Chip label={`${styleProfile.sample_count} samples analyzed`} size="small" />
            </Box>
          </Paper>
        )}
      </Box>
    </Box>
  );
};

export default WritingInterface;