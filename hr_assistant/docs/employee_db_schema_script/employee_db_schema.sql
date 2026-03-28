-- =============================================================================
-- HR Assistant Database Schema
-- Run this script as the postgres superuser (or a role with CREATEDB privileges)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Database
-- ---------------------------------------------------------------------------
CREATE DATABASE hr_assistant_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Connect to the new database
\c hr_assistant_db;

-- ---------------------------------------------------------------------------
-- 2. Schema & Extensions
-- ---------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS hr_assistant
    AUTHORIZATION postgres;

SET search_path TO hr_assistant, public;

-- Set default search_path for all future connections to this database
ALTER DATABASE hr_assistant_db SET search_path TO hr_assistant, public;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

COMMENT ON SCHEMA hr_assistant IS 'HR Assistant application schema';

-- ---------------------------------------------------------------------------
-- 3. Shared trigger function (must exist before tables that reference it)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION hr_assistant.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- ---------------------------------------------------------------------------
-- 4. departments
-- ---------------------------------------------------------------------------
CREATE TABLE hr_assistant.departments (
    id               SERIAL          PRIMARY KEY,
    name             VARCHAR(100)    NOT NULL UNIQUE,
    description      TEXT,
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  hr_assistant.departments             IS 'Organisational departments within the company.';
COMMENT ON COLUMN hr_assistant.departments.id          IS 'Auto-incrementing primary key.';
COMMENT ON COLUMN hr_assistant.departments.name        IS 'Unique human-readable department name (e.g. Engineering, HR).';
COMMENT ON COLUMN hr_assistant.departments.description IS 'Optional free-text description of the department.';
COMMENT ON COLUMN hr_assistant.departments.created_at  IS 'UTC timestamp when the record was inserted.';

CREATE INDEX idx_departments_name ON hr_assistant.departments (name);

-- ---------------------------------------------------------------------------
-- 5. employees
-- ---------------------------------------------------------------------------
CREATE TYPE hr_assistant.employee_status AS ENUM ('active', 'inactive', 'on_leave');

CREATE TABLE hr_assistant.employees (
    id               SERIAL              PRIMARY KEY,
    employee_number  VARCHAR(20)         NOT NULL UNIQUE,
    first_name       VARCHAR(100)        NOT NULL,
    last_name        VARCHAR(100)        NOT NULL,
    email            VARCHAR(255)        NOT NULL UNIQUE,
    phone            VARCHAR(30),
    department_id    INTEGER             NOT NULL REFERENCES hr_assistant.departments (id) ON DELETE RESTRICT,
    position         VARCHAR(150)        NOT NULL,
    hire_date        DATE                NOT NULL,
    salary           NUMERIC(12, 2)      NOT NULL CHECK (salary >= 0),
    status           hr_assistant.employee_status  NOT NULL DEFAULT 'active',
    created_at       TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  hr_assistant.employees                 IS 'Master table for all company employees.';
COMMENT ON COLUMN hr_assistant.employees.id              IS 'Auto-incrementing surrogate primary key.';
COMMENT ON COLUMN hr_assistant.employees.employee_number IS 'Human-readable unique employee identifier (e.g. EMP-0001).';
COMMENT ON COLUMN hr_assistant.employees.first_name      IS 'Employee given name.';
COMMENT ON COLUMN hr_assistant.employees.last_name       IS 'Employee family name / surname.';
COMMENT ON COLUMN hr_assistant.employees.email           IS 'Work email address; must be unique across all employees.';
COMMENT ON COLUMN hr_assistant.employees.phone           IS 'Contact phone number (optional).';
COMMENT ON COLUMN hr_assistant.employees.department_id   IS 'Foreign key to hr_assistant.departments.';
COMMENT ON COLUMN hr_assistant.employees.position        IS 'Job title / position within the company.';
COMMENT ON COLUMN hr_assistant.employees.hire_date       IS 'Calendar date on which the employee started.';
COMMENT ON COLUMN hr_assistant.employees.salary          IS 'Annual gross salary in the company base currency.';
COMMENT ON COLUMN hr_assistant.employees.status          IS 'Current employment status: active, inactive, or on_leave.';
COMMENT ON COLUMN hr_assistant.employees.created_at      IS 'UTC timestamp when the record was first inserted.';
COMMENT ON COLUMN hr_assistant.employees.updated_at      IS 'UTC timestamp of the most recent update.';

CREATE INDEX idx_employees_department_id ON hr_assistant.employees (department_id);
CREATE INDEX idx_employees_status        ON hr_assistant.employees (status);
CREATE INDEX idx_employees_email         ON hr_assistant.employees (email);
CREATE INDEX idx_employees_hire_date     ON hr_assistant.employees (hire_date);
CREATE INDEX idx_employees_last_name     ON hr_assistant.employees (last_name);

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON hr_assistant.employees
    FOR EACH ROW EXECUTE FUNCTION hr_assistant.set_updated_at();

-- ---------------------------------------------------------------------------
-- 6. benefits
-- ---------------------------------------------------------------------------
CREATE TYPE hr_assistant.benefit_status AS ENUM ('active', 'inactive', 'pending');

CREATE TABLE hr_assistant.benefits (
    id           SERIAL             PRIMARY KEY,
    employee_id  INTEGER            NOT NULL REFERENCES hr_assistant.employees (id) ON DELETE CASCADE,
    benefit_type VARCHAR(100)       NOT NULL,
    description  TEXT,
    start_date   DATE               NOT NULL,
    end_date     DATE,
    status       hr_assistant.benefit_status  NOT NULL DEFAULT 'active',
    CONSTRAINT chk_benefit_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

COMMENT ON TABLE  hr_assistant.benefits              IS 'Employee benefits such as health insurance, dental, and pension plans.';
COMMENT ON COLUMN hr_assistant.benefits.id           IS 'Auto-incrementing primary key.';
COMMENT ON COLUMN hr_assistant.benefits.employee_id  IS 'Foreign key to the employee who owns this benefit.';
COMMENT ON COLUMN hr_assistant.benefits.benefit_type IS 'Category of benefit (e.g. Health Insurance, Dental, Pension).';
COMMENT ON COLUMN hr_assistant.benefits.description  IS 'Optional additional details about the benefit plan.';
COMMENT ON COLUMN hr_assistant.benefits.start_date   IS 'Date the benefit coverage begins.';
COMMENT ON COLUMN hr_assistant.benefits.end_date     IS 'Date the benefit coverage ends; NULL means currently open-ended.';
COMMENT ON COLUMN hr_assistant.benefits.status       IS 'Whether the benefit is currently active, inactive, or pending approval.';

CREATE INDEX idx_benefits_employee_id ON hr_assistant.benefits (employee_id);
CREATE INDEX idx_benefits_status      ON hr_assistant.benefits (status);

-- ---------------------------------------------------------------------------
-- 7. leave_requests
-- ---------------------------------------------------------------------------
CREATE TYPE hr_assistant.leave_type   AS ENUM ('annual', 'sick', 'maternity', 'paternity', 'unpaid', 'compassionate', 'other');
CREATE TYPE hr_assistant.leave_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled');

CREATE TABLE hr_assistant.leave_requests (
    id           SERIAL            PRIMARY KEY,
    employee_id  INTEGER           NOT NULL REFERENCES hr_assistant.employees (id) ON DELETE CASCADE,
    leave_type   hr_assistant.leave_type     NOT NULL,
    start_date   DATE              NOT NULL,
    end_date     DATE              NOT NULL,
    reason       TEXT,
    status       hr_assistant.leave_status   NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_leave_dates CHECK (end_date >= start_date)
);

COMMENT ON TABLE  hr_assistant.leave_requests             IS 'Employee leave requests including annual leave, sick leave, and parental leave.';
COMMENT ON COLUMN hr_assistant.leave_requests.id          IS 'Auto-incrementing primary key.';
COMMENT ON COLUMN hr_assistant.leave_requests.employee_id IS 'Foreign key to the employee submitting the request.';
COMMENT ON COLUMN hr_assistant.leave_requests.leave_type  IS 'Type of leave being requested.';
COMMENT ON COLUMN hr_assistant.leave_requests.start_date  IS 'First day of the requested leave period.';
COMMENT ON COLUMN hr_assistant.leave_requests.end_date    IS 'Last day of the requested leave period (inclusive).';
COMMENT ON COLUMN hr_assistant.leave_requests.reason      IS 'Employee-provided reason for the leave.';
COMMENT ON COLUMN hr_assistant.leave_requests.status      IS 'Current state of the request: pending, approved, rejected, or cancelled.';
COMMENT ON COLUMN hr_assistant.leave_requests.created_at  IS 'UTC timestamp when the request was submitted.';
COMMENT ON COLUMN hr_assistant.leave_requests.updated_at  IS 'UTC timestamp of the last status change.';

CREATE INDEX idx_leave_requests_employee_id ON hr_assistant.leave_requests (employee_id);
CREATE INDEX idx_leave_requests_status      ON hr_assistant.leave_requests (status);
CREATE INDEX idx_leave_requests_start_date  ON hr_assistant.leave_requests (start_date);

CREATE TRIGGER trg_leave_requests_updated_at
    BEFORE UPDATE ON hr_assistant.leave_requests
    FOR EACH ROW EXECUTE FUNCTION hr_assistant.set_updated_at();

-- ---------------------------------------------------------------------------
-- 8. expense_claims
-- ---------------------------------------------------------------------------
CREATE TYPE hr_assistant.expense_status AS ENUM ('pending', 'approved', 'rejected', 'reimbursed');

CREATE TABLE hr_assistant.expense_claims (
    id           SERIAL               PRIMARY KEY,
    employee_id  INTEGER              NOT NULL REFERENCES hr_assistant.employees (id) ON DELETE CASCADE,
    amount       NUMERIC(10, 2)       NOT NULL CHECK (amount > 0),
    currency     CHAR(3)              NOT NULL DEFAULT 'USD',
    description  TEXT                 NOT NULL,
    category     VARCHAR(100)         NOT NULL,
    receipt_url  VARCHAR(500),
    status       hr_assistant.expense_status    NOT NULL DEFAULT 'pending',
    submitted_at TIMESTAMPTZ          NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

COMMENT ON TABLE  hr_assistant.expense_claims              IS 'Employee expense reimbursement claims.';
COMMENT ON COLUMN hr_assistant.expense_claims.id           IS 'Auto-incrementing primary key.';
COMMENT ON COLUMN hr_assistant.expense_claims.employee_id  IS 'Foreign key to the employee submitting the claim.';
COMMENT ON COLUMN hr_assistant.expense_claims.amount       IS 'Claimed amount; must be positive.';
COMMENT ON COLUMN hr_assistant.expense_claims.currency     IS 'ISO 4217 three-letter currency code (e.g. USD, GBP, EUR).';
COMMENT ON COLUMN hr_assistant.expense_claims.description  IS 'Free-text description of the expense.';
COMMENT ON COLUMN hr_assistant.expense_claims.category     IS 'Expense category (e.g. Travel, Meals, Equipment, Training).';
COMMENT ON COLUMN hr_assistant.expense_claims.receipt_url  IS 'URL or path to the supporting receipt document.';
COMMENT ON COLUMN hr_assistant.expense_claims.status       IS 'Workflow state: pending, approved, rejected, or reimbursed.';
COMMENT ON COLUMN hr_assistant.expense_claims.submitted_at IS 'UTC timestamp when the claim was submitted.';
COMMENT ON COLUMN hr_assistant.expense_claims.processed_at IS 'UTC timestamp when the claim was approved or rejected.';

CREATE INDEX idx_expense_claims_employee_id  ON hr_assistant.expense_claims (employee_id);
CREATE INDEX idx_expense_claims_status       ON hr_assistant.expense_claims (status);
CREATE INDEX idx_expense_claims_submitted_at ON hr_assistant.expense_claims (submitted_at);

-- ---------------------------------------------------------------------------
-- 9. onboarding_tasks
-- ---------------------------------------------------------------------------
CREATE TABLE hr_assistant.onboarding_tasks (
    id           SERIAL       PRIMARY KEY,
    employee_id  INTEGER      NOT NULL REFERENCES hr_assistant.employees (id) ON DELETE CASCADE,
    task_name    VARCHAR(200) NOT NULL,
    description  TEXT,
    due_date     DATE,
    completed    BOOLEAN      NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ
);

COMMENT ON TABLE  hr_assistant.onboarding_tasks              IS 'Checklist tasks assigned to employees during the onboarding process.';
COMMENT ON COLUMN hr_assistant.onboarding_tasks.id           IS 'Auto-incrementing primary key.';
COMMENT ON COLUMN hr_assistant.onboarding_tasks.employee_id  IS 'Foreign key to the newly hired employee.';
COMMENT ON COLUMN hr_assistant.onboarding_tasks.task_name    IS 'Short name / title of the onboarding task.';
COMMENT ON COLUMN hr_assistant.onboarding_tasks.description  IS 'Detailed instructions for completing the task.';
COMMENT ON COLUMN hr_assistant.onboarding_tasks.due_date     IS 'Target completion date for the task.';
COMMENT ON COLUMN hr_assistant.onboarding_tasks.completed    IS 'TRUE once the task has been marked as done.';
COMMENT ON COLUMN hr_assistant.onboarding_tasks.completed_at IS 'UTC timestamp when the task was marked complete.';

CREATE INDEX idx_onboarding_tasks_employee_id ON hr_assistant.onboarding_tasks (employee_id);
CREATE INDEX idx_onboarding_tasks_completed   ON hr_assistant.onboarding_tasks (completed);
