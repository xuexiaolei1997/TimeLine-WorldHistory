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

const PeriodTable = ({ periods, onEdit, onDelete }) => {
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

  const sortedPeriods = periods.sort((a, b) => {
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
                  active={orderBy === 'startYear'}
                  direction={orderBy === 'startYear' ? order : 'asc'}
                  onClick={() => handleRequestSort('startYear')}
                >
                  {t('admin.table.startYear')}
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'endYear'}
                  direction={orderBy === 'endYear' ? order : 'asc'}
                  onClick={() => handleRequestSort('endYear')}
                >
                  {t('admin.table.endYear')}
                </TableSortLabel>
              </TableCell>
              <TableCell>{t('admin.table.description')}</TableCell>
              <TableCell>{t('admin.table.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedPeriods
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((period) => (
                <TableRow key={period.id}>
                  <TableCell>{period.name}</TableCell>
                  <TableCell>{period.startYear}</TableCell>
                  <TableCell>{period.endYear}</TableCell>
                  <TableCell>{period.description}</TableCell>
                  <TableCell>
                    <Tooltip title={t('admin.edit')}>
                      <IconButton onClick={() => onEdit(period)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('admin.delete')}>
                      <IconButton onClick={() => onDelete(period.id)}>
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
        count={periods.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage={t('admin.table.rowsPerPage')}
      />
    </Paper>
  );
};

export default PeriodTable;
