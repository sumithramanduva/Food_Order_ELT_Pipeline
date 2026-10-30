
import mysql.connector
import pandas as pd

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    RAW_DATABASE,
    RAW_TABLE,
    BATCH_SIZE
)


def retrieve_raw_batches():

    connection = None
    cursor = None

    try:
        # Connect to raw database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=RAW_DATABASE
        )

        cursor = connection.cursor()

        # Retrieve original columns, excluding the internal row ID
        cursor.execute(
            f"SELECT * FROM `{RAW_TABLE}` ORDER BY raw_record_id"
        )

        column_names = [
            description[0]
            for description in cursor.description
        ]

        if "raw_record_id" in column_names:
            column_names.remove("raw_record_id")

        total_retrieved = 0
        total_batches = 0

        print("Starting raw data retrieval...\n")

        while True:

            # Retrieve 100 records at a time
            records = cursor.fetchmany(BATCH_SIZE)

            if not records:
                break

            total_batches += 1

            # Remove internal row ID from retrieved records
            batch_records = [
                tuple(row[1:]) for row in records
            ]

            # Convert retrieved records into DataFrame
            batch_df = pd.DataFrame(
                batch_records,
                columns=column_names
            )

            total_retrieved += len(batch_df)

            print(f"Batch Number: {total_batches}")
            print(f"Records Retrieved: {len(batch_df)}")
            print("-" * 40)

            # Return each batch as a DataFrame
            yield total_batches, batch_df

        print("\nRaw data retrieval completed!")
        print("Total Batches Retrieved:", total_batches)
        print("Total Records Retrieved:", total_retrieved)

    except mysql.connector.Error as error:
        print("Raw data retrieval failed:", error)
        raise

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":

    for batch_number, batch_df in retrieve_raw_batches():
        pass
