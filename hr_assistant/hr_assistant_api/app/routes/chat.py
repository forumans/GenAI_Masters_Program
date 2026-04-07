"""Chat endpoints — standard and streaming HR assistant responses."""

import json
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import ChatRequest, ChatResponse
from app.services.hr_policy_service import get_ai_service

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


def _extract_employee_names(question: str) -> list[str]:
    """Extract potential employee names from the question."""
    names = []
    
    # Pattern 1: Two words starting with capital letters (e.g., "John Doe")
    pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'
    matches = re.findall(pattern, question)
    names.extend(matches)
    
    # Pattern 2: Single capitalized name (e.g., "Gopi")
    # Look for capitalized words that might be names
    # Exclude common words that start with capital but aren't names
    common_words = {'The', 'What', 'When', 'Where', 'Who', 'How', 'Why', 'Is', 'Are', 'Was', 'Were', 'Will', 'Can', 'Could', 'Should', 'Would', 'Do', 'Does', 'Did', 'Has', 'Have', 'Had'}
    words = re.findall(r'\b[A-Z][a-z]+\b', question)
    for word in words:
        if word not in common_words and len(word) > 2:  # Exclude short words like "It", "He", "She"
            names.append(word)
    
    # Also check for common titles
    if "Mr." in question or "Ms." in question or "Mrs." in question:
        title_pattern = r'(?:Mr|Ms|Mrs)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        title_matches = re.findall(title_pattern, question)
        names.extend(title_matches)
    
    return list(set(names))  # Remove duplicates


def _find_employee_by_name(name: str, db: Session) -> Optional[Employee]:
    """Find an employee by first and last name or single name."""
    parts = name.split()
    
    if len(parts) >= 2:
        # Two or more parts - treat as first name + last name(s)
        first_name = parts[0]
        last_name = " ".join(parts[1:])  # Handle multi-word last names
        
        # Try exact match first
        employee = db.query(Employee).filter(
            Employee.first_name.ilike(first_name),
            Employee.last_name.ilike(last_name)
        ).first()
        
        if employee:
            return employee
        
        # Try fuzzy match
        employee = db.query(Employee).filter(
            Employee.first_name.ilike(f"%{first_name}%"),
            Employee.last_name.ilike(f"%{last_name}%")
        ).first()
        
        return employee
    else:
        # Single name - could be first name or last name
        single_name = parts[0]
        
        # Try first name
        employee = db.query(Employee).filter(
            Employee.first_name.ilike(single_name)
        ).first()
        
        if employee:
            logger.info(f"Found employee by first name: {employee.full_name}, status: {employee.status}")
            return employee
        
        # Try last name
        employee = db.query(Employee).filter(
            Employee.last_name.ilike(single_name)
        ).first()
        
        if employee:
            logger.info(f"Found employee by last name: {employee.full_name}, status: {employee.status}")
            return employee
        
        # Try fuzzy match in both fields
        employee = db.query(Employee).filter(
            (Employee.first_name.ilike(f"%{single_name}%")) |
            (Employee.last_name.ilike(f"%{single_name}%"))
        ).first()
        
        if employee:
            logger.info(f"Found employee by fuzzy match: {employee.full_name}, status: {employee.status}")
        
        return employee
    
    return None


