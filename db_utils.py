import os
import pandas as pd

def fetch_courses():
    try:
        import mysql.connector

        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST"),
            port=int(os.environ.get("MYSQL_PORT")),
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DATABASE")
        )
        cursor = conn.cursor(dictionary=True)

        sql_query = f"""
        SELECT 
            titolo, 
            descrizione, 
            requisiti,
            COALESCE(
            CASE 
                WHEN testocosto IS NULL OR 
                 LOWER(TRIM(testocosto)) IN ('0-richiedere', '0', 'richiedere', 'null', 'nan')
                THEN 'Contact the company for information about the cost.'
                ELSE testocosto
            END,
            'Contact the company for information about the cost.'
            ) AS testocosto,
            ore, 
            sede
        FROM {os.environ.get("TABLE")} 
        WHERE {os.environ.get("FILTER")}
        ORDER BY titolo
        """

        cursor.execute(sql_query)
        courses = cursor.fetchall()
        cursor.close()
        conn.close()

        df = pd.DataFrame(courses)
        return df
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return pd.DataFrame()
