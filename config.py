
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE_PATH = BASE_DIR / "food_orders.csv"
BATCH_SIZE = 100

# MySQL Configuration
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
# Raw Database
RAW_DATABASE = "food_orders_raw_db"
RAW_TABLE = "raw_food_orders"

# Analytics Database
ANALYTICS_DATABASE = "food_orders_analytics_db"
ANALYTICS_TABLE = "cleaned_food_orders"

# Reports Directory
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

print("Configuration loaded successfully!")
print("Dataset path:", CSV_FILE_PATH)
print("Batch size:", BATCH_SIZE)
print("Raw database:", RAW_DATABASE)
print("Analytics database:", ANALYTICS_DATABASE)
