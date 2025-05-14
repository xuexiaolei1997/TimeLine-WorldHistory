import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Box, 
  IconButton, 
  Tooltip, 
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Alert,
  AlertTitle,
  Collapse,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import { 
  Check as CheckIcon, 
  Warning as WarningIcon, 
  Error as ErrorIcon,
  Speed as SpeedIcon,
  NotificationsActive as AlertIcon
} from '@mui/icons-material';
import config from '../config';

const HealthMonitor = () => {
  const { t } = useTranslation();
  const [health, setHealth] = useState({ status: 'unknown', services: {} });
  const [metrics, setMetrics] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const checkHealth = async () => {
    try {
      const [healthResponse, metricsResponse, alertsResponse] = await Promise.all([
        fetch(`${config.apiBaseUrl}/health`),
        fetch(`${config.apiBaseUrl}/health/metrics`),
        fetch(`${config.apiBaseUrl}/health/alerts`)
      ]);
      
      const healthData = await healthResponse.json();
      const metricsData = await metricsResponse.json();
      const alertsData = await alertsResponse.json();
      
      setHealth(healthData);
      setMetrics(metricsData.data || {});
      setAlerts(alertsData.data || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setHealth({ status: 'unhealthy', services: {} });
      setMetrics({});
      setAlerts([]);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckIcon sx={{ color: 'success.main' }} />;
      case 'degraded':
        return <WarningIcon sx={{ color: 'warning.main' }} />;
      case 'unhealthy':
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      default:
        return <WarningIcon sx={{ color: 'grey.500' }} />;
    }
  };

  const getTooltipContent = () => {
    if (error) return t('performance.backendUnreachable');
    
    const messages = [];
    Object.entries(health.services).forEach(([service, status]) => {
      messages.push(`${service}: ${status.status}${status.error ? ` (${status.error})` : ''}`);
    });
    return messages.join('\n');
  };

  const renderMetricsTable = () => (
    <TableContainer component={Paper}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('performance.table.endpoint')}</TableCell>
            <TableCell align="right">{t('performance.table.average')}</TableCell>
            <TableCell align="right">{t('performance.table.p95')}</TableCell>
            <TableCell align="right">{t('performance.table.max')}</TableCell>
            <TableCell align="right">{t('performance.table.errorRate')}</TableCell>
            <TableCell align="right">{t('performance.table.samples')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.entries(metrics).map(([endpoint, data]) => (
            <TableRow 
              key={endpoint}
              sx={{ 
                backgroundColor: data.error_rate > '5.0%' ? 'error.main' : 'inherit',
                '&:hover': { backgroundColor: 'action.hover' }
              }}
            >
              <TableCell component="th" scope="row">{endpoint}</TableCell>
              <TableCell align="right">{data.average}</TableCell>
              <TableCell align="right">{data.p95}</TableCell>
              <TableCell align="right">{data.max}</TableCell>
              <TableCell align="right">{data.error_rate}</TableCell>
              <TableCell align="right">{data.samples}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderAlerts = () => (
    <Box sx={{ mt: 2 }}>
      {alerts.length > 0 ? (
        alerts.map((alert, index) => (
          <Alert 
            key={`${alert.endpoint}-${alert.metric}-${alert.timestamp}`}
            severity="warning"
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
        ))
      ) : (
        <Typography variant="body2" color="text.secondary">
          {t('performance.noAlerts')}
        </Typography>
      )}
    </Box>
  );

  return (
    <>
      <Box sx={{ position: 'fixed', bottom: 16, right: 16, zIndex: 1000 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title={t('performance.viewMetrics')} arrow placement="left">
            <IconButton size="small" onClick={() => setDialogOpen(true)}>
              <Badge
                badgeContent={alerts.length}
                color="error"
                invisible={alerts.length === 0}
              >
                <SpeedIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          <Tooltip title={getTooltipContent()} arrow placement="left">
            <IconButton size="small" onClick={checkHealth}>
              <Badge
                variant="dot"
                color={health.status === 'healthy' ? 'success' : 'error'}
                invisible={health.status === 'unknown'}
              >
                {getStatusIcon(health.status)}
              </Badge>
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
              <Tab label={t('performance.tabs.metrics')} />
              <Tab 
                label={t('performance.tabs.alerts')} 
                icon={alerts.length > 0 ? <AlertIcon color="error" /> : undefined}
                iconPosition="end"
              />
            </Tabs>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="subtitle2" gutterBottom>
            {t('performance.serviceStatus')}: {health.status}
          </Typography>
          {Object.entries(health.services).map(([service, status]) => (
            <Typography key={service} variant="body2" gutterBottom>
              {service}: {status.status} {status.error && `(${status.error})`}
            </Typography>
          ))}
          <Divider sx={{ my: 2 }} />
          {activeTab === 0 ? (
            Object.keys(metrics).length > 0 ? renderMetricsTable() : (
              <Typography variant="body2" color="text.secondary">
                {t('performance.noData')}
              </Typography>
            )
          ) : (
            renderAlerts()
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default HealthMonitor;