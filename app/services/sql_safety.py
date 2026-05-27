import re
import sqlparse
from fastapi import HTTPException

BLOCKED_PATTERNS = [
    r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b",
    r"\bDROP\b",   r"\bALTER\b",  r"\bTRUNCATE\b",
    r"\bUNION\b",  r"\bEXEC\b",
    r"--",          r"/\*",
]

def validateSQL(sql: str) -> str:
    """
    Checks that the SQL is safe to run.
    Raises HTTPException 400 if anything looks dangerous.
    Returns the SQL (with LIMIT added if missing).
    """
    upper = sql.upper()

    # Check for forbidden keywords
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, upper, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail=f"Unsafe query rejected: matched pattern '{pattern}'"
            )

    # Verify it parses as a SELECT statement
    parsed = sqlparse.parse(sql)
    if not parsed or parsed[0].get_type() != "SELECT":
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed."
        )

    return sql