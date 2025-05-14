import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab
} from '@mui/material';
import EventTable from './EventTable';
import EventForm from './EventForm';
import PeriodTable from './PeriodTable';
import PeriodForm from './PeriodForm';
import RegionTable from './RegionTable';
import RegionForm from './RegionForm';
import { useTranslation } from 'react-i18next';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('events');
  const { t } = useTranslation();
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [periods, setPeriods] = useState([]);
  const [regions, setRegions] = useState([]);
  const [openForm, setOpenForm] = useState(false);
  const [editEvent, setEditEvent] = useState(null);
  const [editPeriod, setEditPeriod] = useState(null);
  const [editRegion, setEditRegion] = useState(null);
  const [searchParams, setSearchParams] = useState({
    title: '',
    period: '',
    startDate: '',
    endDate: ''
  });

  // 加载数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 加载事件数据
        const eventsResponse = await fetch('/events');
        const eventsData = await eventsResponse.json();
        setEvents(eventsData);
        setFilteredEvents(eventsData);

        // 加载时期数据
        const periodsResponse = await fetch('/periods');
        const periodsData = await periodsResponse.json();
        setPeriods(periodsData);

        // 加载区域数据
        const regionsResponse = await fetch('/regions');
        const regionsData = await regionsResponse.json();
        setRegions(regionsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, []);

  // 处理查询
  const handleSearch = () => {
    if (activeTab === 'events') {
      const filtered = events.filter(event => {
        return (
          (!searchParams.title || event.title.includes(searchParams.title)) &&
          (!searchParams.period || event.period === searchParams.period) &&
          (!searchParams.startDate || new Date(event.startDate) >= new Date(searchParams.startDate)) &&
          (!searchParams.endDate || new Date(event.endDate) <= new Date(searchParams.endDate))
        );
      });
      setFilteredEvents(filtered);
    }
  };

  // 重置查询
  const handleReset = () => {
    setSearchParams({
      title: '',
      period: '',
      startDate: '',
      endDate: ''
    });
    setFilteredEvents(events);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {t('admin.title')}
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label={t('admin.tabs.events')} value="events" />
        <Tab label={t('admin.tabs.periods')} value="periods" />
        <Tab label={t('admin.tabs.regions')} value="regions" />
      </Tabs>
      
      {/* 查询表单 - 仅事件页面显示 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label={t('admin.search.title')}
              value={searchParams.title}
              onChange={(e) => setSearchParams({...searchParams, title: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>{t('admin.search.period')}</InputLabel>
              <Select
                value={searchParams.period}
                onChange={(e) => setSearchParams({...searchParams, period: e.target.value})}
                label={t('admin.search.period')}
              >
                <MenuItem value="">{t('admin.all')}</MenuItem>
                <MenuItem value="ancient">{t('periods.ancient')}</MenuItem>
                <MenuItem value="medieval">{t('periods.medieval')}</MenuItem>
                <MenuItem value="modern">{t('periods.modern')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label={t('admin.search.startDate')}
              type="date"
              InputLabelProps={{ shrink: true }}
              value={searchParams.startDate}
              onChange={(e) => setSearchParams({...searchParams, startDate: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label={t('admin.search.endDate')}
              type="date"
              InputLabelProps={{ shrink: true }}
              value={searchParams.endDate}
              onChange={(e) => setSearchParams({...searchParams, endDate: e.target.value})}
            />
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="contained" onClick={handleSearch}>
                {t('admin.search')}
              </Button>
              <Button variant="outlined" onClick={handleReset}>
                {t('admin.reset')}
              </Button>
              <Button 
                variant="contained" 
                color="success"
                onClick={() => {
                  setEditEvent(null);
                  setOpenForm(true);
                }}
              >
                {t('admin.add')}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {activeTab === 'events' && (
        <>
          {/* 事件表格 */}
          <EventTable 
            events={filteredEvents} 
            onEdit={(event) => {
              setEditEvent(event);
              setOpenForm(true);
            }}
            onDelete={async (id) => {
              try {
                await fetch(`/events/${id}`, { method: 'DELETE' });
                setEvents(events.filter(e => e.id !== id));
                setFilteredEvents(filteredEvents.filter(e => e.id !== id));
              } catch (error) {
                console.error('Error deleting event:', error);
              }
            }}
          />

          {/* 事件表单弹窗 */}
          <EventForm
            open={openForm && activeTab === 'events'}
            event={editEvent}
            onClose={() => setOpenForm(false)}
            onSubmit={async (formData) => {
              try {
                const method = editEvent ? 'PUT' : 'POST';
                const url = editEvent ? `/events/${editEvent.id}` : '/events';
                
                const response = await fetch(url, {
                  method,
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify(formData),
                });

                const updatedEvent = await response.json();
                
                if (editEvent) {
                  setEvents(events.map(e => e.id === updatedEvent.id ? updatedEvent : e));
                  setFilteredEvents(filteredEvents.map(e => e.id === updatedEvent.id ? updatedEvent : e));
                } else {
                  setEvents([...events, updatedEvent]);
                  setFilteredEvents([...filteredEvents, updatedEvent]);
                }
                
                setOpenForm(false);
              } catch (error) {
                console.error('Error saving event:', error);
              }
            }}
          />
        </>
      )}

      {activeTab === 'periods' && (
        <>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button 
              variant="contained" 
              color="success"
              onClick={() => {
                setEditPeriod(null);
                setOpenForm(true);
              }}
            >
              {t('admin.add')}
            </Button>
          </Box>
          
          <PeriodTable 
            periods={periods} 
            onEdit={(period) => {
              setEditPeriod(period);
              setOpenForm(true);
            }}
            onDelete={async (id) => {
              try {
                await fetch(`/periods/${id}`, { method: 'DELETE' });
                setPeriods(periods.filter(p => p.id !== id));
              } catch (error) {
                console.error('Error deleting period:', error);
              }
            }}
          />

          <PeriodForm
            open={openForm && activeTab === 'periods'}
            period={editPeriod}
            onClose={() => setOpenForm(false)}
            onSubmit={async (formData) => {
              try {
                const method = editPeriod ? 'PUT' : 'POST';
                const url = editPeriod ? `/periods/${editPeriod.id}` : '/periods';
                
                const response = await fetch(url, {
                  method,
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify(formData),
                });

                const updatedPeriod = await response.json();
                
                if (editPeriod) {
                  setPeriods(periods.map(p => p.id === updatedPeriod.id ? updatedPeriod : p));
                } else {
                  setPeriods([...periods, updatedPeriod]);
                }
                
                setOpenForm(false);
              } catch (error) {
                console.error('Error saving period:', error);
              }
            }}
          />
        </>
      )}

      {activeTab === 'regions' && (
        <>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button 
              variant="contained" 
              color="success"
              onClick={() => {
                setEditRegion(null);
                setOpenForm(true);
              }}
            >
              {t('admin.add')}
            </Button>
          </Box>
          
          <RegionTable 
            regions={regions} 
            onEdit={(region) => {
              setEditRegion(region);
              setOpenForm(true);
            }}
            onDelete={async (id) => {
              try {
                await fetch(`/regions/${id}`, { method: 'DELETE' });
                setRegions(regions.filter(r => r.id !== id));
              } catch (error) {
                console.error('Error deleting region:', error);
              }
            }}
          />

          <RegionForm
            open={openForm && activeTab === 'regions'}
            region={editRegion}
            onClose={() => setOpenForm(false)}
            onSubmit={async (formData) => {
              try {
                const method = editRegion ? 'PUT' : 'POST';
                const url = editRegion ? `/regions/${editRegion.id}` : '/regions';
                
                const response = await fetch(url, {
                  method,
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify(formData),
                });

                const updatedRegion = await response.json();
                
                if (editRegion) {
                  setRegions(regions.map(r => r.id === updatedRegion.id ? updatedRegion : r));
                } else {
                  setRegions([...regions, updatedRegion]);
                }
                
                setOpenForm(false);
              } catch (error) {
                console.error('Error saving region:', error);
              }
            }}
          />
        </>
      )}
    </Box>
  );
};

export default AdminPanel;
