
import mysql.connector

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    RAW_DATABASE
)

print("Checking MySQL configuration...")
print("Host:", MYSQL_HOST)
print("User:", MYSQL_USER)
print("Password loaded:", bool(MYSQL_PASSWORD))

if not MYSQL_PASSWORD:
    print("ERROR: MySQL password is missing.")
else:
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=RAW_DATABASE
        )

        if connection.is_connected():
            print("\nMySQL connection successful!")
            print("Connected Database:", RAW_DATABASE)

        connection.close()

    except mysql.connector.Error as error:
        print("\nMySQL connection failed!")
        print("Error:", error)
