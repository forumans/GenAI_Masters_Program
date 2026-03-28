import React, { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Pencil, ArrowLeft, CheckCircle2, Clock, XCircle } from "lucide-react";
import {
  employeesApi,
  leaveRequestsApi,
  expenseClaimsApi,
  onboardingTasksApi,
} from "../services/api";
import type { LeaveStatus, ExpenseStatus } from "../types";

type TabKey = "leave" | "expenses" | "onboarding";

const statusColors: Record<LeaveStatus | ExpenseStatus, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  cancelled: "bg-gray-100 text-gray-800",
  reimbursed: "bg-blue-100 text-blue-800",
};

const EmployeeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const employeeId = Number(id);
  const [activeTab, setActiveTab] = useState<TabKey>("leave");

  const { data: employee, isLoading, isError } = useQuery({
    queryKey: ["employee", employeeId],
    queryFn: () => employeesApi.get(employeeId),
    enabled: !!employeeId,
  });

  const { data: leaveRequests = [] } = useQuery({
    queryKey: ["leave-requests", employeeId],
    queryFn: () => leaveRequestsApi.list(employeeId),
    enabled: !!employeeId && activeTab === "leave",
  });

  const { data: expenseClaims = [] } = useQuery({
    queryKey: ["expense-claims", employeeId],
    queryFn: () => expenseClaimsApi.list(employeeId),
    enabled: !!employeeId && activeTab === "expenses",
  });

  const { data: onboardingTasks = [] } = useQuery({
    queryKey: ["onboarding-tasks", employeeId],
    queryFn: () => onboardingTasksApi.list(employeeId),
    enabled: !!employeeId && activeTab === "onboarding",
  });

  if (isLoading) {
    return <div className="text-center py-20 text-gray-400">Loading employee…</div>;
  }

  if (isError || !employee) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600 mb-4">Employee not found.</p>
        <Link to="/employees" className="text-primary-600 hover:underline text-sm">
          Back to employees
        </Link>
      </div>
    );
  }

  const tabs: { key: TabKey; label: string }[] = [
    { key: "leave", label: "Leave Requests" },
    { key: "expenses", label: "Expense Claims" },
    { key: "onboarding", label: "Onboarding Tasks" },
  ];

  const tabClass = (key: TabKey) =>
    [
      "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
      activeTab === key
        ? "border-primary-600 text-primary-600"
        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300",
    ].join(" ");

  return (
    <div className="space-y-6">
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      {/* Header card */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {employee.first_name} {employee.last_name}
            </h1>
            <p className="text-gray-500">{employee.position}</p>
            <p className="text-xs text-gray-400 mt-1">{employee.employee_number}</p>
          </div>
          <Link
            to={`/employees/${employeeId}/edit`}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Pencil className="w-4 h-4" />
            Edit
          </Link>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <Detail label="Email" value={employee.email} />
          <Detail label="Phone" value={employee.phone ?? "—"} />
          <Detail label="Department" value={employee.department?.name ?? "—"} />
          <Detail label="Hire Date" value={new Date(employee.hire_date).toLocaleDateString()} />
          <Detail label="Salary" value={`$${Number(employee.salary).toLocaleString()}`} />
          <Detail
            label="Status"
            value={
              <span
                className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                  {
                    active: "bg-green-100 text-green-800",
                    inactive: "bg-gray-100 text-gray-800",
                    on_leave: "bg-yellow-100 text-yellow-800",
                  }[employee.status]
                }`}
              >
                {employee.status.replace("_", " ")}
              </span>
            }
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
        <div className="flex border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              className={tabClass(tab.key)}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-4">
          {/* Leave Requests */}
          {activeTab === "leave" && (
            <div className="space-y-2">
              {leaveRequests.length === 0 ? (
                <p className="text-gray-400 text-sm py-6 text-center">No leave requests found.</p>
              ) : (
                leaveRequests.map((req) => (
                  <div
                    key={req.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
                  >
                    <div>
                      <span className="font-medium capitalize">{req.leave_type}</span>
                      <span className="text-gray-500 ml-2">
                        {new Date(req.start_date).toLocaleDateString()} –{" "}
                        {new Date(req.end_date).toLocaleDateString()}
                      </span>
                      {req.reason && (
                        <p className="text-gray-400 text-xs mt-0.5">{req.reason}</p>
                      )}
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[req.status]}`}
                    >
                      {req.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Expense Claims */}
          {activeTab === "expenses" && (
            <div className="space-y-2">
              {expenseClaims.length === 0 ? (
                <p className="text-gray-400 text-sm py-6 text-center">No expense claims found.</p>
              ) : (
                expenseClaims.map((claim) => (
                  <div
                    key={claim.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
                  >
                    <div>
                      <span className="font-medium">
                        {claim.currency} {Number(claim.amount).toFixed(2)}
                      </span>
                      <span className="text-gray-500 ml-2 capitalize">{claim.category}</span>
                      <p className="text-gray-400 text-xs mt-0.5">{claim.description}</p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[claim.status]}`}
                    >
                      {claim.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Onboarding Tasks */}
          {activeTab === "onboarding" && (
            <div className="space-y-2">
              {onboardingTasks.length === 0 ? (
                <p className="text-gray-400 text-sm py-6 text-center">No onboarding tasks found.</p>
              ) : (
                onboardingTasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg text-sm"
                  >
                    {task.completed ? (
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    ) : (
                      <Clock className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className={`font-medium ${task.completed ? "line-through text-gray-400" : "text-gray-900"}`}>
                        {task.task_name}
                      </p>
                      {task.description && (
                        <p className="text-gray-400 text-xs mt-0.5">{task.description}</p>
                      )}
                      {task.due_date && !task.completed && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Due: {new Date(task.due_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const Detail: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div>
    <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
    <p className="text-sm font-medium text-gray-900 mt-0.5">{value}</p>
  </div>
);

export default EmployeeDetailPage;
