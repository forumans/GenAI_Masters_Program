import React from 'react';
import type { TableData } from '../../types/response';

interface TableViewProps {
  data: TableData;
}

const TableView: React.FC<TableViewProps> = ({ data }) => (
  <div className="overflow-x-auto">
    <table className="min-w-full border text-sm">
      <thead className="bg-gray-100">
        <tr>
          {data.columns.map((col, i) => (
            <th key={i} className="px-3 py-2 border text-left">
              {col}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.rows.map((row, i) => (
          <tr key={i} className="hover:bg-gray-50">
            {row.map((cell, j) => (
              <td key={j} className="px-3 py-2 border">
                {cell || ''}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default TableView;
