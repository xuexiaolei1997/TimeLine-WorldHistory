import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import i18n from 'i18next';
import { initReactI18next, useTranslation } from 'react-i18next';
import { 
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Paper,
  Box,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Button,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import Earth3D from './components/Earth3D';
import TimelineController from './components/Timeline/TimelineController';
import AdminPanel from './components/Admin/AdminPanel';
import HealthMonitor from './components/HealthMonitor';
import { loadInitialData } from './utils/DataLoader';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00b4d8',
    },
    secondary: {
      main: '#1a1a2e',
    },
    background: {
      default: '#0f0c29',
      paper: '#1a1a2e',
    },
  },
  typography: {
    fontFamily: 'Poppins, Arial, sans-serif',
  },
});

// 初始化i18n
i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: require('./locales/en/translation.json') },
      zh: { translation: require('./locales/zh/translation.json') }
    },
    lng: 'zh',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

function App() {
  const { t } = useTranslation();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [regions, setRegions] = useState([]);
  const [timezone, setTimezone] = useState(8);
  const [rotationSpeed, setRotationSpeed] = useState(0);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [retryCountdown, setRetryCountdown] = useState(null);

  const handleError = useCallback((error) => {
    console.error('Application error:', error);
    const errorDetails = error.requestId ? ` (ID: ${error.requestId})` : '';
    
    if (error.type === 'DATABASE_ERROR') {
      setError({
        title: t('databaseError'),
        message: `${error.message}${errorDetails}`,
        retry: true,
        requestId: error.requestId
      });
    } else if (error.type === 'VALIDATION_ERROR') {
      setNotification({
        open: true,
        message: `${t('validationError')}: ${error.message}${errorDetails}`,
        severity: 'warning'
      });
    } else if (error.type === 'CLIENT_ERROR') {
      if (error.message.includes('timeout')) {
        setError({
          title: t('timeoutError'),
          message: `${t('pleaseCheckConnection')}${errorDetails}`,
          retry: true,
          requestId: error.requestId
        });
      } else if (error.message.includes('Too many requests')) {
        const retryAfter = error.details?.retry_after || 60;
        setRetryCountdown(retryAfter);
        setError({
          title: t('rateLimitError'),
          message: `${t('rateLimitMessage')}${errorDetails}`,
          retry: false,
          requestId: error.requestId
        });

        // Start countdown
        const timer = setInterval(() => {
          setRetryCountdown(prev => {
            if (prev <= 1) {
              clearInterval(timer);
              setError(null);
              return null;
            }
            return prev - 1;
          });
        }, 1000);

        return () => clearInterval(timer);
      } else {
        setNotification({
          open: true,
          message: `${error.message}${errorDetails}`,
          severity: 'error'
        });
      }
    } else {
      setError({
        title: t('error'),
        message: `${error.message || t('unknownError')}${errorDetails}`,
        retry: true,
        requestId: error.requestId
      });
    }
  }, [t]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await loadInitialData();
        setEvents(data.events);
        setRegions(data.regions || []);
      } catch (error) {
        handleError(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [handleError]);

  const handleRetry = () => {
    setError(null);
    window.location.reload();
  };

  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          backgroundColor: 'background.default'
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          backgroundColor: 'background.default',
          color: 'error.main',
          p: 3,
          textAlign: 'center'
        }}
      >
        <Typography variant="h5" gutterBottom>
          {error.title}
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          {error.message}
        </Typography>
        {error.requestId && (
          <Typography variant="caption" color="text.secondary" sx={{ mb: 2 }}>
            {t('requestId')}: {error.requestId}
          </Typography>
        )}
        {retryCountdown && (
          <Typography variant="body2" sx={{ mb: 2 }}>
            {t('retryingIn', { seconds: retryCountdown })}
          </Typography>
        )}
        {error.retry && (
          <Button 
            variant="contained" 
            onClick={handleRetry}
            sx={{ mt: 2 }}
          >
            {t('retry')}
          </Button>
        )}
      </Box>
    );
  }

  return (
    <Router>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Routes>
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/" element={
      <Box sx={{ display: 'flex', height: '100vh' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              {t('welcome')}
            </Typography>
            <IconButton 
              color="inherit"
              onClick={() => setSettingsOpen(true)}
            >
              <SettingsIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
        <Dialog 
          open={settingsOpen}
          onClose={() => setSettingsOpen(false)}
        >
          <DialogTitle>{t('settings')}</DialogTitle>
          <DialogContent>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>{t('language')}</InputLabel>
              <Select
                value={i18n.language}
                onChange={(e) => i18n.changeLanguage(e.target.value)}
                label={t('language')}
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="zh">中文</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>{t('timezone')}</InputLabel>
              <Select
                value={timezone}
                onChange={(e) => setTimezone(Number(e.target.value))}
                label={t('timezone')}
              >
                <MenuItem value={-12}>UTC-12</MenuItem>
                <MenuItem value={-8}>UTC-8</MenuItem>
                <MenuItem value={0}>UTC</MenuItem>
                <MenuItem value={8}>UTC+8 (北京时间)</MenuItem>
                <MenuItem value={12}>UTC+12</MenuItem>
              </Select>
            </FormControl>
            <Box>
              <Typography gutterBottom>{t('rotationSpeed')}</Typography>
              <Slider
                value={rotationSpeed}
                onChange={(e, newValue) => setRotationSpeed(newValue)}
                min={0}
                max={10}
                step={0.1}
                valueLabelDisplay="auto"
                marks={[
                  { value: 0, label: t('stop') },
                  { value: 5, label: t('normal') },
                  { value: 10, label: t('fast') }
                ]}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSettingsOpen(false)}>{t('close')}</Button>
          </DialogActions>
        </Dialog>
        <Paper
          elevation={3}
          sx={{
            width: 300,
            height: '100vh',
            position: 'fixed',
            overflow: 'auto',
            zIndex: 1,
            mt: 8,
            borderRadius: 0,
          }}
        >
          <TimelineController 
            currentDate={currentDate}
            onDateChange={setCurrentDate}
          />
        </Paper>
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            ml: '300px',
            mt: 8,
            height: 'calc(100vh - 64px)',
          }}
        >
          <Earth3D 
            currentDate={currentDate}
            events={events}
            regions={regions}
            timezone={timezone}
            rotationSpeed={rotationSpeed}
            onZoomChange={setZoomLevel}
          />
          <div style={{ position: 'absolute', bottom: 20, left: 320, color: 'white' }}>
            Current date: {currentDate.toString()}
          </div>
          <div style={{ position: 'absolute', bottom: 50, left: 320, color: 'white' }}>
            Zoom level: {zoomLevel}
          </div>
        </Box>
        <HealthMonitor />
      </Box>
        } />
      </Routes>
        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={() => setNotification(prev => ({ ...prev, open: false }))}
        >
          <Alert 
            onClose={() => setNotification(prev => ({ ...prev, open: false }))} 
            severity={notification.severity}
          >
            {notification.message}
          </Alert>
        </Snackbar>
    </ThemeProvider>
    </Router>
  );
}

export default App;
