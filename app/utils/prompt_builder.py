def buildPrompt(userPrompt: str, schema: dict) -> str:
    return f"""
You are an SQL generator. Given the following schema:

Table: {schema['table']}
Columns:{', '.join(schema['columns'])}

Generate a MySQL query (no INSERT, UPDATE, DELETE) that fulfills: "{userPrompt}"

Only retrun SQL, no explanation.
"""

def cleanSQL(rawSQL: str) -> str:
    # Remove ```sql and ``` wrappers
    if rawSQL.startswith("```"):
        rawSQL = rawSQL.strip("`")  # removes backticks
        rawSQL = rawSQL.replace("sql", "", 1).strip()

    # Replace newlines with space
    cleaned_sql = " ".join(rawSQL.split())

    return cleaned_sql