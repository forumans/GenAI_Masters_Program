"""SQLAlchemy ORM models for the HR Assistant application."""

import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Boolean,
    Numeric,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Enum types
# ---------------------------------------------------------------------------

class EmployeeStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"


class BenefitStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"


class LeaveType(str, enum.Enum):
    annual = "annual"
    sick = "sick"
    maternity = "maternity"
    paternity = "paternity"
    unpaid = "unpaid"
    compassionate = "compassionate"
    other = "other"


class LeaveStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class ExpenseStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    reimbursed = "reimbursed"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Department(Base):
    """Organisational department."""

    __tablename__ = "departments"
    __table_args__ = {"schema": "hr_assistant"}

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False, unique=True)
    description: Optional[str] = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    employees = relationship("Employee", back_populates="department", lazy="select")

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"


class Employee(Base):
    """Company employee master record."""

    __tablename__ = "employees"
    __table_args__ = {"schema": "hr_assistant"}

    id: int = Column(Integer, primary_key=True)
    employee_number: str = Column(String(20), nullable=False, unique=True)
    first_name: str = Column(String(100), nullable=False)
    last_name: str = Column(String(100), nullable=False)
    email: str = Column(String(255), nullable=False, unique=True)
    phone: Optional[str] = Column(String(30), nullable=True)
    department_id: int = Column(Integer, ForeignKey("hr_assistant.departments.id"), nullable=False)
    position: str = Column(String(150), nullable=False)
    hire_date: date = Column(Date, nullable=False)
    salary: Decimal = Column(Numeric(12, 2), nullable=False)
    status: EmployeeStatus = Column(
        SAEnum(EmployeeStatus, name="employee_status"),
        nullable=False,
        default=EmployeeStatus.active,
    )
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    department = relationship("Department", back_populates="employees")
    benefits = relationship("Benefit", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")
    expense_claims = relationship("ExpenseClaim", back_populates="employee", cascade="all, delete-orphan")
    onboarding_tasks = relationship("OnboardingTask", back_populates="employee", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Employee id={self.id} number={self.employee_number!r} name={self.full_name!r}>"


class Benefit(Base):
    """Employee benefit (health, dental, pension, etc.)."""

    __tablename__ = "benefits"
    __table_args__ = {"schema": "hr_assistant"}

    id: int = Column(Integer, primary_key=True)
    employee_id: int = Column(Integer, ForeignKey("hr_assistant.employees.id"), nullable=False)
    benefit_type: str = Column(String(100), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    start_date: date = Column(Date, nullable=False)
    end_date: Optional[date] = Column(Date, nullable=True)
    status: BenefitStatus = Column(
        SAEnum(BenefitStatus, name="benefit_status"),
        nullable=False,
        default=BenefitStatus.active,
    )

    employee = relationship("Employee", back_populates="benefits")

    def __repr__(self) -> str:
        return f"<Benefit id={self.id} type={self.benefit_type!r} employee_id={self.employee_id}>"


class LeaveRequest(Base):
    """Employee leave request."""

    __tablename__ = "leave_requests"
    __table_args__ = {"schema": "hr_assistant"}

    id: int = Column(Integer, primary_key=True)
    employee_id: int = Column(Integer, ForeignKey("hr_assistant.employees.id"), nullable=False)
    leave_type: LeaveType = Column(
        SAEnum(LeaveType, name="leave_type"), nullable=False
    )
    start_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    reason: Optional[str] = Column(Text, nullable=True)
    status: LeaveStatus = Column(
        SAEnum(LeaveStatus, name="leave_status"),
        nullable=False,
        default=LeaveStatus.pending,
    )
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee = relationship("Employee", back_populates="leave_requests")

    def __repr__(self) -> str:
        return (
            f"<LeaveRequest id={self.id} employee_id={self.employee_id} "
            f"type={self.leave_type} status={self.status}>"
        )


class ExpenseClaim(Base):
    """Employee expense reimbursement claim."""

    __tablename__ = "expense_claims"
    __table_args__ = {"schema": "hr_assistant"}

    id: int = Column(Integer, primary_key=True)
    employee_id: int = Column(Integer, ForeignKey("hr_assistant.employees.id"), nullable=False)
    amount: Decimal = Column(Numeric(10, 2), nullable=False)
    currency: str = Column(String(3), nullable=False, default="USD")
    description: str = Column(Text, nullable=False)
    category: str = Column(String(100), nullable=False)
    receipt_url: Optional[str] = Column(String(500), nullable=True)
    status: ExpenseStatus = Column(
        SAEnum(ExpenseStatus, name="expense_status"),
        nullable=False,
        default=ExpenseStatus.pending,
    )
    submitted_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at: Optional[datetime] = Column(DateTime, nullable=True)

    employee = relationship("Employee", back_populates="expense_claims")

    def __repr__(self) -> str:
        return (
            f"<ExpenseClaim id={self.id} employee_id={self.employee_id} "
            f"amount={self.amount} status={self.status}>"
        )


class OnboardingTask(Base):
    """Onboarding checklist task for a new employee."""

    __tablename__ = "onboarding_tasks"
    __table_args__ = {"schema": "hr_assistant"}

    id: int = Column(Integer, primary_key=True)
    employee_id: int = Column(Integer, ForeignKey("hr_assistant.employees.id"), nullable=False)
    task_name: str = Column(String(200), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    due_date: Optional[date] = Column(Date, nullable=True)
    completed: bool = Column(Boolean, nullable=False, default=False)
    completed_at: Optional[datetime] = Column(DateTime, nullable=True)

    employee = relationship("Employee", back_populates="onboarding_tasks")

    def __repr__(self) -> str:
        return (
            f"<OnboardingTask id={self.id} employee_id={self.employee_id} "
            f"task={self.task_name!r} completed={self.completed}>"
        )
