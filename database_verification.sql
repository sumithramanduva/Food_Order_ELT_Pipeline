CREATE DATABASE IF NOT EXISTS food_orders_raw_db;

USE food_orders_raw_db;

SHOW DATABASES;

# verifying the records

USE food_orders_raw_db;

SELECT COUNT(*) AS total_records
FROM raw_food_orders;
SELECT * 
FROM raw_food_orders
LIMIT 5;

CREATE DATABASE IF NOT EXISTS food_orders_analytics_db;
USE food_orders_analytics_db;
SHOW DATABASES;

USE food_orders_raw_db;
SELECT COUNT(*) AS total_raw_records
FROM raw_food_orders;

SELECT * FROM raw_food_orders LIMIT 5;

SELECT COUNT(*) AS total_raw_records
FROM food_orders_raw_db.raw_food_orders;

USE food_orders_analytics_db;
SHOW TABLES;
SELECT COUNT(*) AS total_cleaned_records
FROM cleaned_food_orders;

SELECT *
FROM cleaned_food_orders
LIMIT 5;

USE food_orders_analytics_db;

SHOW TABLES;

SELECT COUNT(*) AS total_cleaned_records
FROM cleaned_food_orders;

SELECT *
FROM cleaned_food_orders
LIMIT 5;