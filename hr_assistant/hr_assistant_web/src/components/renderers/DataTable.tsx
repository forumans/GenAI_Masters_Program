import React, { useState, useMemo } from 'react';
import type { TableData } from '../../types/response';

interface DataTableProps {
  data: TableData;
}

const DataTable: React.FC<DataTableProps> = ({ data }) => {
  const [search, setSearch] = useState("");
  const [sortColumn, setSortColumn] = useState<number | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Filter rows based on search
  const filteredRows = useMemo(() => {
    if (!search) return data.rows;
    
    return data.rows.filter((row) =>
      row.some((cell) =>
        cell?.toLowerCase().includes(search.toLowerCase())
      )
    );
  }, [data.rows, search]);

  // Sort rows based on column
  const sortedRows = useMemo(() => {
    if (sortColumn === null) return filteredRows;
    
    return [...filteredRows].sort((a, b) => {
      const aValue = a[sortColumn] || '';
      const bValue = b[sortColumn] || '';
      
      const comparison = aValue.localeCompare(bValue);
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [filteredRows, sortColumn, sortDirection]);

  const handleSort = (columnIndex: number) => {
    if (sortColumn === columnIndex) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnIndex);
      setSortDirection('asc');
    }
  };

  return (
    <div className="space-y-3">
      {/* Search Input */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search table..."
          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <svg
          className="absolute right-3 top-2.5 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Results count */}
      {search && (
        <div className="text-sm text-gray-600">
          Showing {sortedRows.length} of {data.rows.length} results
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {data.columns.map((col, i) => (
                <th
                  key={i}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort(i)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{col}</span>
                    {sortColumn === i && (
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        {sortDirection === 'asc' ? (
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 15l7-7 7 7"
                          />
                        ) : (
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                          />
                        )}
                      </svg>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedRows.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50">
                {row.map((cell, j) => (
                  <td key={j} className="px-4 py-3 text-sm text-gray-900">
                    {cell || ''}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* No results */}
      {sortedRows.length === 0 && (
        <div className="text-center text-gray-500 py-4">
          No matching records found
        </div>
      )}
    </div>
  );
};

export default DataTable;
