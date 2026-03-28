import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import type { Employee, Department, EmployeeFormData } from "../types";

interface EmployeeFormProps {
  initialData?: Employee;
  departments: Department[];
  onSubmit: (data: EmployeeFormData) => Promise<void>;
  isSubmitting: boolean;
}

const EmployeeForm: React.FC<EmployeeFormProps> = ({
  initialData,
  departments,
  onSubmit,
  isSubmitting,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EmployeeFormData>({
    defaultValues: {
      employee_number: "",
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      department_id: "",
      position: "",
      hire_date: "",
      salary: "",
      status: "active",
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        employee_number: initialData.employee_number,
        first_name: initialData.first_name,
        last_name: initialData.last_name,
        email: initialData.email,
        phone: initialData.phone ?? "",
        department_id: initialData.department_id,
        position: initialData.position,
        hire_date: initialData.hire_date,
        salary: initialData.salary,
        status: initialData.status,
      });
    }
  }, [initialData, reset]);

  const inputClass =
    "block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none disabled:bg-gray-100";

  const labelClass = "block text-sm font-medium text-gray-700 mb-1";
  const errorClass = "mt-1 text-xs text-red-600";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Employee Number */}
        <div>
          <label className={labelClass}>Employee Number *</label>
          <input
            {...register("employee_number", {
              required: "Employee number is required",
            })}
            className={inputClass}
            placeholder="EMP-0001"
          />
          {errors.employee_number && (
            <p className={errorClass}>{errors.employee_number.message}</p>
          )}
        </div>

        {/* Status */}
        <div>
          <label className={labelClass}>Status *</label>
          <select
            {...register("status", { required: "Status is required" })}
            className={inputClass}
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="on_leave">On Leave</option>
          </select>
        </div>

        {/* First Name */}
        <div>
          <label className={labelClass}>First Name *</label>
          <input
            {...register("first_name", { required: "First name is required" })}
            className={inputClass}
            placeholder="Jane"
          />
          {errors.first_name && (
            <p className={errorClass}>{errors.first_name.message}</p>
          )}
        </div>

        {/* Last Name */}
        <div>
          <label className={labelClass}>Last Name *</label>
          <input
            {...register("last_name", { required: "Last name is required" })}
            className={inputClass}
            placeholder="Doe"
          />
          {errors.last_name && (
            <p className={errorClass}>{errors.last_name.message}</p>
          )}
        </div>

        {/* Email */}
        <div>
          <label className={labelClass}>Email *</label>
          <input
            {...register("email", {
              required: "Email is required",
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: "Enter a valid email address",
              },
            })}
            type="email"
            className={inputClass}
            placeholder="jane.doe@company.com"
          />
          {errors.email && (
            <p className={errorClass}>{errors.email.message}</p>
          )}
        </div>

        {/* Phone */}
        <div>
          <label className={labelClass}>Phone</label>
          <input
            {...register("phone")}
            type="tel"
            className={inputClass}
            placeholder="+1 555 000 0000"
          />
        </div>

        {/* Department */}
        <div>
          <label className={labelClass}>Department *</label>
          <select
            {...register("department_id", {
              required: "Department is required",
              validate: (v) => v !== "" || "Department is required",
            })}
            className={inputClass}
          >
            <option value="">Select department…</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
          {errors.department_id && (
            <p className={errorClass}>{errors.department_id.message}</p>
          )}
        </div>

        {/* Position */}
        <div>
          <label className={labelClass}>Position *</label>
          <input
            {...register("position", { required: "Position is required" })}
            className={inputClass}
            placeholder="Software Engineer"
          />
          {errors.position && (
            <p className={errorClass}>{errors.position.message}</p>
          )}
        </div>

        {/* Hire Date */}
        <div>
          <label className={labelClass}>Hire Date *</label>
          <input
            {...register("hire_date", { required: "Hire date is required" })}
            type="date"
            className={inputClass}
          />
          {errors.hire_date && (
            <p className={errorClass}>{errors.hire_date.message}</p>
          )}
        </div>

        {/* Salary */}
        <div>
          <label className={labelClass}>Annual Salary *</label>
          <input
            {...register("salary", {
              required: "Salary is required",
              min: { value: 0, message: "Salary cannot be negative" },
            })}
            type="number"
            step="0.01"
            min="0"
            className={inputClass}
            placeholder="60000"
          />
          {errors.salary && (
            <p className={errorClass}>{errors.salary.message}</p>
          )}
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center px-6 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? "Saving…" : initialData ? "Update Employee" : "Create Employee"}
        </button>
      </div>
    </form>
  );
};

export default EmployeeForm;
