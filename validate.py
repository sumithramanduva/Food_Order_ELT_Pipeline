
import pandas as pd

from config import REPORTS_DIR


FINANCIAL_COLUMNS = [
    "Commission Fee",
    "Delivery Fee",
    "Payment Processing Fee",
    "Refunds/Chargebacks"
]

TIMESTAMP_COLUMNS = [
    "Order Date and Time",
    "Delivery Date and Time"
]


def validate_data(transformed_df, rejected_df):

    accepted_records = []
    validation_rejections = []

    seen_order_ids = set()
    seen_records = set()

    # Include records rejected during transformation
    checked_count = len(transformed_df) + len(rejected_df)

    duplicate_order_count = 0
    duplicate_record_count = 0
    invalid_duration_count = 0
    invalid_revenue_count = 0

    source_columns = [
        column for column in transformed_df.columns
        if column not in [
            "Delivery_Time_Minutes",
            "Platform_Net_Revenue"
        ]
    ]

    for _, row in transformed_df.iterrows():

        record = row.to_dict()
        reasons = []

        # 1. Check Order ID
        order_id = record.get("Order ID")

        if pd.isna(order_id) or str(order_id).strip() == "":
            reasons.append("Missing Order ID")

        elif str(order_id) in seen_order_ids:
            reasons.append("Duplicate Order ID")
            duplicate_order_count += 1

        else:
            seen_order_ids.add(str(order_id))

        # 2. Check timestamps
        order_time = record.get("Order Date and Time")
        delivery_time = record.get("Delivery Date and Time")

        if pd.isna(order_time) or pd.isna(delivery_time):

            reasons.append("Missing or Invalid Timestamp")
            invalid_duration_count += 1

        else:
            calculated_minutes = (
                delivery_time - order_time
            ).total_seconds() / 60

            stored_minutes = record.get(
                "Delivery_Time_Minutes"
            )

            if calculated_minutes < 0:
                reasons.append("Negative Delivery Duration")
                invalid_duration_count += 1

            elif (
                pd.isna(stored_minutes)
                or abs(calculated_minutes - stored_minutes) > 0.01
            ):
                reasons.append("Incorrect Delivery Duration")
                invalid_duration_count += 1

        # 3. Check financial values and revenue
        financial_values = [
            record.get(column)
            for column in FINANCIAL_COLUMNS
        ]

        revenue = record.get("Platform_Net_Revenue")

        if all(pd.notna(value) for value in financial_values):

            expected_revenue = (
                record["Commission Fee"]
                + record["Delivery Fee"]
                - record["Payment Processing Fee"]
                - record["Refunds/Chargebacks"]
            )

            if (
                pd.isna(revenue)
                or abs(expected_revenue - revenue) > 0.01
            ):
                reasons.append("Incorrect Platform Net Revenue")
                invalid_revenue_count += 1

        elif pd.notna(revenue):
            reasons.append(
                "Revenue Present Despite Missing Components"
            )
            invalid_revenue_count += 1

        # 4. Check exact duplicate records
        fingerprint = tuple(
            str(record.get(column))
            for column in source_columns
        )

        if fingerprint in seen_records:
            reasons.append("Duplicate Record")
            duplicate_record_count += 1

        else:
            seen_records.add(fingerprint)

        # 5. Separate accepted and rejected records
        if reasons:

            record["Rejection_Reason"] = "; ".join(reasons)
            validation_rejections.append(record)

        else:
            accepted_records.append(record)

    # Create accepted DataFrame
    accepted_df = pd.DataFrame(
        accepted_records,
        columns=transformed_df.columns
    )

    # Combine transformation and validation rejections
    new_rejected_df = pd.DataFrame(validation_rejections)

    if not rejected_df.empty and not new_rejected_df.empty:

        final_rejected_df = pd.concat(
            [rejected_df, new_rejected_df],
            ignore_index=True
        )

    elif not rejected_df.empty:

        final_rejected_df = rejected_df.copy()

    else:

        final_rejected_df = new_rejected_df

    # Create validation report
    report_rows = [
        {
            "Validation Check": "Total records checked",
            "Status": "INFO",
            "Count": checked_count
        },
        {
            "Validation Check": "Accepted records",
            "Status": "PASS",
            "Count": len(accepted_df)
        },
        {
            "Validation Check": "Rejected records",
            "Status": "INFO",
            "Count": len(final_rejected_df)
        },
        {
            "Validation Check": "Duplicate Order IDs found",
            "Status": "INFO",
            "Count": duplicate_order_count
        },
        {
            "Validation Check": "Duplicate records found during validation",
            "Status": "INFO",
            "Count": duplicate_record_count
        },
        {
            "Validation Check": "Invalid delivery durations",
            "Status": "PASS" if invalid_duration_count == 0 else "FAIL",
            "Count": invalid_duration_count
        },
        {
            "Validation Check": "Invalid platform net revenue",
            "Status": "PASS" if invalid_revenue_count == 0 else "FAIL",
            "Count": invalid_revenue_count
        },
        {
            "Validation Check": "Missing Order IDs in accepted data",
            "Status": (
                "PASS"
                if accepted_df["Order ID"].notna().all()
                else "FAIL"
            ),
            "Count": accepted_df["Order ID"].isna().sum()
        }
    ]

    # Check timestamp completeness in accepted records
    for column in TIMESTAMP_COLUMNS:

        invalid_count = accepted_df[column].isna().sum()

        report_rows.append({
            "Validation Check": f"Missing {column}",
            "Status": "PASS" if invalid_count == 0 else "FAIL",
            "Count": invalid_count
        })

    report_df = pd.DataFrame(report_rows)

    # Save reports
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_df.to_csv(
        REPORTS_DIR / "validation_report.csv",
        index=False
    )

    final_rejected_df.to_csv(
        REPORTS_DIR / "rejected_records.csv",
        index=False
    )

    # Display summary
    print("\n" + "=" * 45)
    print("VALIDATION SUMMARY")
    print("=" * 45)

    print("Total Records Checked:", checked_count)
    print("Accepted Records:", len(accepted_df))
    print("Rejected Records:", len(final_rejected_df))
    print("Duplicate Order IDs Found:", duplicate_order_count)
    print("Duplicate Records Found:", duplicate_record_count)

    print("\nReports generated:")
    print(REPORTS_DIR / "validation_report.csv")
    print(REPORTS_DIR / "rejected_records.csv")

    return accepted_df, final_rejected_df


if __name__ == "__main__":
    print("Validation module loaded successfully!")
