import React from "react";
import { Link } from "react-router-dom";
import { Pencil, Trash2, Eye } from "lucide-react";
import type { Employee } from "../types";

interface EmployeeListProps {
  employees: Employee[];
  onDelete: (id: number) => void;
}

const statusBadge: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  inactive: "bg-gray-100 text-gray-800",
  on_leave: "bg-yellow-100 text-yellow-800",
};

const EmployeeList: React.FC<EmployeeListProps> = ({ employees, onDelete }) => {
  if (employees.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500">
        No employees found. Add one to get started.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-gray-600 uppercase tracking-wide text-xs">
              Employee
            </th>
            <th className="px-4 py-3 text-left font-semibold text-gray-600 uppercase tracking-wide text-xs">
              Position
            </th>
            <th className="px-4 py-3 text-left font-semibold text-gray-600 uppercase tracking-wide text-xs">
              Department
            </th>
            <th className="px-4 py-3 text-left font-semibold text-gray-600 uppercase tracking-wide text-xs">
              Status
            </th>
            <th className="px-4 py-3 text-left font-semibold text-gray-600 uppercase tracking-wide text-xs">
              Hire Date
            </th>
            <th className="px-4 py-3 text-right font-semibold text-gray-600 uppercase tracking-wide text-xs">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100">
          {employees.map((emp) => (
            <tr key={emp.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3">
                <div className="font-medium text-gray-900">
                  {emp.first_name} {emp.last_name}
                </div>
                <div className="text-gray-500 text-xs">{emp.email}</div>
                <div className="text-gray-400 text-xs">{emp.employee_number}</div>
              </td>
              <td className="px-4 py-3 text-gray-700">{emp.position}</td>
              <td className="px-4 py-3 text-gray-700">
                {emp.department?.name ?? "—"}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    statusBadge[emp.status] ?? "bg-gray-100 text-gray-800"
                  }`}
                >
                  {emp.status.replace("_", " ")}
                </span>
              </td>
              <td className="px-4 py-3 text-gray-700">
                {new Date(emp.hire_date).toLocaleDateString()}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-2">
                  <Link
                    to={`/employees/${emp.id}`}
                    className="p-1.5 rounded text-gray-500 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                    title="View employee"
                  >
                    <Eye className="w-4 h-4" />
                  </Link>
                  <Link
                    to={`/employees/${emp.id}/edit`}
                    className="p-1.5 rounded text-gray-500 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                    title="Edit employee"
                  >
                    <Pencil className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => onDelete(emp.id)}
                    className="p-1.5 rounded text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
                    title="Delete employee"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default EmployeeList;
