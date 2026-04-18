import os
import mysql.connector

def getConnection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

def executeQuery(query: str):
    conn = getConnection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results