import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import EmployeeList from "../components/EmployeeList";
import { employeesApi } from "../services/api";

const EmployeesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["employees", page, statusFilter],
    queryFn: () =>
      employeesApi.list({
        page,
        per_page: 15,
        status: statusFilter || undefined,
      }),
    placeholderData: (prev) => prev,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => employeesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employees"] });
    },
  });

  const handleDelete = (id: number) => {
    if (window.confirm("Are you sure you want to delete this employee?")) {
      deleteMutation.mutate(id);
    }
  };

  const employees = data?.items ?? [];
  const filtered = search.trim()
    ? employees.filter((e) => {
        const q = search.toLowerCase();
        return (
          e.first_name.toLowerCase().includes(q) ||
          e.last_name.toLowerCase().includes(q) ||
          e.email.toLowerCase().includes(q) ||
          e.employee_number.toLowerCase().includes(q)
        );
      })
    : employees;

  return (
    <div className="space-y-5">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
          <p className="text-sm text-gray-500">
            {data?.total ?? 0} total employee{data?.total !== 1 ? "s" : ""}
          </p>
        </div>
        <Link
          to="/employees/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Employee
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name, email, or number…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="sm:w-44 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="on_leave">On Leave</option>
        </select>
      </div>

      {/* Error */}
      {isError && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          Failed to load employees. Please check your API connection and try again.
        </div>
      )}

      {/* Delete error */}
      {deleteMutation.isError && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          Failed to delete employee. They may have associated records.
        </div>
      )}

      {/* List */}
      {isLoading ? (
        <div className="text-center py-16 text-gray-400">Loading employees…</div>
      ) : (
        <EmployeeList employees={filtered} onDelete={handleDelete} />
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            Page {data.page} of {data.pages}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded hover:bg-gray-100 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
              disabled={page === data.pages}
              className="p-1.5 rounded hover:bg-gray-100 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployeesPage;
