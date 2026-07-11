"""AI assistant / natural-language query endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import nl_query

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])


@router.post("/query", response_model=schemas.AssistantResponse)
def query(payload: schemas.AssistantQuery, db: Session = Depends(get_db)):
    result = nl_query.answer_question(db, payload.question)
    return schemas.AssistantResponse(question=payload.question, **result)


@router.get("/examples")
def examples():
    return {
        "examples": [
            "How many seats are available on floor 3?",
            "Show me all employees in the Data Platform project",
            "Which new joiners don't have a seat?",
            "What is the seat utilization in Building A?",
            "List employees in the Engineering department",
            "How many employees are there in total?",
            "Where does John sit?",
        ]
    }
