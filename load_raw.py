
import pandas as pd
import mysql.connector

from config import (
    CSV_FILE_PATH,
    BATCH_SIZE,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    RAW_DATABASE,
    RAW_TABLE
)


def load_raw_data():

    connection = None
    cursor = None

    try:
        # Read original CSV without cleaning
        df = pd.read_csv(CSV_FILE_PATH)

        print("Total records in CSV:", len(df))

        # Connect to raw database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=RAW_DATABASE
        )

        cursor = connection.cursor()

        # Create table columns dynamically.
        # All original columns are stored as LONGTEXT
        # to preserve their original textual values.
        columns = ", ".join(
            f"`{column}` LONGTEXT"
            for column in df.columns
        )

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{RAW_TABLE}` (
            `raw_record_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
            {columns}
        )
        """

        cursor.execute(create_table_query)

        # Insert query
        column_names = ", ".join(
            f"`{column}`" for column in df.columns
        )

        placeholders = ", ".join(
            ["%s"] * len(df.columns)
        )

        insert_query = f"""
        INSERT INTO `{RAW_TABLE}` ({column_names})
        VALUES ({placeholders})
        """

        total_loaded = 0
        successful_batches = 0
        failed_batches = 0

        # Load records in batches
        for batch_number, start in enumerate(
            range(0, len(df), BATCH_SIZE),
            start=1
        ):

            batch_df = df.iloc[start:start + BATCH_SIZE]

            # Convert missing values to SQL NULL
            batch_df = batch_df.astype(object).where(
                pd.notna(batch_df), None
            )

            records = [
                tuple(row)
                for row in batch_df.itertuples(
                    index=False, name=None
                )
            ]

            try:
                cursor.executemany(insert_query, records)
                connection.commit()

                total_loaded += len(records)
                successful_batches += 1

                print(
                    f"Batch {batch_number}: "
                    f"{len(records)} records loaded successfully"
                )

            except mysql.connector.Error as error:
                connection.rollback()
                failed_batches += 1

                print(
                    f"Batch {batch_number} failed: {error}"
                )

        # Verify raw table record count
        cursor.execute(
            f"SELECT COUNT(*) FROM `{RAW_TABLE}`"
        )

        database_count = cursor.fetchone()[0]

        print("\nRAW DATA LOAD SUMMARY")
        print("-------------------------")
        print("CSV Records:", len(df))
        print("Records Loaded This Run:", total_loaded)
        print("Records in Raw Database:", database_count)
        print("Successful Batches:", successful_batches)
        print("Failed Batches:", failed_batches)

    except Exception as error:
        if connection and connection.is_connected():
            connection.rollback()

        print("Raw data loading failed:", error)

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    load_raw_data()
