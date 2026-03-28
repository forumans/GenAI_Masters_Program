import axios, { AxiosInstance } from "axios";
import type {
  Employee,
  Department,
  LeaveRequest,
  ExpenseClaim,
  OnboardingTask,
  PaginatedResponse,
  EmployeeFormData,
  LeaveRequestFormData,
  ExpenseClaimFormData,
} from "../types";

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const API_BASE = process.env.REACT_APP_API_URL ?? "http://localhost:5000";

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30_000,
});

// ---------------------------------------------------------------------------
// Departments
// ---------------------------------------------------------------------------

export const departmentsApi = {
  list: (): Promise<Department[]> =>
    api.get<Department[]>("/api/departments").then((r) => r.data),

  create: (data: { name: string; description?: string }): Promise<Department> =>
    api.post<Department>("/api/departments", data).then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Employees
// ---------------------------------------------------------------------------

export interface ListEmployeesParams {
  page?: number;
  per_page?: number;
  department_id?: number;
  status?: string;
}

export const employeesApi = {
  list: (params?: ListEmployeesParams): Promise<PaginatedResponse<Employee>> =>
    api
      .get<PaginatedResponse<Employee>>("/api/employees", { params })
      .then((r) => r.data),

  get: (id: number): Promise<Employee> =>
    api.get<Employee>(`/api/employees/${id}`).then((r) => r.data),

  create: (data: EmployeeFormData): Promise<Employee> =>
    api.post<Employee>("/api/employees", data).then((r) => r.data),

  update: (id: number, data: Partial<EmployeeFormData>): Promise<Employee> =>
    api.put<Employee>(`/api/employees/${id}`, data).then((r) => r.data),

  delete: (id: number): Promise<void> =>
    api.delete(`/api/employees/${id}`).then(() => undefined),
};

// ---------------------------------------------------------------------------
// Leave Requests
// ---------------------------------------------------------------------------

export const leaveRequestsApi = {
  list: (employeeId: number): Promise<LeaveRequest[]> =>
    api
      .get<LeaveRequest[]>(`/api/employees/${employeeId}/leave-requests`)
      .then((r) => r.data),

  create: (
    employeeId: number,
    data: LeaveRequestFormData
  ): Promise<LeaveRequest> =>
    api
      .post<LeaveRequest>(
        `/api/employees/${employeeId}/leave-requests`,
        data
      )
      .then((r) => r.data),

  update: (
    employeeId: number,
    requestId: number,
    data: Partial<LeaveRequestFormData> & { status?: string }
  ): Promise<LeaveRequest> =>
    api
      .put<LeaveRequest>(
        `/api/employees/${employeeId}/leave-requests/${requestId}`,
        data
      )
      .then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Expense Claims
// ---------------------------------------------------------------------------

export const expenseClaimsApi = {
  list: (employeeId: number): Promise<ExpenseClaim[]> =>
    api
      .get<ExpenseClaim[]>(`/api/employees/${employeeId}/expense-claims`)
      .then((r) => r.data),

  create: (
    employeeId: number,
    data: ExpenseClaimFormData
  ): Promise<ExpenseClaim> =>
    api
      .post<ExpenseClaim>(
        `/api/employees/${employeeId}/expense-claims`,
        data
      )
      .then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Onboarding Tasks
// ---------------------------------------------------------------------------

export const onboardingTasksApi = {
  list: (employeeId: number): Promise<OnboardingTask[]> =>
    api
      .get<OnboardingTask[]>(`/api/employees/${employeeId}/onboarding-tasks`)
      .then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

export interface ChatRequest {
  message: string;
  employee_id?: number;
}

export interface ChatResponse {
  response: string;
}

export const chatApi = {
  send: (data: ChatRequest): Promise<ChatResponse> =>
    api.post<ChatResponse>("/api/chat", data).then((r) => r.data),

  sendStream: async function* (
    data: ChatRequest
  ): AsyncGenerator<string, void, unknown> {
    const response = await fetch(`${API_BASE}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Stream request failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const raw = line.slice(6).trim();
          if (!raw) continue;
          try {
            const parsed = JSON.parse(raw);
            if (parsed.done) return;
            if (parsed.error) throw new Error(parsed.error);
            if (parsed.token) yield parsed.token;
          } catch {
            // ignore malformed events
          }
        }
      }
    }
  },
};

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export const healthApi = {
  check: (): Promise<{ status: string }> =>
    api.get<{ status: string }>("/health").then((r) => r.data),
};

export default api;
