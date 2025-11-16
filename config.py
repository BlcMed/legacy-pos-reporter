"""
Configuration settings for the restaurant report system.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backup paths
# BACKUP_BASE_PATH = "D:/backups/"
BACKUP_BASE_PATH = "./backups/"
MDB_FILENAME = "resturant.mdb"

# Email configuration
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Restaurant info
RESTAURANT_NAME = os.getenv("RESTAURANT_NAME", "TORNADO RESTAURANT")

# Report settings
REPORT_TITLE = "Monthly Sales Report"
TOP_ITEMS_COUNT = 10

# Date format in MDB
MDB_DATE_FORMAT = "%m/%d/%y %H:%M:%S"
