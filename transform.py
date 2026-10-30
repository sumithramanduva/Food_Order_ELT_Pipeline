
import pandas as pd
import numpy as np


# Financial columns
FINANCIAL_COLUMNS = [
    "Order Value",
    "Delivery Fee",
    "Commission Fee",
    "Payment Processing Fee",
    "Refunds/Chargebacks"
]

# Timestamp columns
TIMESTAMP_COLUMNS = [
    "Order Date and Time",
    "Delivery Date and Time"
]


def transform_batch(batch_df, seen_records, seen_order_ids):

    # Keep the original retrieved batch unchanged
    df = batch_df.copy()

    valid_records = []
    rejected_records = []

    # Process records one by one
    for _, row in df.iterrows():

        record = row.to_dict()

        # Create a fingerprint using the original values
        fingerprint = tuple(
            None if pd.isna(value) else str(value)
            for value in row.tolist()
        )

        # Check exact duplicates across all batches
        if fingerprint in seen_records:
            record["Rejection_Reason"] = "Duplicate Record"
            rejected_records.append(record)
            continue

        seen_records.add(fingerprint)

        # Check missing Order ID
        order_id = record.get("Order ID")

        if pd.isna(order_id) or str(order_id).strip() == "":
            record["Rejection_Reason"] = "Missing Order ID"
            rejected_records.append(record)
            continue

        # Check repeated Order ID across batches
        if str(order_id) in seen_order_ids:
            record["Rejection_Reason"] = "Duplicate Order ID"
            rejected_records.append(record)
            continue

        # Convert timestamps
        for column in TIMESTAMP_COLUMNS:
            if column not in df.columns:
                raise ValueError(f"Missing required column: {column}")

            record[column] = pd.to_datetime(
                record[column],
                errors="coerce"
            )

        # Reject invalid or missing timestamps
        if (
            pd.isna(record["Order Date and Time"])
            or pd.isna(record["Delivery Date and Time"])
        ):
            record["Rejection_Reason"] = "Invalid or Missing Timestamp"
            rejected_records.append(record)
            continue

        # Calculate delivery duration
        delivery_minutes = (
            record["Delivery Date and Time"]
            - record["Order Date and Time"]
        ).total_seconds() / 60

        # Reject negative delivery duration
        if delivery_minutes < 0:
            record["Delivery_Time_Minutes"] = delivery_minutes
            record["Rejection_Reason"] = "Negative Delivery Duration"
            rejected_records.append(record)
            continue

        record["Delivery_Time_Minutes"] = delivery_minutes

        # Convert financial columns into numeric values
        for column in FINANCIAL_COLUMNS:
            if column in record:
                record[column] = pd.to_numeric(
                    record[column],
                    errors="coerce"
                )

        # Handle categorical missing values
        if pd.isna(record.get("Payment Method")):
            record["Payment Method"] = "Unknown"

        if pd.isna(record.get("Discounts and Offers")):
            record["Discounts and Offers"] = "Not Specified"

        # Calculate platform net revenue
        revenue_columns = [
            "Commission Fee",
            "Delivery Fee",
            "Payment Processing Fee",
            "Refunds/Chargebacks"
        ]

        if all(
            pd.notna(record[column])
            for column in revenue_columns
        ):
            record["Platform_Net_Revenue"] = (
                record["Commission Fee"]
                + record["Delivery Fee"]
                - record["Payment Processing Fee"]
                - record["Refunds/Chargebacks"]
            )
        else:
            record["Platform_Net_Revenue"] = np.nan

        # Mark accepted Order ID
        seen_order_ids.add(str(order_id))

        valid_records.append(record)

    valid_df = pd.DataFrame(valid_records)
    rejected_df = pd.DataFrame(rejected_records)

    return valid_df, rejected_df


if __name__ == "__main__":

    print("Transformation module loaded successfully!")
    print("Financial columns:", FINANCIAL_COLUMNS)
    print("Timestamp columns:", TIMESTAMP_COLUMNS)
