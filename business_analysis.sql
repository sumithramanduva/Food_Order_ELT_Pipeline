
USE food_orders_analytics_db;

-- ==========================================
-- FOOD ORDERS BUSINESS ANALYSIS
-- ==========================================


-- 1. Total Order Value
SELECT
    ROUND(SUM(`Order Value`), 2) AS Total_Order_Value
FROM cleaned_food_orders;


-- 2. Average Order Value
SELECT
    ROUND(AVG(`Order Value`), 2) AS Average_Order_Value
FROM cleaned_food_orders;


-- 3. Most Common Payment Method
SELECT
    `Payment Method`,
    COUNT(*) AS Total_Orders
FROM cleaned_food_orders
GROUP BY `Payment Method`
ORDER BY Total_Orders DESC;


-- 4. Most Common Order Channel
SELECT
    `Order Channel`,
    COUNT(*) AS Total_Orders
FROM cleaned_food_orders
GROUP BY `Order Channel`
ORDER BY Total_Orders DESC;


-- 5. Average Delivery Time in Minutes
SELECT
    ROUND(AVG(`Delivery_Time_Minutes`), 2)
    AS Average_Delivery_Time_Minutes
FROM cleaned_food_orders;


-- 6. Total Platform Net Revenue
SELECT
    ROUND(SUM(`Platform_Net_Revenue`), 2)
    AS Total_Platform_Net_Revenue
FROM cleaned_food_orders;
