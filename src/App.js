import React, { useState, useEffect } from 'react';
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
  Button
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import Earth3D from './components/Earth3D';
import TimelineController from './components/Timeline/TimelineController';
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
  const [timezone, setTimezone] = useState(8); // 默认北京时间UTC+8
  const [rotationSpeed, setRotationSpeed] = useState(0); // 默认自转速度
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Loading initial data...');
        const data = await loadInitialData();
        console.log('Data loaded successfully:', data);
        setEvents(data.events);
      } catch (error) {
        console.error('Failed to load data:', error);
      }
    };
    fetchData();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
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
            timezone={timezone}
            rotationSpeed={rotationSpeed}
          />
          <div style={{ position: 'absolute', bottom: 20, left: 320, color: 'white' }}>
            Current date: {currentDate.toString()}
          </div>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
