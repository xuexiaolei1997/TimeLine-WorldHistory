import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  Typography
} from '@mui/material';
import { useTranslation } from 'react-i18next';

const RegionForm = ({ open, region, onClose, onSubmit }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: '',
    coordinates: [0, 0],
    description: ''
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (region) {
      setFormData({
        name: region.name || '',
        coordinates: region.coordinates || [0, 0],
        description: region.description || ''
      });
    } else {
      setFormData({
        name: '',
        coordinates: [0, 0],
        description: ''
      });
    }
  }, [region]);

  const validate = () => {
    const newErrors = {};
    if (!formData.name) newErrors.name = t('admin.form.errors.required');
    if (!formData.coordinates || formData.coordinates.length !== 2) {
      newErrors.coordinates = t('admin.form.errors.invalidCoordinates');
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleCoordinatesChange = (e) => {
    const { value } = e.target;
    const coords = value.split(',').map(Number);
    if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
      setFormData({
        ...formData,
        coordinates: coords
      });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {region ? t('admin.form.editTitle') : t('admin.form.addTitle')}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              name="name"
              label={t('admin.form.name')}
              value={formData.name}
              onChange={handleChange}
              error={!!errors.name}
              helperText={errors.name}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              name="coordinates"
              label={t('admin.form.coordinates')}
              value={formData.coordinates.join(',')}
              onChange={handleCoordinatesChange}
              error={!!errors.coordinates}
              helperText={errors.coordinates || t('admin.form.coordinatesHelp')}
              placeholder="latitude,longitude"
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

export default RegionForm;
