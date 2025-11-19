"""
Configuration settings for the restaurant report system.
Reads all configurable values from `settings.ini`.
"""

import configparser
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), './settings.ini')

config = configparser.ConfigParser()
config.read(SETTINGS_FILE)

# Backup paths
BACKUP_BASE_PATH = "./backups"
MDB_FILENAME = "resturant.mdb"
MONTHLY_REPORTS_PATH = "./reports/monthly"
DAILY_REPORTS_PATH = "./reports/daily"

# Email configuration (from settings.ini)
EMAIL_FROM = config["EMAIL"].get("email_from", "example@gmail.com")
EMAIL_PASSWORD = config["EMAIL"].get("email_password", "")
EMAIL_TO = config["EMAIL"].get("email_to", "")
SMTP_SERVER = config["EMAIL"].get("smtp_server", "smtp.gmail.com")
SMTP_PORT = int(config["EMAIL"].get("smtp_port", "587"))

# Restaurant info
RESTAURANT_NAME = "TORNADO RESTAURANT"

# Report settings
REPORT_TITLE = "Sales Report"
