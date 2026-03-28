"""Model package — import all models to ensure they are registered with SQLAlchemy."""

from app.models.employee import (  # noqa: F401
    Department,
    Employee,
    Benefit,
    LeaveRequest,
    ExpenseClaim,
    OnboardingTask,
)
