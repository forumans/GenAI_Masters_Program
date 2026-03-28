"""Tests for SQLAlchemy model validation and relationships."""

import pytest
from datetime import date, datetime

from app.models.employee import (
    Department,
    Employee,
    Benefit,
    LeaveRequest,
    ExpenseClaim,
    OnboardingTask,
    EmployeeStatus,
    LeaveStatus,
    ExpenseStatus,
    BenefitStatus,
)


class TestDepartmentModel:
    def test_department_creation(self, db):
        """Department can be created with required fields."""
        dept = Department(name="Marketing", description="Marketing team")
        db.session.add(dept)
        db.session.commit()
        assert dept.id is not None
        assert dept.name == "Marketing"
        assert dept.created_at is not None

    def test_department_repr(self, db, sample_department):
        """Department __repr__ contains id and name."""
        r = repr(sample_department)
        assert "Department" in r
        assert sample_department.name in r

    def test_department_requires_name(self, db):
        """Department without a name raises an IntegrityError on commit."""
        from sqlalchemy.exc import IntegrityError
        dept = Department()  # no name
        db.session.add(dept)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


class TestEmployeeModel:
    def test_employee_full_name(self, sample_employee):
        """Employee.full_name returns first and last name combined."""
        assert sample_employee.full_name == "Jane Doe"

    def test_employee_repr(self, sample_employee):
        """Employee __repr__ contains expected info."""
        r = repr(sample_employee)
        assert "Employee" in r
        assert "EMP-0001" in r

    def test_employee_default_status(self, db, sample_department):
        """Employee defaults to 'active' status."""
        emp = Employee(
            employee_number="EMP-0050",
            first_name="Bob",
            last_name="Test",
            email="bob.test@example.com",
            department_id=sample_department.id,
            position="Analyst",
            hire_date=date(2024, 1, 1),
            salary=55000,
        )
        db.session.add(emp)
        db.session.commit()
        assert emp.status == EmployeeStatus.active

    def test_employee_department_relationship(self, db, sample_employee, sample_department):
        """Employee.department returns the related Department object."""
        assert sample_employee.department is not None
        assert sample_employee.department.id == sample_department.id

    def test_employee_timestamps(self, db, sample_employee):
        """Employee has created_at and updated_at timestamps set on creation."""
        assert sample_employee.created_at is not None
        assert sample_employee.updated_at is not None


class TestBenefitModel:
    def test_benefit_creation(self, db, sample_employee):
        """Benefit can be created and linked to an employee."""
        benefit = Benefit(
            employee_id=sample_employee.id,
            benefit_type="Health Insurance",
            description="Company health plan",
            start_date=date(2022, 1, 15),
            status=BenefitStatus.active,
        )
        db.session.add(benefit)
        db.session.commit()
        assert benefit.id is not None
        assert benefit.employee_id == sample_employee.id

    def test_benefit_default_status(self, db, sample_employee):
        """Benefit defaults to 'active' status."""
        benefit = Benefit(
            employee_id=sample_employee.id,
            benefit_type="Dental",
            start_date=date(2022, 1, 15),
        )
        db.session.add(benefit)
        db.session.commit()
        assert benefit.status == BenefitStatus.active

    def test_benefit_cascade_delete(self, db, sample_department):
        """Deleting an employee cascade-deletes their benefits."""
        emp = Employee(
            employee_number="EMP-CASCADE-1",
            first_name="Cascade",
            last_name="Test",
            email="cascade.test@example.com",
            department_id=sample_department.id,
            position="Tester",
            hire_date=date(2023, 1, 1),
            salary=50000,
        )
        db.session.add(emp)
        db.session.commit()

        benefit = Benefit(
            employee_id=emp.id,
            benefit_type="Pension",
            start_date=date(2023, 1, 1),
        )
        db.session.add(benefit)
        db.session.commit()
        benefit_id = benefit.id

        db.session.delete(emp)
        db.session.commit()

        deleted_benefit = db.session.get(Benefit, benefit_id)
        assert deleted_benefit is None


class TestLeaveRequestModel:
    def test_leave_request_creation(self, db, sample_employee):
        """LeaveRequest can be created with required fields."""
        req = LeaveRequest(
            employee_id=sample_employee.id,
            leave_type="annual",
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 7),
            reason="Annual holiday",
        )
        db.session.add(req)
        db.session.commit()
        assert req.id is not None
        assert req.status == LeaveStatus.pending

    def test_leave_request_repr(self, db, sample_employee):
        """LeaveRequest __repr__ contains expected info."""
        req = LeaveRequest(
            employee_id=sample_employee.id,
            leave_type="sick",
            start_date=date(2024, 5, 1),
            end_date=date(2024, 5, 3),
        )
        db.session.add(req)
        db.session.commit()
        r = repr(req)
        assert "LeaveRequest" in r

    def test_leave_request_relationship(self, db, sample_employee):
        """LeaveRequest.employee returns the related Employee."""
        req = LeaveRequest(
            employee_id=sample_employee.id,
            leave_type="maternity",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 1),
        )
        db.session.add(req)
        db.session.commit()
        assert req.employee.id == sample_employee.id


class TestExpenseClaimModel:
    def test_expense_claim_creation(self, db, sample_employee):
        """ExpenseClaim can be created with required fields."""
        claim = ExpenseClaim(
            employee_id=sample_employee.id,
            amount=99.99,
            currency="USD",
            description="Conference ticket",
            category="Training",
        )
        db.session.add(claim)
        db.session.commit()
        assert claim.id is not None
        assert claim.status == ExpenseStatus.pending
        assert claim.submitted_at is not None

    def test_expense_claim_default_currency(self, db, sample_employee):
        """ExpenseClaim defaults to USD currency."""
        claim = ExpenseClaim(
            employee_id=sample_employee.id,
            amount=50.00,
            description="Taxi",
            category="Travel",
        )
        db.session.add(claim)
        db.session.commit()
        assert claim.currency == "USD"


class TestOnboardingTaskModel:
    def test_onboarding_task_creation(self, db, sample_employee):
        """OnboardingTask can be created with required fields."""
        task = OnboardingTask(
            employee_id=sample_employee.id,
            task_name="Complete IT setup",
            description="Set up laptop and install required software",
            due_date=date(2022, 1, 20),
        )
        db.session.add(task)
        db.session.commit()
        assert task.id is not None
        assert task.completed is False
        assert task.completed_at is None

    def test_onboarding_task_complete(self, db, sample_employee):
        """Marking an OnboardingTask as complete sets completed=True."""
        task = OnboardingTask(
            employee_id=sample_employee.id,
            task_name="Sign NDA",
            due_date=date(2022, 1, 20),
        )
        db.session.add(task)
        db.session.commit()

        task.completed = True
        task.completed_at = datetime.utcnow()
        db.session.commit()

        refreshed = db.session.get(OnboardingTask, task.id)
        assert refreshed.completed is True
        assert refreshed.completed_at is not None
