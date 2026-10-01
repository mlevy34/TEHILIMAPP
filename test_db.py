import pyodbc

connection = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\MSSQLSERVER01;"
    "DATABASE=Tehilim Together;"
    "Trusted_Connection=yes;"
)

print("Connected successfully!")

cursor = connection.cursor()

cursor.execute("SELECT DB_NAME()")
print("Database:", cursor.fetchone()[0])

cursor.execute("""
    SELECT TABLE_SCHEMA, TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    ORDER BY TABLE_NAME
""")

for row in cursor.fetchall():
    print(row)

connection.close()