def _build_employee_context(employee_id: Optional[int], db: Session, question: str = None) -> Optional[str]:
    """Build employee context from ID or name extraction."""
    # First try by ID if provided
    if employee_id:
        emp = db.get(Employee, employee_id)
        if emp:
            return (
                f"Employee: {emp.full_name} | "
                f"Number: {emp.employee_number} | "
                f"Position: {emp.position} | "
                f"Department: {emp.department.name if emp.department else 'Unknown'} | "
                f"Status: {emp.status.value} | "
                f"Hire Date: {emp.hire_date.strftime('%m/%d/%Y')}"
            )
    
    # If no ID but we have a question, try to extract names
    if question:
        # Check if this is a request for multiple employees
        if any(keyword in question.lower() for keyword in ["employees", "all employees", "list of", "bring the details", "show all"]):
            names = _extract_employee_names(question)
            logger.info(f"Extracted names for multiple employee search: {names}")
            if names:
                # For each name, find all matching employees
                all_employees = []
                for name in names:
                    employees = _find_all_employees_by_name(name, db)
                    all_employees.extend(employees)
                
                if all_employees:
                    logger.info(f"Found {len(all_employees)} employees total")
                    # Build context with all employees
                    context_parts = []
                    for emp in all_employees:
                        # Calculate years of service
                        from datetime import date
                        today = date.today()
                        years_of_service = today.year - emp.hire_date.year - ((today.month, today.day) < (emp.hire_date.month, emp.hire_date.day))
                        
                        context_parts.append(
                            f"Employee: {emp.full_name} | "
                            f"Number: {emp.employee_number} | "
                            f"Position: {emp.position} | "
                            f"Department: {emp.department.name if emp.department else 'Unknown'} | "
                            f"Status: {emp.status.value} | "
                            f"Hire Date: {emp.hire_date.strftime('%m/%d/%Y')} | "
                            f"Years of Service: {years_of_service}"
                        )
                    
                    return "\n".join(context_parts)
        
        # Single employee request
        names = _extract_employee_names(question)
        logger.info(f"Extracted names for single employee search: {names}")
        for name in names:
            employee = _find_employee_by_name(name, db)
            if employee:
                logger.info(f"Building context for employee: {employee.full_name}")
                logger.info(f"Raw hire_date from database: {employee.hire_date} (type: {type(employee.hire_date)})")
                logger.info(f"hire_date year: {employee.hire_date.year}, month: {employee.hire_date.month}, day: {employee.hire_date.day}")
                # Calculate years of service
                from datetime import date
                today = date.today()
                years_of_service = today.year - employee.hire_date.year - ((today.month, today.day) < (employee.hire_date.month, employee.hire_date.day))
                
                # Format date consistently - database has 2021-07-01, so display as 07/01/2021
                formatted_date = employee.hire_date.strftime('%m/%d/%Y')
                logger.info(f"Formatted date: {formatted_date}")
                
                return (
                    f"Employee: {employee.full_name} | "
                    f"Number: {employee.employee_number} | "
                    f"Position: {employee.position} | "
                    f"Department: {employee.department.name if employee.department else 'Unknown'} | "
                    f"Status: {employee.status.value} | "
                    f"Hire Date: {formatted_date} | "
                    f"Years of Service: {years_of_service}"
                )
        logger.debug(f"No employee found for extracted names: {names}")
    
    return None


def _find_all_employees_by_name(name: str, db: Session) -> list[Employee]:
    """Find all employees by first name, last name, or single name."""
    employees = []
    parts = name.split()
    
    if len(parts) >= 2:
        # Two or more parts - treat as first name + last name(s)
        first_name = parts[0]
        last_name = " ".join(parts[1:])
        
        # Try exact match
        emps = db.query(Employee).filter(
            Employee.first_name.ilike(first_name),
            Employee.last_name.ilike(last_name)
        ).all()
        employees.extend(emps)
        
        # Try fuzzy match
        emps = db.query(Employee).filter(
            Employee.first_name.ilike(f"%{first_name}%"),
            Employee.last_name.ilike(f"%{last_name}%")
        ).all()
        employees.extend(emps)
    else:
        # Single name - could be first name or last name
        single_name = parts[0]
        
        # Try first name
        emps = db.query(Employee).filter(
            Employee.first_name.ilike(single_name)
        ).all()
        employees.extend(emps)
        
        # Try last name
        emps = db.query(Employee).filter(
            Employee.last_name.ilike(single_name)
        ).all()
        employees.extend(emps)
        
        # Try fuzzy match in both fields
        emps = db.query(Employee).filter(
            (Employee.first_name.ilike(f"%{single_name}%")) |
            (Employee.last_name.ilike(f"%{single_name}%"))
        ).all()
        employees.extend(emps)
    
    # Remove duplicates
    unique_employees = []
    seen_ids = set()
    for emp in employees:
        if emp.id not in seen_ids:
            unique_employees.append(emp)
            seen_ids.add(emp.id)
    
    return unique_employees


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    employee_context = _build_employee_context(payload.employee_id, db, payload.message)
    logger.debug(f"Employee context: {employee_context or 'No employee context provided'}")
    try:
        ai_service = get_ai_service()
        response_text = ai_service.generate_response(
            question=payload.message,
            employee_context=employee_context,
            conversation_history=payload.conversation_history,
            db=db
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(exc)}")
    return {"response": response_text}


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest, db: Session = Depends(get_db)):
    employee_context = _build_employee_context(payload.employee_id, db, payload.message)
    logger.debug(f"Employee context: {employee_context or 'No employee context provided'}")
    logger.info(f"Received chat request. History present: {bool(payload.conversation_history)}")
    if payload.conversation_history:
        logger.debug(f"History length: {len(payload.conversation_history)}")
    try:
        ai_service = get_ai_service()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI service init error: {str(exc)}")

    def generate():
        try:
            for token in ai_service.stream_response(
                question=payload.message,
                employee_context=employee_context,
                conversation_history=payload.conversation_history,
                db=db
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        finally:
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
