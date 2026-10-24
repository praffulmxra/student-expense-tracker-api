from db import get_connection

connection = None

try:
    connection = get_connection()
    print("Database connected successfully!")
    print("Connection closed:", connection.closed)

except Exception as error:
    print("Database connection failed:")
    print(error)

finally:
    if connection is not None:
        connection.close()
