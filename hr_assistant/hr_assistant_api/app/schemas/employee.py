"""Pydantic v2 schemas for request validation and response serialisation."""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.employee import (
    EmployeeStatus,
    BenefitStatus,
    LeaveType,
    LeaveStatus,
    ExpenseStatus,
)


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Department name must not be blank.")
        return v.strip()


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------

class DepartmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class EmployeeCreate(BaseModel):
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department_id: int
    position: str
    hire_date: date
    salary: Decimal
    status: EmployeeStatus = EmployeeStatus.active

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email address.")
        return v.lower().strip()

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Salary cannot be negative.")
        return v

    @field_validator("employee_number")
    @classmethod
    def validate_employee_number(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Employee number must not be blank.")
        return v.strip().upper()


class EmployeeUpdate(BaseModel):
    employee_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    salary: Optional[Decimal] = None
    status: Optional[EmployeeStatus] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email address.")
        return v.lower().strip() if v else v

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("Salary cannot be negative.")
        return v

    @field_validator("employee_number")
    @classmethod
    def validate_employee_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Employee number must not be blank.")
        return v.strip().upper() if v else v


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department_id: int
    position: str
    hire_date: date  # Use date type but handle timezone in endpoints
    salary: Decimal
    status: EmployeeStatus
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentSummary] = None


class EmployeeEditResponse(BaseModel):
    """Response schema for edit form that includes date in ISO format for date input."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department_id: int
    position: str
    hire_date: str  # ISO format for date input (YYYY-MM-DD)
    hire_date_display: str  # Display format (MM/DD/YYYY)
    salary: Decimal
    status: EmployeeStatus
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentSummary] = None

    @classmethod
    def from_orm(cls, obj):
        """Create from ORM model with both date formats."""
        data = obj.__dict__.copy()
        if hasattr(obj, 'hire_date') and obj.hire_date:
            data['hire_date'] = obj.hire_date.strftime('%Y-%m-%d')  # ISO format for date input
            data['hire_date_display'] = obj.hire_date.strftime('%m/%d/%Y')  # Display format
        return cls(**data)


class PaginatedEmployees(BaseModel):
    items: list[EmployeeResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ---------------------------------------------------------------------------
# Leave Request
# ---------------------------------------------------------------------------

class LeaveRequestCreate(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "LeaveRequestCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date.")
        return self


class LeaveRequestUpdate(BaseModel):
    leave_type: Optional[LeaveType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[LeaveStatus] = None


class LeaveRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: LeaveStatus
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Expense Claim
# ---------------------------------------------------------------------------

class ExpenseClaimCreate(BaseModel):
    amount: Decimal
    currency: str = "USD"
    description: str
    category: str
    receipt_url: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO 4217 code.")
        return v.upper()


class ExpenseClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    amount: Decimal
    currency: str
    description: str
    category: str
    receipt_url: Optional[str] = None
    status: ExpenseStatus
    submitted_at: datetime
    processed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Onboarding Task
# ---------------------------------------------------------------------------

class OnboardingTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    task_name: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: bool
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    employee_id: Optional[int] = None
    conversation_history: Optional[List[dict]] = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message must not be empty.")
        return v.strip()


class ChatResponse(BaseModel):
    response: str
