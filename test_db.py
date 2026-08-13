from database import get_connection

connection = get_connection()

with connection.cursor() as cursor:
    cursor.execute("SELECT DATABASE() AS current_database")
    print(cursor.fetchone())

connection.close()