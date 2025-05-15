import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  AlertTitle,
  CircularProgress,
  Tabs,
  Tab,
  Badge,
  Chip,
  useTheme
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const HealthMonitor = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [healthData, setHealthData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        const [healthResponse, alertsResponse] = await Promise.all([
          axios.get('/api/health'),
          axios.get('/api/health/alerts')
        ]);

        setHealthData(healthResponse.data);
        setAlerts(alertsResponse.data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHealthData();
    const interval = setInterval(fetchHealthData, 30000); // 每30秒更新一次

    return () => clearInterval(interval);
  }, []);

  const renderMetrics = () => {
    if (!healthData?.metrics) {
      return (
        <Typography variant="body2" color="textSecondary">
          {t('performance.noData')}
        </Typography>
      );
    }

    return (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>{t('performance.table.endpoint')}</TableCell>
              <TableCell align="right">{t('performance.table.average')}</TableCell>
              <TableCell align="right">{t('performance.table.p95')}</TableCell>
              <TableCell align="right">{t('performance.table.max')}</TableCell>
              <TableCell align="right">{t('performance.table.samples')}</TableCell>
              <TableCell align="right">{t('performance.table.errorRate')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(healthData.metrics).map(([endpoint, metrics]) => (
              <TableRow key={endpoint}>
                <TableCell component="th" scope="row">
                  {endpoint}
                </TableCell>
                <TableCell align="right">
                  {metrics.average_response_time.toFixed(2)}ms
                </TableCell>
                <TableCell align="right">
                  {metrics.p95_response_time.toFixed(2)}ms
                </TableCell>
                <TableCell align="right">
                  {metrics.max_response_time.toFixed(2)}ms
                </TableCell>
                <TableCell align="right">
                  {metrics.request_count}
                </TableCell>
                <TableCell align="right">
                  <Chip
                    size="small"
                    label={`${(metrics.error_rate * 100).toFixed(1)}%`}
                    color={metrics.error_rate > 0.05 ? 'error' : 'success'}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderAlerts = () => {
    if (!alerts?.length) {
      return (
        <Typography variant="body2" color="textSecondary">
          {t('performance.noAlerts')}
        </Typography>
      );
    }

    return alerts.map((alert, index) => (
      <Alert
        key={index}
        severity={alert.severity}
        sx={{ mb: 1 }}
      >
        <AlertTitle>{t('performance.alert.title')}</AlertTitle>
        {t('performance.alert.message', {
          endpoint: alert.endpoint,
          metric: t(`performance.metrics.${alert.metric}`),
          value: alert.value,
          threshold: alert.threshold
        })}
      </Alert>
    ));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {t('performance.backendUnreachable')}
      </Alert>
    );
  }

  return (
    <Paper sx={{ 
      p: 2, 
      m: 2,
      backgroundColor: theme.palette.background.paper,
      borderRadius: theme.shape.borderRadius,
      boxShadow: theme.shadows[1]
    }}>
      <Typography variant="h6" gutterBottom sx={{ color: theme.palette.text.primary }}>
        {t('performance.title')}
      </Typography>

      <Box sx={{ 
        borderBottom: 1, 
        borderColor: theme.palette.divider,
        mb: 2 
      }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          aria-label="health monitor tabs"
          sx={{
            '& .MuiTab-root': {
              color: theme.palette.text.secondary,
              '&.Mui-selected': {
                color: theme.palette.primary.main
              }
            }
          }}
        >
          <Tab
            label={t('performance.tabs.metrics')}
            id="health-tab-0"
          />
          <Tab
            label={
              <Badge
                badgeContent={alerts.length}
                color="error"
                sx={{
                  '& .MuiBadge-badge': {
                    right: -15,
                    top: -5,
                  },
                }}
              >
                {t('performance.tabs.alerts')}
              </Badge>
            }
            id="health-tab-1"
          />
        </Tabs>
      </Box>

      <Box role="tabpanel" hidden={activeTab !== 0}>
        {activeTab === 0 && renderMetrics()}
      </Box>
      
      <Box role="tabpanel" hidden={activeTab !== 1}>
        {activeTab === 1 && renderAlerts()}
      </Box>

      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" color="textSecondary">
          {t('performance.serviceStatus')}:
        </Typography>
        <Chip
          size="small"
          label={healthData?.status || 'unknown'}
          color={healthData?.status === 'healthy' ? 'success' : 'error'}
        />
      </Box>
    </Paper>
  );
};

export default HealthMonitor;