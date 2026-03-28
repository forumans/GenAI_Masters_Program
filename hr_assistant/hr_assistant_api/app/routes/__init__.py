"""Router registration — attaches all routers to the application."""

from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    from app.routes.health import router as health_router
    from app.routes.employees import router as employees_router
    from app.routes.chat import router as chat_router

    app.include_router(health_router)
    app.include_router(employees_router)
    app.include_router(chat_router)
