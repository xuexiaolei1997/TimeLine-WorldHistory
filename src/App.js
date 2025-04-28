import React, { useState, useEffect } from 'react';
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

function App() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [timezone, setTimezone] = useState(8); // 默认北京时间UTC+8
  const [rotationSpeed, setRotationSpeed] = useState(1); // 默认自转速度
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const data = await loadInitialData();
      setEvents(data.events);
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
              世界历史时间线
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
          <DialogTitle>设置</DialogTitle>
          <DialogContent>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>时区选择</InputLabel>
              <Select
                value={timezone}
                onChange={(e) => setTimezone(Number(e.target.value))}
                label="时区选择"
              >
                <MenuItem value={-12}>UTC-12</MenuItem>
                <MenuItem value={-8}>UTC-8</MenuItem>
                <MenuItem value={0}>UTC</MenuItem>
                <MenuItem value={8}>UTC+8 (北京时间)</MenuItem>
                <MenuItem value={12}>UTC+12</MenuItem>
              </Select>
            </FormControl>
            <Box>
              <Typography gutterBottom>地球自转速度</Typography>
              <Slider
                value={rotationSpeed}
                onChange={(e, newValue) => setRotationSpeed(newValue)}
                min={0}
                max={1}
                step={0.01}
                valueLabelDisplay="auto"
                marks={[
                  { value: 0, label: '停止' },
                  { value: 0.5, label: '正常' },
                  { value: 1, label: '快速' }
                ]}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSettingsOpen(false)}>关闭</Button>
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
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
