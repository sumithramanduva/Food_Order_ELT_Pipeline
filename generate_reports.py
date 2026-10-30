
import pandas as pd

from retrieve_raw import retrieve_raw_batches
from transform import transform_batch
from validate import validate_data


def generate_reports():

    seen_records = set()
    seen_order_ids = set()

    transformed_batches = []
    rejected_batches = []

    total_retrieved = 0

    print("\nGENERATING VALIDATION REPORTS")
    print("-" * 40)

    for batch_number, batch_df in retrieve_raw_batches():

        total_retrieved += len(batch_df)

        valid_df, rejected_df = transform_batch(
            batch_df,
            seen_records,
            seen_order_ids
        )

        transformed_batches.append(valid_df)

        if not rejected_df.empty:
            rejected_batches.append(rejected_df)

        print(
            f"Batch {batch_number}: "
            f"{len(valid_df)} accepted, "
            f"{len(rejected_df)} rejected"
        )

    combined_df = pd.concat(
        transformed_batches,
        ignore_index=True
    )

    if rejected_batches:
        combined_rejected_df = pd.concat(
            rejected_batches,
            ignore_index=True
        )
    else:
        combined_rejected_df = pd.DataFrame()

    validated_df, final_rejected_df = validate_data(
        combined_df,
        combined_rejected_df
    )

    print("\nFINAL REPORT")
    print("-" * 40)
    print("Raw Records Retrieved:", total_retrieved)
    print("Accepted Records:", len(validated_df))
    print("Rejected Records:", len(final_rejected_df))
    print("Reports generated successfully!")


if __name__ == "__main__":
    generate_reports()
