"""Chat endpoints — standard and streaming HR assistant responses."""

import json
import logging
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


def _build_employee_context(employee_id: Optional[int], db: Session) -> Optional[str]:
    if not employee_id:
        return None
    emp = db.get(Employee, employee_id)
    if emp is None:
        return None
    return (
        f"Employee: {emp.full_name} | "
        f"Number: {emp.employee_number} | "
        f"Position: {emp.position} | "
        f"Department: {emp.department.name if emp.department else 'Unknown'} | "
        f"Status: {emp.status.value} | "
        f"Hire Date: {emp.hire_date}"
    )


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    employee_context = _build_employee_context(payload.employee_id, db)
    try:
        ai_service = get_ai_service()
        response_text = ai_service.generate_response(
            question=payload.message,
            employee_context=employee_context,
            conversation_history=payload.conversation_history,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(exc)}")
    return {"response": response_text}


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest, db: Session = Depends(get_db)):
    employee_context = _build_employee_context(payload.employee_id, db)
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
