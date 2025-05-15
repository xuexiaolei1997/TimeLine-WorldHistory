import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  TableSortLabel,
  IconButton,
  Tooltip,
  Chip,
  Rating,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography
} from '@mui/material';
import { Edit, Delete, Visibility, Language } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

const EventTable = ({ events, onEdit, onDelete }) => {
  const { t, i18n } = useTranslation();
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);
  const [order, setOrder] = React.useState('asc');
  const [orderBy, setOrderBy] = React.useState('title');
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [eventToDelete, setEventToDelete] = React.useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = React.useState(false);
  const [selectedEvent, setSelectedEvent] = React.useState(null);

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleDeleteClick = (event) => {
    setEventToDelete(event);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (eventToDelete) {
      onDelete(eventToDelete.id);
    }
    setDeleteDialogOpen(false);
    setEventToDelete(null);
  };

  const handleDetailClick = (event) => {
    setSelectedEvent(event);
    setDetailDialogOpen(true);
  };

  const sortedEvents = events.sort((a, b) => {
    const aValue = a[orderBy];
    const bValue = b[orderBy];

    if (orderBy === 'title') {
      return order === 'asc'
        ? aValue[i18n.language].localeCompare(bValue[i18n.language])
        : bValue[i18n.language].localeCompare(aValue[i18n.language]);
    }

    if (orderBy === 'date') {
      const aDate = new Date(aValue.start);
      const bDate = new Date(bValue.start);
      return order === 'asc' ? aDate - bDate : bDate - aDate;
    }

    return order === 'asc'
      ? aValue > bValue ? 1 : -1
      : bValue > aValue ? 1 : -1;
  });

  return (
    <Paper sx={{ width: '100%', mb: 2 }}>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'title'}
                  direction={orderBy === 'title' ? order : 'asc'}
                  onClick={() => handleRequestSort('title')}
                >
                  {t('admin.table.title')}
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'period'}
                  direction={orderBy === 'period' ? order : 'asc'}
                  onClick={() => handleRequestSort('period')}
                >
                  {t('admin.table.period')}
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'date'}
                  direction={orderBy === 'date' ? order : 'asc'}
                  onClick={() => handleRequestSort('date')}
                >
                  {t('admin.table.date')}
                </TableSortLabel>
              </TableCell>
              <TableCell>{t('admin.table.importance')}</TableCell>
              <TableCell>{t('admin.table.tags')}</TableCell>
              <TableCell>{t('admin.table.status')}</TableCell>
              <TableCell align="center">{t('admin.table.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedEvents
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((event) => (
                <TableRow key={event.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {event.title[i18n.language]}
                      <Tooltip title={t('admin.table.multiLang')}>
                        <Language fontSize="small" color="action" />
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {t(`periods.${event.period}`)}
                  </TableCell>
                  <TableCell>
                    <Tooltip title={`${t('admin.table.endDate')}: ${new Date(event.date.end).toLocaleDateString()}`}>
                      <span>{new Date(event.date.start).toLocaleDateString()}</span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Rating value={event.importance} readOnly size="small" />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {event.tags.keywords.slice(0, 2).map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                      {event.tags.keywords.length > 2 && (
                        <Chip
                          label={`+${event.tags.keywords.length - 2}`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={event.is_public ? t('admin.table.public') : t('admin.table.private')}
                      color={event.is_public ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title={t('admin.view')}>
                      <IconButton onClick={() => handleDetailClick(event)} size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('admin.edit')}>
                      <IconButton onClick={() => onEdit(event)} size="small">
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('admin.delete')}>
                      <IconButton onClick={() => handleDeleteClick(event)} size="small" color="error">
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={events.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage={t('admin.table.rowsPerPage')}
      />

      {/* 删除确认对话框 */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>{t('admin.deleteConfirmTitle')}</DialogTitle>
        <DialogContent>
          <Typography>
            {t('admin.deleteConfirmMessage', {
              title: eventToDelete?.title[i18n.language]
            })}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            {t('admin.cancel')}
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            {t('admin.delete')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 详情对话框 */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedEvent?.title[i18n.language]}
        </DialogTitle>
        <DialogContent>
          {selectedEvent && (
            <Box sx={{ '& > *': { mb: 2 } }}>
              <Typography variant="h6">{t('admin.form.description')}</Typography>
              <Typography>{selectedEvent.description[i18n.language]}</Typography>

              <Typography variant="h6">{t('admin.form.location')}</Typography>
              <Typography>
                {t('admin.form.coordinates')}: {selectedEvent.location.coordinates.join(', ')}
              </Typography>
              <Typography>
                {t('admin.form.region')}: {selectedEvent.location.region_name}
              </Typography>

              <Typography variant="h6">{t('admin.form.media')}</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {selectedEvent.media.images.length > 0 && (
                  <Chip label={`${selectedEvent.media.images.length} ${t('admin.images')}`} />
                )}
                {selectedEvent.media.videos.length > 0 && (
                  <Chip label={`${selectedEvent.media.videos.length} ${t('admin.videos')}`} />
                )}
                {selectedEvent.media.audios.length > 0 && (
                  <Chip label={`${selectedEvent.media.audios.length} ${t('admin.audios')}`} />
                )}
              </Box>

              <Typography variant="h6">{t('admin.form.tags')}</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {selectedEvent.tags.keywords.map((tag, index) => (
                  <Chip key={index} label={tag} variant="outlined" />
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>
            {t('admin.close')}
          </Button>
          <Button
            onClick={() => {
              setDetailDialogOpen(false);
              onEdit(selectedEvent);
            }}
            color="primary"
          >
            {t('admin.edit')}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default EventTable;
