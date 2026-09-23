import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.meta_db import QueryHistoryModel, get_db_session
from app.services.sql_generator import generate_sql
from app.services.sql_validator import validate_sql
from app.services.execution_engine import run_select
from app.services.session_store import get_session

logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    session_id: str = Field(..., description="ID of the active database session")
    text: str = Field(..., description="Natural language user question")
    language: str = Field("en", description="Language code, default 'en'")


class QueryResponse(BaseModel):
    query_id: Union[str, int]
    sql: str
    explanation: str
    confidence: float
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    query_type: str = "select"
    result: List[Any]
    chart_type: str = "none"


class HistoryConversation(BaseModel):
    id: str
    nl_query: str
    timestamp: str


class HistoryResponse(BaseModel):
    conversations: List[HistoryConversation]


@router.get("/history", response_model=HistoryResponse)
def get_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db_session),
):
    """Retrieve query history from data/meta.db filtered by session_id, most recent first, limit to 20."""
    query = db.query(QueryHistoryModel)
    if session_id:
        query = query.filter(QueryHistoryModel.session_id == session_id)

    records = query.order_by(QueryHistoryModel.created_at.desc()).limit(20).all()

    conversations = [
        HistoryConversation(
            id=str(record.id),
            nl_query=record.nl_query,
            timestamp=record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else "",
        )
        for record in records
    ]
    return HistoryResponse(conversations=conversations)


@router.post("/query", response_model=QueryResponse)
def handle_query(
    payload: QueryRequest,
    db: Session = Depends(get_db_session),
):
    """Translate natural language to SQL, validate it, execute it, and record history."""
    session = get_session(payload.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{payload.session_id}' not found. Please connect to a database first.",
        )

    # 1. Generate SQL using Gemini
    try:
        gen_data = generate_sql(payload.session_id, payload.text)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "Error generating SQL for session '%s' and question '%s': %s",
            payload.session_id,
            payload.text,
            exc,
            exc_info=True,
        )
        err_msg = str(exc)
        if "429" in err_msg or "quota" in err_msg.lower() or "toomanyrequests" in type(exc).__name__.lower():
            raise HTTPException(
                status_code=429,
                detail=f"Gemini API rate limit or quota exceeded: {err_msg}",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SQL: {err_msg}",
        )

    sql = gen_data.get("sql", "")
    explanation = gen_data.get("explanation", "")
    confidence = float(gen_data.get("confidence", 0.9))

    # 2. Validate SQL before execution
    validation = validate_sql(sql)
    if not validation.get("valid", False):
        friendly_message = validation.get("message", "Invalid SQL query.")
        query_record = QueryHistoryModel(
            session_id=payload.session_id,
            nl_query=payload.text,
            generated_sql=sql,
            confidence=0.0,
            query_type="select",
            created_at=datetime.utcnow(),
        )
        db.add(query_record)
        db.commit()
        db.refresh(query_record)

        return QueryResponse(
            query_id=str(query_record.id),
            sql=sql,
            explanation=friendly_message,
            confidence=0.0,
            needs_clarification=False,
            clarification_question=None,
            query_type="select",
            result=[],
            chart_type="none",
        )

    # 3. Execute SQL
    exec_result = run_select(payload.session_id, sql)
    if isinstance(exec_result, dict) and "error" in exec_result:
        friendly_message = f"Database query execution failed: {exec_result['error']}"
        query_record = QueryHistoryModel(
            session_id=payload.session_id,
            nl_query=payload.text,
            generated_sql=sql,
            confidence=0.0,
            query_type="select",
            created_at=datetime.utcnow(),
        )
        db.add(query_record)
        db.commit()
        db.refresh(query_record)

        return QueryResponse(
            query_id=str(query_record.id),
            sql=sql,
            explanation=friendly_message,
            confidence=0.0,
            needs_clarification=False,
            clarification_question=None,
            query_type="select",
            result=[],
            chart_type="none",
        )

    # 4. Save successful query to query_history in meta_db
    query_record = QueryHistoryModel(
        session_id=payload.session_id,
        nl_query=payload.text,
        generated_sql=sql,
        confidence=confidence,
        query_type="select",
        created_at=datetime.utcnow(),
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    return QueryResponse(
        query_id=str(query_record.id),
        sql=sql,
        explanation=explanation,
        confidence=confidence,
        needs_clarification=False,
        clarification_question=None,
        query_type="select",
        result=exec_result,
        chart_type="none",
    )
