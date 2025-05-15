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
  Typography,
  Rating,
  Switch,
  FormControlLabel,
  Chip,
  IconButton,
  Box,
  Tooltip,
  InputAdornment
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import AddIcon from '@mui/icons-material/Add';

const EventForm = ({ open, event, onClose, onSubmit }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    title: {
      en: '',
      zh: ''
    },
    period: '',
    startDate: '',
    endDate: '',
    location: {
      coordinates: [0, 0],
      zoomLevel: 3,
      highlightColor: '#FF0000',
      region_name: ''
    },
    description: {
      en: '',
      zh: ''
    },
    media: {
      images: [],
      videos: [],
      audios: [],
      thumbnail: ''
    },
    contentRefs: {
      articles: [],
      images: [],
      videos: [],
      documents: []
    },
    tags: {
      category: [],
      keywords: []
    },
    importance: 3,
    is_public: true
  });
  const [errors, setErrors] = useState({});
  const [newTag, setNewTag] = useState('');

  useEffect(() => {
    if (event) {
      setFormData({
        title: event.title || { en: '', zh: '' },
        period: event.period || '',
        startDate: event.startDate ? new Date(event.startDate).toISOString().split('T')[0] : '',
        endDate: event.endDate ? new Date(event.endDate).toISOString().split('T')[0] : '',
        location: event.location || {
          coordinates: [0, 0],
          zoomLevel: 3,
          highlightColor: '#FF0000',
          region_name: ''
        },
        description: event.description || { en: '', zh: '' },
        media: event.media || {
          images: [],
          videos: [],
          audios: [],
          thumbnail: ''
        },
        contentRefs: event.contentRefs || {
          articles: [],
          images: [],
          videos: [],
          documents: []
        },
        tags: event.tags || {
          category: [],
          keywords: []
        },
        importance: event.importance || 3,
        is_public: event.is_public !== false
      });
    }
  }, [event]);

  const validate = () => {
    const newErrors = {};
    if (!formData.title.en) newErrors['title.en'] = t('admin.form.errors.required');
    if (!formData.title.zh) newErrors['title.zh'] = t('admin.form.errors.required');
    if (!formData.period) newErrors.period = t('admin.form.errors.required');
    if (!formData.startDate) newErrors.startDate = t('admin.form.errors.required');
    if (!formData.endDate) newErrors.endDate = t('admin.form.errors.required');
    if (new Date(formData.endDate) < new Date(formData.startDate)) {
      newErrors.endDate = t('admin.form.errors.invalidDateRange');
    }
    if (!formData.description.en) newErrors['description.en'] = t('admin.form.errors.required');
    if (!formData.description.zh) newErrors['description.zh'] = t('admin.form.errors.required');
    if (!Array.isArray(formData.location.coordinates) || 
        formData.location.coordinates.length !== 2 ||
        formData.location.coordinates.some(coord => isNaN(coord))) {
      newErrors['location.coordinates'] = t('admin.form.errors.invalidCoordinates');
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
    setFormData(prev => {
      const newData = { ...prev };
      if (name.includes('.')) {
        const [parent, child] = name.split('.');
        newData[parent] = { ...newData[parent], [child]: value };
      } else {
        newData[name] = value;
      }
      return newData;
    });
  };

  const handleLocationChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      location: {
        ...prev.location,
        [name]: name === 'coordinates' ? value.split(',').map(Number) : value
      }
    }));
  };

  const handleTagAdd = (tagType) => {
    if (newTag.trim()) {
      setFormData(prev => ({
        ...prev,
        tags: {
          ...prev.tags,
          [tagType]: [...prev.tags[tagType], newTag.trim()]
        }
      }));
      setNewTag('');
    }
  };

  const handleTagDelete = (tagType, index) => {
    setFormData(prev => ({
      ...prev,
      tags: {
        ...prev.tags,
        [tagType]: prev.tags[tagType].filter((_, i) => i !== index)
      }
    }));
  };

  const handleContentRefAdd = (type) => {
    setFormData(prev => ({
      ...prev,
      contentRefs: {
        ...prev.contentRefs,
        [type]: [...prev.contentRefs[type], { type, url: '', title: '', description: '' }]
      }
    }));
  };

  const handleColorChange = (color) => {
    setFormData(prev => ({
      ...prev,
      location: {
        ...prev.location,
        highlightColor: color
      }
    }));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {event ? t('admin.form.editTitle') : t('admin.form.addTitle')}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* 标题（多语言） */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="title.en"
              label={t('admin.form.titleEn')}
              value={formData.title.en}
              onChange={handleChange}
              error={!!errors['title.en']}
              helperText={errors['title.en']}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="title.zh"
              label={t('admin.form.titleZh')}
              value={formData.title.zh}
              onChange={handleChange}
              error={!!errors['title.zh']}
              helperText={errors['title.zh']}
            />
          </Grid>

          {/* 时期选择 */}
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
                <MenuItem value="contemporary">{t('periods.contemporary')}</MenuItem>
              </Select>
              {errors.period && (
                <Typography variant="caption" color="error">
                  {errors.period}
                </Typography>
              )}
            </FormControl>
          </Grid>

          {/* 日期范围 */}
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

          {/* 位置信息 */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="coordinates"
              label={t('admin.form.coordinates')}
              value={formData.location.coordinates.join(',')}
              onChange={handleLocationChange}
              error={!!errors['location.coordinates']}
              helperText={errors['location.coordinates'] || t('admin.form.coordinatesHelp')}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="zoomLevel"
              label={t('admin.form.zoomLevel')}
              type="number"
              value={formData.location.zoomLevel}
              onChange={handleLocationChange}
              inputProps={{ min: 1, max: 20 }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="region_name"
              label={t('admin.form.regionName')}
              value={formData.location.region_name}
              onChange={handleLocationChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box>
              <InputLabel>{t('admin.form.highlightColor')}</InputLabel>
              <input
                type="color"
                value={formData.location.highlightColor}
                onChange={(e) => handleColorChange(e.target.value)}
                style={{
                  width: '100%',
                  height: '40px',
                  cursor: 'pointer'
                }}
              />
            </Box>
          </Grid>

          {/* 描述（多语言） */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="description.en"
              label={t('admin.form.descriptionEn')}
              value={formData.description.en}
              onChange={handleChange}
              multiline
              rows={4}
              error={!!errors['description.en']}
              helperText={errors['description.en']}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="description.zh"
              label={t('admin.form.descriptionZh')}
              value={formData.description.zh}
              onChange={handleChange}
              multiline
              rows={4}
              error={!!errors['description.zh']}
              helperText={errors['description.zh']}
            />
          </Grid>

          {/* 重要性和公开性 */}
          <Grid item xs={12} sm={6}>
            <Box>
              <Typography component="legend">{t('admin.form.importance')}</Typography>
              <Rating
                name="importance"
                value={formData.importance}
                onChange={(event, newValue) => {
                  handleChange({
                    target: { name: 'importance', value: newValue }
                  });
                }}
              />
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_public}
                  onChange={(e) => handleChange({
                    target: { name: 'is_public', value: e.target.checked }
                  })}
                  name="is_public"
                />
              }
              label={t('admin.form.isPublic')}
            />
          </Grid>

          {/* 标签 */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              {t('admin.form.tags')}
            </Typography>
            <Box sx={{ mb: 2 }}>
              <TextField
                size="small"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder={t('admin.form.newTag')}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => handleTagAdd('keywords')} size="small">
                        <AddIcon />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {formData.tags.keywords.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  onDelete={() => handleTagDelete('keywords', index)}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Grid>

          {/* 媒体和内容引用 */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              {t('admin.form.media')}
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              {['images', 'videos', 'audios'].map((type) => (
                <Button
                  key={type}
                  variant="outlined"
                  onClick={() => handleContentRefAdd(type)}
                  startIcon={<AddIcon />}
                >
                  {t(`admin.form.add${type.charAt(0).toUpperCase() + type.slice(1)}`)}
                </Button>
              ))}
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('admin.cancel')}</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          {t('admin.save')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EventForm;
