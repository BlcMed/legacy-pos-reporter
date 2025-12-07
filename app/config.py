"""
Configuration settings for the restaurant report system.
Reads all configurable values from `settings.ini`.
"""

import configparser
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '../settings.ini')
CONFIG_FILE =  os.path.join(os.path.dirname(__file__), '../config.ini')

config = configparser.ConfigParser()
config.read([SETTINGS_FILE, CONFIG_FILE])

# Backup paths
BACKUP_BASE_PATH = config["PATH"].get("backup_base_path", "./backups")
DAILY_REPORTS_PATH = config["PATH"].get("daily_reports_path", "./reports/daily")
MONTHLY_REPORTS_PATH = config["PATH"].get("monthly_reports_path","./reports/monthly")
MDB_FILENAME = "resturant.mdb"

# Restaurant info
RESTAURANT_NAME = "TORNADO RESTAURANT"
# Report settings
REPORT_TITLE = "Sales Report"

# Email configuration (from settings.ini)
EMAIL_FROM = config["EMAIL"].get("email_from", "example@gmail.com")
EMAIL_PASSWORD = config["EMAIL"].get("email_password", "")
EMAIL_TO = config["EMAIL"].get("email_to", "")
SMTP_SERVER = config["EMAIL"].get("smtp_server", "smtp.gmail.com")
SMTP_PORT = int(config["EMAIL"].get("smtp_port", "587"))
