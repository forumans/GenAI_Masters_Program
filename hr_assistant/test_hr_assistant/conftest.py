"""Pytest configuration and shared fixtures for the HR Assistant test suite."""

import pytest
from datetime import date
from unittest.mock import MagicMock

from starlette.testclient import TestClient

from app import create_app
from app.database import Base, engine, SessionLocal
from app.models.employee import Department, Employee


@pytest.fixture(scope="session")
def app():
    """Create a FastAPI application configured for testing.

    Yields:
        FastAPI application instance.
    """
    application = create_app()
    Base.metadata.create_all(bind=engine)
    yield application
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client(app):
    """Return a Starlette TestClient for the test session.

    Args:
        app: The testing FastAPI application.

    Yields:
        TestClient instance.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def db():
    """Provide a clean database session for each test.

    Wraps every test in a transaction and rolls it back on teardown so each
    test starts with a fresh state.

    Yields:
        SQLAlchemy Session.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def sample_department(db):
    """Create and persist a sample department for use in tests.

    Args:
        db: The db fixture.

    Returns:
        Department instance.
    """
    dept = Department(name="Engineering", description="Software Engineering department")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@pytest.fixture()
def sample_employee(db, sample_department):
    """Create and persist a sample employee for use in tests.

    Args:
        db: The db fixture.
        sample_department: Department fixture.

    Returns:
        Employee instance.
    """
    emp = Employee(
        employee_number="EMP-0001",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="+1-555-000-0001",
        department_id=sample_department.id,
        position="Software Engineer",
        hire_date=date(2022, 1, 15),
        salary=75000.00,
        status="active",
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp
