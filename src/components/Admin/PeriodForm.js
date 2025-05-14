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

const PeriodForm = ({ open, period, onClose, onSubmit }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: '',
    startYear: '',
    endYear: '',
    description: ''
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (period) {
      setFormData({
        name: period.name || '',
        startYear: period.startYear || '',
        endYear: period.endYear || '',
        description: period.description || ''
      });
    } else {
      setFormData({
        name: '',
        startYear: '',
        endYear: '',
        description: ''
      });
    }
  }, [period]);

  const validate = () => {
    const newErrors = {};
    if (!formData.name) newErrors.name = t('admin.form.errors.required');
    if (!formData.startYear) newErrors.startYear = t('admin.form.errors.required');
    if (!formData.endYear) newErrors.endYear = t('admin.form.errors.required');
    if (parseInt(formData.endYear) < parseInt(formData.startYear)) {
      newErrors.endYear = t('admin.form.errors.invalidYear');
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validate()) {
      onSubmit({
        ...formData,
        startYear: parseInt(formData.startYear),
        endYear: parseInt(formData.endYear)
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

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {period ? t('admin.form.editTitle') : t('admin.form.addTitle')}
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
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="startYear"
              label={t('admin.form.startYear')}
              type="number"
              value={formData.startYear}
              onChange={handleChange}
              error={!!errors.startYear}
              helperText={errors.startYear}
              inputProps={{ min: -10000, max: 10000 }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="endYear"
              label={t('admin.form.endYear')}
              type="number"
              value={formData.endYear}
              onChange={handleChange}
              error={!!errors.endYear}
              helperText={errors.endYear}
              inputProps={{ min: -10000, max: 10000 }}
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

export default PeriodForm;
