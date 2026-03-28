"""Tests for employee and department CRUD endpoints."""

import json
import pytest


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health_check(client):
    """GET /health should return 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------

class TestDepartments:
    def test_list_departments_empty(self, client, db):
        """GET /api/departments returns an empty list when no departments exist."""
        response = client.get("/api/departments")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_department(self, client, db):
        """POST /api/departments creates a new department and returns 201."""
        payload = {"name": "Finance", "description": "Finance and Accounting"}
        response = client.post(
            "/api/departments",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Finance"
        assert "id" in data

    def test_create_department_missing_name(self, client, db):
        """POST /api/departments without a name should return 422."""
        response = client.post(
            "/api/departments",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_list_departments_after_create(self, client, db, sample_department):
        """GET /api/departments returns the seeded department."""
        response = client.get("/api/departments")
        assert response.status_code == 200
        items = response.get_json()
        names = [d["name"] for d in items]
        assert sample_department.name in names


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

class TestEmployeesCreate:
    def test_create_employee(self, client, db, sample_department):
        """POST /api/employees creates a valid employee."""
        payload = {
            "employee_number": "EMP-0010",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "department_id": sample_department.id,
            "position": "DevOps Engineer",
            "hire_date": "2023-03-01",
            "salary": "80000.00",
            "status": "active",
        }
        response = client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == "john.smith@example.com"
        assert data["employee_number"] == "EMP-0010"

    def test_create_employee_invalid_email(self, client, db, sample_department):
        """POST /api/employees with bad email returns 422."""
        payload = {
            "employee_number": "EMP-0011",
            "first_name": "Bad",
            "last_name": "Email",
            "email": "not-an-email",
            "department_id": sample_department.id,
            "position": "Tester",
            "hire_date": "2023-01-01",
            "salary": "50000",
            "status": "active",
        }
        response = client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_create_employee_negative_salary(self, client, db, sample_department):
        """POST /api/employees with negative salary returns 422."""
        payload = {
            "employee_number": "EMP-0012",
            "first_name": "Jane",
            "last_name": "Rich",
            "email": "jane.rich@example.com",
            "department_id": sample_department.id,
            "position": "CEO",
            "hire_date": "2020-01-01",
            "salary": "-1000",
            "status": "active",
        }
        response = client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 422


class TestEmployeesRead:
    def test_list_employees(self, client, db, sample_employee):
        """GET /api/employees returns paginated results."""
        response = client.get("/api/employees")
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_get_employee_by_id(self, client, db, sample_employee):
        """GET /api/employees/<id> returns the correct employee."""
        response = client.get(f"/api/employees/{sample_employee.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_employee.id
        assert data["email"] == sample_employee.email

    def test_get_employee_not_found(self, client, db):
        """GET /api/employees/99999 returns 404."""
        response = client.get("/api/employees/99999")
        assert response.status_code == 404

    def test_list_employees_filter_status(self, client, db, sample_employee):
        """GET /api/employees?status=active returns only active employees."""
        response = client.get("/api/employees?status=active")
        assert response.status_code == 200
        data = response.get_json()
        for emp in data["items"]:
            assert emp["status"] == "active"


class TestEmployeesUpdate:
    def test_update_employee(self, client, db, sample_employee):
        """PUT /api/employees/<id> updates the employee."""
        payload = {"position": "Senior Software Engineer"}
        response = client.put(
            f"/api/employees/{sample_employee.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["position"] == "Senior Software Engineer"

    def test_update_employee_not_found(self, client, db):
        """PUT /api/employees/99999 returns 404."""
        response = client.put(
            "/api/employees/99999",
            data=json.dumps({"first_name": "Ghost"}),
            content_type="application/json",
        )
        assert response.status_code == 404


class TestEmployeesDelete:
    def test_delete_employee(self, client, db, sample_department):
        """DELETE /api/employees/<id> removes the employee and returns 204."""
        from app.models.employee import Employee
        from datetime import date

        emp = Employee(
            employee_number="EMP-DEL-01",
            first_name="Delete",
            last_name="Me",
            email="delete.me@example.com",
            department_id=sample_department.id,
            position="Temp",
            hire_date=date(2023, 6, 1),
            salary=40000,
            status="active",
        )
        db.session.add(emp)
        db.session.commit()

        response = client.delete(f"/api/employees/{emp.id}")
        assert response.status_code == 204

        # Verify gone
        get_response = client.get(f"/api/employees/{emp.id}")
        assert get_response.status_code == 404


# ---------------------------------------------------------------------------
# Leave Requests
# ---------------------------------------------------------------------------

class TestLeaveRequests:
    def test_list_leave_requests_empty(self, client, db, sample_employee):
        """GET /api/employees/<id>/leave-requests returns empty list."""
        response = client.get(f"/api/employees/{sample_employee.id}/leave-requests")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_leave_request(self, client, db, sample_employee):
        """POST /api/employees/<id>/leave-requests creates a leave request."""
        payload = {
            "leave_type": "annual",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "reason": "Summer vacation",
        }
        response = client.post(
            f"/api/employees/{sample_employee.id}/leave-requests",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["leave_type"] == "annual"
        assert data["status"] == "pending"

    def test_create_leave_request_employee_not_found(self, client, db):
        """POST /api/employees/99999/leave-requests returns 404."""
        payload = {
            "leave_type": "sick",
            "start_date": "2024-01-01",
            "end_date": "2024-01-03",
        }
        response = client.post(
            "/api/employees/99999/leave-requests",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Expense Claims
# ---------------------------------------------------------------------------

class TestExpenseClaims:
    def test_list_expense_claims_empty(self, client, db, sample_employee):
        """GET /api/employees/<id>/expense-claims returns empty list."""
        response = client.get(f"/api/employees/{sample_employee.id}/expense-claims")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_expense_claim(self, client, db, sample_employee):
        """POST /api/employees/<id>/expense-claims creates a claim."""
        payload = {
            "amount": "125.50",
            "currency": "USD",
            "description": "Team lunch",
            "category": "Meals",
        }
        response = client.post(
            f"/api/employees/{sample_employee.id}/expense-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert float(data["amount"]) == 125.50
        assert data["status"] == "pending"

    def test_create_expense_claim_zero_amount(self, client, db, sample_employee):
        """POST with zero amount should return 422."""
        payload = {
            "amount": "0",
            "currency": "USD",
            "description": "Free lunch",
            "category": "Meals",
        }
        response = client.post(
            f"/api/employees/{sample_employee.id}/expense-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 422
