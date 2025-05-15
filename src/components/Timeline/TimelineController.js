import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Slider,
  IconButton,
  Typography,
  Paper,
  ButtonGroup,
  Tooltip,
  Chip,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  FastForward,
  FastRewind,
  FilterList,
  Timeline,
  StarBorder,
  Public
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';

const TimelineController = ({
  events,
  currentDate,
  onDateChange,
  onEventSelect,
  onPeriodChange,
  selectedPeriod,
  onImportanceChange,
  minImportance
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [visibleEvents, setVisibleEvents] = useState([]);
  
  // 计算时间范围
  const timeRange = events.reduce(
    (range, event) => {
      const startDate = new Date(event.date.start);
      const endDate = new Date(event.date.end);
      return {
        min: startDate < range.min ? startDate : range.min,
        max: endDate > range.max ? endDate : range.max,
      };
    },
    { min: new Date(), max: new Date() }
  );

  // 处理时间轴播放
  useEffect(() => {
    let timer;
    if (isPlaying) {
      timer = setInterval(() => {
        const nextDate = new Date(currentDate.getTime() + playbackSpeed * 86400000);
        if (nextDate > timeRange.max) {
          setIsPlaying(false);
        } else {
          onDateChange(nextDate);
        }
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isPlaying, currentDate, playbackSpeed, timeRange.max, onDateChange]);

  // 处理可见事件
  useEffect(() => {
    const visible = events.filter(event => {
      const eventStart = new Date(event.date.start);
      const eventEnd = new Date(event.date.end);
      return currentDate >= eventStart && currentDate <= eventEnd;
    });
    setVisibleEvents(visible);
  }, [currentDate, events]);

  const handleSliderChange = (event, newValue) => {
    const date = new Date(timeRange.min.getTime() + 
      (newValue / 100) * (timeRange.max.getTime() - timeRange.min.getTime()));
    onDateChange(date);
  };

  const getSliderValue = useCallback(() => {
    return ((currentDate.getTime() - timeRange.min.getTime()) /
      (timeRange.max.getTime() - timeRange.min.getTime())) * 100;
  }, [currentDate, timeRange]);

  const handleSpeedChange = (multiplier) => {
    setPlaybackSpeed(current => {
      const newSpeed = current * multiplier;
      return Math.min(Math.max(newSpeed, 0.25), 16);
    });
  };

  return (
    <>
      <Paper
        elevation={3}
        sx={{
          position: 'fixed',
          bottom: 20,
          left: '50%',
          transform: 'translateX(-50%)',
          width: '90%',
          maxWidth: 800,
          p: 2,
          zIndex: 1000,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {format(currentDate, 'yyyy-MM-dd')}
          </Typography>
          <Tooltip title={t('timeline.filter')}>
            <IconButton onClick={() => setDrawerOpen(true)}>
              <FilterList />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <ButtonGroup size="small">
            <IconButton onClick={() => handleSpeedChange(0.5)}>
              <FastRewind />
            </IconButton>
            <IconButton onClick={() => setIsPlaying(!isPlaying)}>
              {isPlaying ? <Pause /> : <PlayArrow />}
            </IconButton>
            <IconButton onClick={() => handleSpeedChange(2)}>
              <FastForward />
            </IconButton>
          </ButtonGroup>

          <Slider
            value={getSliderValue()}
            onChange={handleSliderChange}
            aria-label="timeline-slider"
            sx={{ flexGrow: 1 }}
          />

          <Chip
            label={`${t('timeline.speed')} ${playbackSpeed}x`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>

        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {visibleEvents.map((event) => (
            <Chip
              key={event.id}
              label={event.title[navigator.language.split('-')[0]] || event.title.en}
              onClick={() => onEventSelect(event)}
              color="primary"
              size="small"
            />
          ))}
        </Box>
      </Paper>

      <Drawer
        anchor={isMobile ? 'bottom' : 'right'}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: isMobile ? 'auto' : 250, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            {t('timeline.filters')}
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <Timeline />
              </ListItemIcon>
              <ListItemText primary={t('timeline.period')} />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <StarBorder />
              </ListItemIcon>
              <ListItemText primary={t('timeline.importance')} />
              <Slider
                value={minImportance}
                onChange={(e, value) => onImportanceChange(value)}
                min={1}
                max={5}
                step={1}
                marks
                sx={{ width: 100 }}
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <Public />
              </ListItemIcon>
              <ListItemText primary={t('timeline.region')} />
            </ListItem>
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default TimelineController;
