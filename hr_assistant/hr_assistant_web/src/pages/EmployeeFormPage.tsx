import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import EmployeeForm from "../components/EmployeeForm";
import { employeesApi, departmentsApi } from "../services/api";
import type { EmployeeFormData } from "../types";

const EmployeeFormPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = !!id;
  const employeeId = id ? Number(id) : undefined;

  const { data: employee, isLoading: employeeLoading } = useQuery({
    queryKey: ["employee", employeeId],
    queryFn: () => employeesApi.get(employeeId!),
    enabled: isEdit,
  });

  const { data: departments = [], isLoading: depsLoading } = useQuery({
    queryKey: ["departments"],
    queryFn: () => departmentsApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: (data: EmployeeFormData) => employeesApi.create(data),
    onSuccess: (emp) => {
      queryClient.invalidateQueries({ queryKey: ["employees"] });
      navigate(`/employees/${emp.id}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: EmployeeFormData) => employeesApi.update(employeeId!, data),
    onSuccess: (emp) => {
      queryClient.invalidateQueries({ queryKey: ["employee", employeeId] });
      queryClient.invalidateQueries({ queryKey: ["employees"] });
      navigate(`/employees/${emp.id}`);
    },
  });

  const handleSubmit = async (data: EmployeeFormData) => {
    if (isEdit) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;
  const error = createMutation.error || updateMutation.error;

  if ((isEdit && employeeLoading) || depsLoading) {
    return (
      <div className="text-center py-20 text-gray-400">Loading…</div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      {/* Card */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h1 className="text-xl font-bold text-gray-900 mb-6">
          {isEdit ? "Edit Employee" : "New Employee"}
        </h1>

        {error && (
          <div className="mb-5 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
            {(error as any)?.response?.data?.error ??
              JSON.stringify((error as any)?.response?.data?.errors) ??
              "An error occurred. Please check the form and try again."}
          </div>
        )}

        <EmployeeForm
          initialData={employee}
          departments={departments}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />
      </div>
    </div>
  );
};

export default EmployeeFormPage;
