def buildPrompt(userPrompt: str, schema: dict) -> str:
    """
    Builds the LLM prompt with full dynamic schema.
    schema: { "table_name": ["col1", "col2"], ... }
    """
    schema_lines = []
    for table, columns in schema.items():
        schema_lines.append(f"Table: {table}")
        schema_lines.append(f"Columns: {', '.join(columns)}")
        schema_lines.append("")

    schema_text = "\n".join(schema_lines).strip()

    return f"""You are a MySQL query generator.

Database schema:
{schema_text}

Rules:
- Generate only SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or ALTER.
- Always add LIMIT 500 unless the user specifies a count.
- If user asks about overall count, then there is no need of LIMIT in the query.
- Return only the SQL query — no explanation, no markdown, no backticks.

User request: "{userPrompt}"
"""

def cleanSQL(rawSQL: str) -> str:
    """
    Strips markdown code fences and normalises whitespace.
    Handles: ```sql ... ```, ``` ... ```, and plain SQL.
    """
    import re
    sql = rawSQL.strip()
    # Remove ```sql or ``` fences
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql)
    # Collapse all whitespace/newlines into single spaces
    sql = " ".join(sql.split())
    return sql.strip()