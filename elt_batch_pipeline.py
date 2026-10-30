
import pandas as pd
import mysql.connector

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    ANALYTICS_DATABASE,
    ANALYTICS_TABLE
)

from retrieve_raw import retrieve_raw_batches
from transform import transform_batch
from validate import validate_data
from load_transformed import load_transformed_data


def check_analytics_table():

    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=ANALYTICS_DATABASE
    )

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = %s
            """,
            (ANALYTICS_DATABASE, ANALYTICS_TABLE)
        )

        table_exists = cursor.fetchone()[0] > 0

        if table_exists:
            cursor.execute(
                f"SELECT COUNT(*) FROM `{ANALYTICS_TABLE}`"
            )

            existing_records = cursor.fetchone()[0]

            if existing_records > 0:
                print(
                    "Analytics table already contains records."
                )
                print(
                    "Stopping to avoid inserting duplicate data."
                )
                return False

        return True

    finally:
        cursor.close()
        connection.close()


def run_pipeline():

    print("=" * 55)
    print("FOOD ORDERS BATCH ELT PIPELINE")
    print("=" * 55)

    if not check_analytics_table():
        return

    # Initialize counters and duplicate tracking
    total_retrieved = 0
    total_transformed = 0

    successful_batches = 0
    failed_batches = 0

    seen_records = set()
    seen_order_ids = set()

    transformed_batches = []
    rejected_batches = []

    # STEP 1: Retrieve raw records and transform
    print("\nSTEP 1: RETRIEVING AND TRANSFORMING DATA")
    print("-" * 55)

    for batch_number, batch_df in retrieve_raw_batches():

        total_retrieved += len(batch_df)

        try:
            valid_df, rejected_df = transform_batch(
                batch_df,
                seen_records,
                seen_order_ids
            )

            transformed_batches.append(valid_df)

            if not rejected_df.empty:
                rejected_batches.append(rejected_df)

            total_transformed += len(valid_df)
            successful_batches += 1

            print(
                f"Batch {batch_number}: "
                f"{len(valid_df)} transformed, "
                f"{len(rejected_df)} rejected"
            )

        except Exception as error:

            failed_batches += 1

            print(
                f"Batch {batch_number} failed: {error}"
            )

    # STEP 2: Combine transformed batches
    print("\nSTEP 2: COMBINING TRANSFORMED DATA")
    print("-" * 55)

    if transformed_batches:
        combined_df = pd.concat(
            transformed_batches,
            ignore_index=True
        )
    else:
        print("No transformed records available.")
        return

    if rejected_batches:
        combined_rejected_df = pd.concat(
            rejected_batches,
            ignore_index=True
        )
    else:
        combined_rejected_df = pd.DataFrame()

    print("Transformed records:", len(combined_df))
    print("Transformation rejections:",
          len(combined_rejected_df))

    # STEP 3: Validate combined records
    print("\nSTEP 3: VALIDATING DATA")
    print("-" * 55)

    validated_df, final_rejected_df = validate_data(
        combined_df,
        combined_rejected_df
    )

    print("Accepted records:", len(validated_df))
    print("Rejected records:", len(final_rejected_df))

    # STEP 4: Load accepted records into analytics database
    print("\nSTEP 4: LOADING ANALYTICS DATA")
    print("-" * 55)

    load_successful_batches = 0
    load_failed_batches = 0

    if not validated_df.empty:

        (
            load_successful_batches,
            load_failed_batches
        ) = load_transformed_data(validated_df)

    else:
        print("No valid records available for loading.")

    # STEP 5: Final execution report
    print("\n" + "=" * 55)
    print("FINAL ELT PIPELINE EXECUTION REPORT")
    print("=" * 55)

    print("Raw Records Retrieved:", total_retrieved)
    print("Retrieval Batches:", (total_retrieved + 99) // 100)
    print("Transformed Records:", total_transformed)
    print("Validated Records:", len(validated_df))
    print("Rejected Records:", len(final_rejected_df))

    print("Transformation Successful Batches:",
          successful_batches)

    print("Transformation Failed Batches:",
          failed_batches)

    print("Analytics Successful Batches:",
          load_successful_batches)

    print("Analytics Failed Batches:",
          load_failed_batches)

    print(
        "Overall Status:",
        "SUCCESS"
        if (
            failed_batches == 0
            and load_failed_batches == 0
            and total_retrieved == 1010
        )
        else "CHECK REQUIRED"
    )

    print("=" * 55)

    print("\nGenerated reports:")
    print("- reports/validation_report.csv")
    print("- reports/rejected_records.csv")


if __name__ == "__main__":
    run_pipeline()
