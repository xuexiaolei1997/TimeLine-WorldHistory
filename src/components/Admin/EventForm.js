import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography
} from '@mui/material';
import { useTranslation } from 'react-i18next';

const EventForm = ({ open, event, onClose, onSubmit }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    title: '',
    period: '',
    startDate: '',
    endDate: '',
    location: {
      coordinates: [0, 0],
      zoomLevel: 3
    },
    description: ''
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (event) {
      setFormData({
        title: event.title || '',
        period: event.period || '',
        startDate: event.startDate ? new Date(event.startDate).toISOString().split('T')[0] : '',
        endDate: event.endDate ? new Date(event.endDate).toISOString().split('T')[0] : '',
        location: event.location || {
          coordinates: [0, 0],
          zoomLevel: 3
        },
        description: event.description || ''
      });
    } else {
      setFormData({
        title: '',
        period: '',
        startDate: '',
        endDate: '',
        location: {
          coordinates: [0, 0],
          zoomLevel: 3
        },
        description: ''
      });
    }
  }, [event]);

  const validate = () => {
    const newErrors = {};
    if (!formData.title) newErrors.title = t('admin.form.errors.required');
    if (!formData.period) newErrors.period = t('admin.form.errors.required');
    if (!formData.startDate) newErrors.startDate = t('admin.form.errors.required');
    if (!formData.endDate) newErrors.endDate = t('admin.form.errors.required');
    if (new Date(formData.endDate) < new Date(formData.startDate)) {
      newErrors.endDate = t('admin.form.errors.invalidDate');
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validate()) {
      onSubmit({
        ...formData,
        startDate: new Date(formData.startDate).toISOString(),
        endDate: new Date(formData.endDate).toISOString()
      });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleLocationChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      location: {
        ...formData.location,
        [name]: name === 'coordinates' ? 
          value.split(',').map(Number) : 
          Number(value)
      }
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {event ? t('admin.form.editTitle') : t('admin.form.addTitle')}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              name="title"
              label={t('admin.form.title')}
              value={formData.title}
              onChange={handleChange}
              error={!!errors.title}
              helperText={errors.title}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth error={!!errors.period}>
              <InputLabel>{t('admin.form.period')}</InputLabel>
              <Select
                name="period"
                value={formData.period}
                onChange={handleChange}
                label={t('admin.form.period')}
              >
                <MenuItem value="ancient">{t('periods.ancient')}</MenuItem>
                <MenuItem value="medieval">{t('periods.medieval')}</MenuItem>
                <MenuItem value="modern">{t('periods.modern')}</MenuItem>
              </Select>
              {errors.period && (
                <Typography variant="caption" color="error">
                  {errors.period}
                </Typography>
              )}
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="zoomLevel"
              label={t('admin.form.zoomLevel')}
              type="number"
              value={formData.location.zoomLevel}
              onChange={handleLocationChange}
              inputProps={{ min: 1, max: 10 }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="startDate"
              label={t('admin.form.startDate')}
              type="date"
              InputLabelProps={{ shrink: true }}
              value={formData.startDate}
              onChange={handleChange}
              error={!!errors.startDate}
              helperText={errors.startDate}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="endDate"
              label={t('admin.form.endDate')}
              type="date"
              InputLabelProps={{ shrink: true }}
              value={formData.endDate}
              onChange={handleChange}
              error={!!errors.endDate}
              helperText={errors.endDate}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="coordinates"
              label={t('admin.form.coordinates')}
              value={formData.location.coordinates.join(',')}
              onChange={handleLocationChange}
              placeholder="latitude,longitude"
              helperText={t('admin.form.coordinatesHelp')}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              name="description"
              label={t('admin.form.description')}
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={4}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('admin.cancel')}</Button>
        <Button onClick={handleSubmit} variant="contained">
          {t('admin.save')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EventForm;
