
import pandas as pd
import mysql.connector

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    ANALYTICS_DATABASE,
    ANALYTICS_TABLE,
    BATCH_SIZE
)


def get_mysql_type(column):

    if column in ["Order ID", "Customer ID", "Restaurant ID",
                  "Payment Method", "Discounts and Offers",
                  "Weather Condition", "Order Channel"]:
        return "VARCHAR(255)"

    if column in ["Order Date and Time", "Delivery Date and Time"]:
        return "DATETIME"

    if column in ["Order Value", "Delivery Fee",
                  "Commission Fee", "Payment Processing Fee",
                  "Refunds/Chargebacks",
                  "Delivery_Time_Minutes",
                  "Platform_Net_Revenue"]:
        return "DECIMAL(15, 4)"

    return "TEXT"


def load_transformed_data(validated_df):

    if validated_df.empty:
        print("No validated records available to load.")
        return 0, 0

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=ANALYTICS_DATABASE
        )

        cursor = connection.cursor()

        # Create table columns dynamically
        column_definitions = []

        for column in validated_df.columns:

            mysql_type = get_mysql_type(column)

            column_definitions.append(
                f"`{column}` {mysql_type}"
            )

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{ANALYTICS_TABLE}` (
            `analytics_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
            {", ".join(column_definitions)}
        )
        """

        cursor.execute(create_table_query)

        # Prepare insertion query
        columns = ", ".join(
            f"`{column}`"
            for column in validated_df.columns
        )

        placeholders = ", ".join(
            ["%s"] * len(validated_df.columns)
        )

        insert_query = f"""
        INSERT INTO `{ANALYTICS_TABLE}` ({columns})
        VALUES ({placeholders})
        """

        total_loaded = 0
        successful_batches = 0
        failed_batches = 0

        # Insert data in batches of 100
        for batch_number, start in enumerate(
            range(0, len(validated_df), BATCH_SIZE),
            start=1
        ):

            batch_df = validated_df.iloc[
                start:start + BATCH_SIZE
            ].copy()

            # Convert pandas missing values to SQL NULL
            batch_df = batch_df.astype(object).where(
                pd.notna(batch_df), None
            )

            # Convert Pandas timestamps into Python datetimes
            for column in [
                "Order Date and Time",
                "Delivery Date and Time"
            ]:
                if column in batch_df.columns:
                    batch_df[column] = batch_df[column].apply(
                        lambda value: (
                            value.to_pydatetime()
                            if isinstance(value, pd.Timestamp)
                            else value
                        )
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

        # Verify database count
        cursor.execute(
            f"SELECT COUNT(*) FROM `{ANALYTICS_TABLE}`"
        )

        final_count = cursor.fetchone()[0]

        print("\nANALYTICS DATABASE LOAD SUMMARY")
        print("--------------------------------")
        print("Records Loaded This Run:", total_loaded)
        print("Records in Analytics Table:", final_count)
        print("Successful Batches:", successful_batches)
        print("Failed Batches:", failed_batches)

        return successful_batches, failed_batches

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print("Analytics loading failed:", error)
        raise

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":

    print("Transformed data loading module loaded successfully!")
