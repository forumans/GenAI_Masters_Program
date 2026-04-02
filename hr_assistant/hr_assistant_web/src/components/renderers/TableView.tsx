import React from 'react';
import DataTable from './DataTable';
import type { TableData } from '../../types/response';

interface TableViewProps {
  data: TableData;
}

const TableView: React.FC<TableViewProps> = ({ data }) => {
  return <DataTable data={data} />;
};

export default TableView;
