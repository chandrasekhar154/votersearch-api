import os
import mysql.connector
from langchain_core.tools import tool

def getConnection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

@tool
def executeQuery(query: str):
    """
    Executes a MySQL Select Query and returns the results as a string. Use this method to run sql queries againest the voter database. 
    """
    
    try:
        conn = getConnection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not results:
            return "Query executed successfully but returned no results."

        return str(results)
    except Exception as e:
        # Return the error as a string
        return f"SQL Error: {str(e)}"

def fetchSchema() -> dict:
    """
    Reads table and column names directly from MySQL INFORMATION_SCHEMA.
    Returns a dict like: { "table_name": ["col1", "col2", ...], ... }
    No manual JSON file needed — works for any number of tables.
    """
    conn = getConnection()
    cursor = conn.cursor(dictionary=True)

    db_name = os.getenv("DB_NAME")
    
    # Read exclusion list from .env — split by comma, strip spaces
    excluded_raw = os.getenv("DB_EXCLUDED_TABLES", "")
    excluded_tables = [t.strip() for t in excluded_raw.split(",") if t.strip()]

    if excluded_tables:
        # Build a placeholder string like %s, %s, %s for each excluded table
        placeholders = ", ".join(["%s"] * len(excluded_tables))

        cursor.execute(f"""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME NOT IN ({placeholders})
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """, (db_name, *excluded_tables))
    else:
        # No exclusions — fetch everything
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """, (db_name,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    schema = {}
    for row in rows:
        table = row["TABLE_NAME"]
        column = row["COLUMN_NAME"]
        if table not in schema:
            schema[table] = []
        schema[table].append(column)

    return schema