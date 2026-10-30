
import pandas as pd

# Dataset path
CSV_FILE_PATH = "food_orders.csv"

# Batch size
BATCH_SIZE = 100


def extract_batches():

    print("Starting batch extraction...\n")

    total_records = 0
    total_batches = 0

    # Read CSV in batches of 100 rows
    for batch_number, batch_df in enumerate(
        pd.read_csv(CSV_FILE_PATH, chunksize=BATCH_SIZE),
        start=1
    ):

        total_batches += 1
        batch_records = len(batch_df)
        total_records += batch_records

        print(f"Batch Number: {batch_number}")
        print(f"Records Extracted: {batch_records}")
        print("-" * 40)

        # Yield original batch without cleaning or transformation
        yield batch_number, batch_df

    print("\nExtraction Completed!")
    print("Total Batches:", total_batches)
    print("Total Records Extracted:", total_records)


if __name__ == "__main__":

    for batch_number, batch_df in extract_batches():
        pass
