from typing import Dict, Any
import sqlglot
from sqlglot import exp


def validate_sql(sql_string: str) -> Dict[str, Any]:
    """Validate that the SQL string has valid syntax and is exclusively a read (SELECT) query.

    Returns:
        dict:
            - {"valid": True} if valid SELECT query.
            - {"valid": False, "reason": "syntax_error", "message": "The generated SQL had invalid syntax."}
            - {"valid": False, "reason": "write_not_supported", "message": "This version only supports read (SELECT) queries."}
    """
    if not sql_string or not isinstance(sql_string, str) or not sql_string.strip():
        return {
            "valid": False,
            "reason": "syntax_error",
            "message": "The generated SQL had invalid syntax.",
        }

    try:
        parsed_statements = sqlglot.parse(sql_string.strip(), read="sqlite")
        statements = [stmt for stmt in parsed_statements if stmt is not None]
        if not statements:
            return {
                "valid": False,
                "reason": "syntax_error",
                "message": "The generated SQL had invalid syntax.",
            }
    except Exception:
        return {
            "valid": False,
            "reason": "syntax_error",
            "message": "The generated SQL had invalid syntax.",
        }

    # Check that each statement is a SELECT query and that there is exactly one statement
    for stmt in statements:
        if not isinstance(stmt, (exp.Select, exp.Query)):
            return {
                "valid": False,
                "reason": "write_not_supported",
                "message": "This version only supports read (SELECT) queries.",
            }

    if len(statements) != 1:
        return {
            "valid": False,
            "reason": "write_not_supported",
            "message": "This version only supports read (SELECT) queries.",
        }

    return {"valid": True}
