# Food Orders Batch-Based ELT Pipeline

## 1. Project Overview

This project implements a batch-based ELT (Extract, Load, Transform) pipeline using Python, Pandas, and MySQL.

The pipeline processes food order data from a CSV file, loads the original records into a MySQL raw database, retrieves the records in batches, transforms and validates the data using Pandas, and stores the cleaned records in a separate analytics database.

## 2. Objectives

- Extract food order records from a CSV file in batches of 100.
- Load original records into a MySQL raw database.
- Retrieve raw records from MySQL in batches.
- Transform data using Pandas.
- Identify duplicate and invalid records.
- Handle missing values using business rules.
- Calculate delivery duration and platform net revenue.
- Validate transformed records.
- Store valid records in a separate analytics database.
- Perform SQL-based business analysis.

## 3. Technologies Used

- Python
- Pandas
- NumPy
- MySQL
- MySQL Connector
- VS Code

## 4. Project Architecture

CSV Dataset → Extract → Raw MySQL Database → Retrieve → Transform → Validate → Analytics MySQL Database → SQL Business Analysis

## 5. Database Details

### Raw Database

Database: `food_orders_raw_db`

Table: `raw_food_orders`

Purpose: Stores the original food order records without applying cleaning or transformation.

### Analytics Database

Database: `food_orders_analytics_db`

Table: `cleaned_food_orders`

Purpose: Stores validated and transformed records for analysis.

## 6. Project Structure

```text
Food_Order_ELT_Pipeline/
│
├── food_orders.csv
├── config.py
├── extract.py
├── load_raw.py
├── retrieve_raw.py
├── transform.py
├── validate.py
├── load_transformed.py
├── elt_batch_pipeline.py
│
├── business_analysis.sql
├── database_verification.sql
├── requirements.txt
├── README.md
│
└── reports/
    ├── validation_report.csv
    └── rejected_records.csv
```

## 7. Batch Processing

The pipeline uses a batch size of 100 records.

The original dataset contains 1,010 records, which are processed in 11 batches:

- Batches 1–10: 100 records each.
- Batch 11: 10 records.

## 8. Data Transformation

The pipeline performs the following transformations:

- Removes duplicate records.
- Handles missing payment methods and discount information.
- Converts timestamp columns into datetime format.
- Converts financial columns into numeric values.
- Calculates delivery time in minutes.
- Calculates platform net revenue.

### Platform Net Revenue Formula

Platform Net Revenue = Commission Fee + Delivery Fee - Payment Processing Fee - Refunds/Chargebacks

## 9. Data Validation

The validation process checks:

- Missing Order IDs.
- Duplicate records and Order IDs.
- Missing or invalid timestamps.
- Negative delivery duration.
- Incorrect delivery duration.
- Incorrect platform net revenue.

Invalid records are stored separately with rejection reasons.

Validation outputs are saved in the `reports` folder.

## 10. Business Analysis

SQL queries are used to calculate:

1. Total order value.
2. Average order value.
3. Most common payment method.
4. Most common order channel.
5. Average delivery time.
6. Total platform net revenue.

## 11. Installation

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Configure the MySQL credentials in `config.py` before running the pipeline.

## 12. Execution

Run the pipeline using:

```bash
python elt_batch_pipeline.py
```

## 13. Output

The pipeline produces:

- Original records in the raw database.
- Validated records in the analytics database.
- Validation report.
- Rejected records with reasons.
- Final pipeline execution summary.

## 14. Conclusion

This project demonstrates a batch-based ELT workflow using Python, Pandas, and MySQL. It separates raw data storage from analytics data storage and applies transformation and validation before making records available for business analysis.
