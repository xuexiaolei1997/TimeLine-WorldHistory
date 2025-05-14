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
  Tooltip
} from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

const RegionTable = ({ regions, onEdit, onDelete }) => {
  const { t } = useTranslation();
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);
  const [order, setOrder] = React.useState('asc');
  const [orderBy, setOrderBy] = React.useState('name');

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

  const sortedRegions = regions.sort((a, b) => {
    if (order === 'asc') {
      return a[orderBy] > b[orderBy] ? 1 : -1;
    } else {
      return a[orderBy] < b[orderBy] ? 1 : -1;
    }
  });

  return (
    <Paper>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'name'}
                  direction={orderBy === 'name' ? order : 'asc'}
                  onClick={() => handleRequestSort('name')}
                >
                  {t('admin.table.name')}
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'coordinates'}
                  direction={orderBy === 'coordinates' ? order : 'asc'}
                  onClick={() => handleRequestSort('coordinates')}
                >
                  {t('admin.table.coordinates')}
                </TableSortLabel>
              </TableCell>
              <TableCell>{t('admin.table.description')}</TableCell>
              <TableCell>{t('admin.table.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRegions
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((region) => (
                <TableRow key={region.id}>
                  <TableCell>{region.name}</TableCell>
                  <TableCell>{region.coordinates.join(', ')}</TableCell>
                  <TableCell>{region.description}</TableCell>
                  <TableCell>
                    <Tooltip title={t('admin.edit')}>
                      <IconButton onClick={() => onEdit(region)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('admin.delete')}>
                      <IconButton onClick={() => onDelete(region.id)}>
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
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={regions.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage={t('admin.table.rowsPerPage')}
      />
    </Paper>
  );
};

export default RegionTable;
