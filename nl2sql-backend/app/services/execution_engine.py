import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Union
from app.services.session_store import get_session


def run_select(session_id: str, sql: str) -> Union[List[Dict[str, Any]], Dict[str, str]]:
    """Execute a SQL query against the session's SQLite database.
    
    Returns:
        List of dicts representing row data, or a dict with an 'error' key on failure.
    """
    session = get_session(session_id)
    if not session:
        return {"error": f"Session '{session_id}' not found. Please connect first."}

    db_path = session.get("db_path")
    if not db_path or not Path(db_path).exists():
        return {"error": f"Database file not found at '{db_path}'."}

    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

