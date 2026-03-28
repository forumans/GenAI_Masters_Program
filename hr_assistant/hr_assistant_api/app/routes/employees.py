"""Employee and department CRUD routes."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.employee import Department, Employee, LeaveRequest, ExpenseClaim, OnboardingTask
from app.schemas.employee import (
    DepartmentCreate,
    DepartmentResponse,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    PaginatedEmployees,
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveRequestResponse,
    ExpenseClaimCreate,
    ExpenseClaimResponse,
    OnboardingTaskResponse,
)

router = APIRouter(prefix="/api")


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------

@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.scalars(select(Department).order_by(Department.name)).all()


@router.post("/departments", response_model=DepartmentResponse, status_code=201)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    dept = Department(name=payload.name, description=payload.description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

@router.get("/employees", response_model=PaginatedEmployees)
def list_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    stmt = select(Employee).options(joinedload(Employee.department))
    if department_id:
        stmt = stmt.where(Employee.department_id == department_id)
    if status:
        stmt = stmt.where(Employee.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    employees = db.scalars(
        stmt.order_by(Employee.last_name, Employee.first_name)
            .offset((page - 1) * per_page)
            .limit(per_page)
    ).unique().all()

    return {
        "items": employees,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.post("/employees", response_model=EmployeeResponse, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    emp = db.scalars(
        select(Employee).options(joinedload(Employee.department)).where(Employee.id == emp.id)
    ).first()
    return emp


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.scalars(
        select(Employee).options(joinedload(Employee.department)).where(Employee.id == employee_id)
    ).first()
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    return emp


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.scalars(
        select(Employee).options(joinedload(Employee.department)).where(Employee.id == employee_id)
    ).first()
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
    emp.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/employees/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(Employee, employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    db.delete(emp)
    db.commit()


# ---------------------------------------------------------------------------
# Leave Requests
# ---------------------------------------------------------------------------

@router.get("/employees/{employee_id}/leave-requests", response_model=list[LeaveRequestResponse])
def list_leave_requests(employee_id: int, db: Session = Depends(get_db)):
    if db.get(Employee, employee_id) is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    return db.scalars(
        select(LeaveRequest).where(LeaveRequest.employee_id == employee_id)
    ).all()


@router.post("/employees/{employee_id}/leave-requests", response_model=LeaveRequestResponse, status_code=201)
def create_leave_request(employee_id: int, payload: LeaveRequestCreate, db: Session = Depends(get_db)):
    if db.get(Employee, employee_id) is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    req = LeaveRequest(employee_id=employee_id, **payload.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.put("/employees/{employee_id}/leave-requests/{request_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    employee_id: int,
    request_id: int,
    payload: LeaveRequestUpdate,
    db: Session = Depends(get_db),
):
    if db.get(Employee, employee_id) is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    leave_req = db.get(LeaveRequest, request_id)
    if leave_req is None or leave_req.employee_id != employee_id:
        raise HTTPException(status_code=404, detail=f"Leave request {request_id} not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(leave_req, field, value)
    leave_req.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(leave_req)
    return leave_req


# ---------------------------------------------------------------------------
# Expense Claims
# ---------------------------------------------------------------------------

@router.get("/employees/{employee_id}/expense-claims", response_model=list[ExpenseClaimResponse])
def list_expense_claims(employee_id: int, db: Session = Depends(get_db)):
    if db.get(Employee, employee_id) is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    return db.scalars(
        select(ExpenseClaim).where(ExpenseClaim.employee_id == employee_id)
    ).all()


@router.post("/employees/{employee_id}/expense-claims", response_model=ExpenseClaimResponse, status_code=201)
def create_expense_claim(employee_id: int, payload: ExpenseClaimCreate, db: Session = Depends(get_db)):
    if db.get(Employee, employee_id) is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    claim = ExpenseClaim(employee_id=employee_id, **payload.model_dump())
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


# ---------------------------------------------------------------------------
# Onboarding Tasks
# ---------------------------------------------------------------------------

@router.get("/employees/{employee_id}/onboarding-tasks", response_model=list[OnboardingTaskResponse])
def list_onboarding_tasks(employee_id: int, db: Session = Depends(get_db)):
    if db.get(Employee, employee_id) is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found.")
    return db.scalars(
        select(OnboardingTask).where(OnboardingTask.employee_id == employee_id)
    ).all()
