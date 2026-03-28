// ---------------------------------------------------------------------------
// Core domain types
// ---------------------------------------------------------------------------

export type EmployeeStatus = "active" | "inactive" | "on_leave";
export type BenefitStatus = "active" | "inactive" | "pending";
export type LeaveType =
  | "annual"
  | "sick"
  | "maternity"
  | "paternity"
  | "unpaid"
  | "compassionate"
  | "other";
export type LeaveStatus = "pending" | "approved" | "rejected" | "cancelled";
export type ExpenseStatus = "pending" | "approved" | "rejected" | "reimbursed";

export interface Department {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Employee {
  id: number;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  department_id: number;
  department: Department | null;
  position: string;
  hire_date: string;
  salary: string;
  status: EmployeeStatus;
  created_at: string;
  updated_at: string;
}

export interface Benefit {
  id: number;
  employee_id: number;
  benefit_type: string;
  description: string | null;
  start_date: string;
  end_date: string | null;
  status: BenefitStatus;
}

export interface LeaveRequest {
  id: number;
  employee_id: number;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  reason: string | null;
  status: LeaveStatus;
  created_at: string;
  updated_at: string;
}

export interface ExpenseClaim {
  id: number;
  employee_id: number;
  amount: string;
  currency: string;
  description: string;
  category: string;
  receipt_url: string | null;
  status: ExpenseStatus;
  submitted_at: string;
  processed_at: string | null;
}

export interface OnboardingTask {
  id: number;
  employee_id: number;
  task_name: string;
  description: string | null;
  due_date: string | null;
  completed: boolean;
  completed_at: string | null;
}

// ---------------------------------------------------------------------------
// Chat types
// ---------------------------------------------------------------------------

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: Date;
}

// ---------------------------------------------------------------------------
// API response wrappers
// ---------------------------------------------------------------------------

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface ApiError {
  error?: string;
  errors?: Record<string, string[]>;
  message?: string;
}

export type ApiResponse<T> = T | ApiError;

// ---------------------------------------------------------------------------
// Form types
// ---------------------------------------------------------------------------

export interface EmployeeFormData {
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  department_id: number | "";
  position: string;
  hire_date: string;
  salary: string;
  status: EmployeeStatus;
}

export interface LeaveRequestFormData {
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  reason: string;
}

export interface ExpenseClaimFormData {
  amount: string;
  currency: string;
  description: string;
  category: string;
  receipt_url: string;
}
