"""
Extract data from MDB backup files using mdb-export.
Cross-platform: works on macOS, Linux, and Windows (with mdb-export.exe).
"""

import subprocess
import pandas as pd
from pathlib import Path
from io import StringIO
import config  # your config file


def find_latest_backup():
    """Find the most recent backup folder."""
    backup_path = Path(config.BACKUP_BASE_PATH)

    if not backup_path.exists():
        raise FileNotFoundError(f"Backup path not found: {config.BACKUP_BASE_PATH}")

    backup_folders = [
        f
        for f in backup_path.iterdir()
        if f.is_dir() and f.name.upper().startswith("BACKUP")
    ]
    if not backup_folders:
        raise FileNotFoundError("No backup folders found")

    # Sort by modification time, get latest
    latest_backup = max(backup_folders, key=lambda x: x.stat().st_mtime)
    return latest_backup


def export_table(mdb_file, table_name):
    """
    Export an MDB table to pandas DataFrame using mdb-export.
    Works on macOS/Linux/Windows (requires mdb-export.exe on Windows).
    """
    try:
        # If on Windows, you might need to provide full path to mdb-export.exe
        cmd = ["mdb-export", str(mdb_file), table_name]
        output = subprocess.check_output(cmd)
    except FileNotFoundError as e:
        raise RuntimeError(
            "mdb-export not found. Install mdbtools or ensure mdb-export.exe is in PATH."
        ) from e
    df = pd.read_csv(StringIO(output.decode("utf-8")))
    return df


def filter_table_by_time(mdb_file, table_name, year, month=None, day=None):
    """Extract INVOICE table for a given monthnd a day."""
    df = export_table(mdb_file, table_name)
    df["DATE"] = pd.to_datetime(df["DATE"], format="%m/%d/%y %H:%M:%S", errors="coerce")
    # Filter by month
    if day and month:
        df = df[
            (df["DATE"].dt.year == year)
            & (df["DATE"].dt.month == month)
            & (df["DATE"].dt.day == day)
        ]
    elif month:
        df = df[(df["DATE"].dt.year == year) & (df["DATE"].dt.month == month)]
    else:
        df = df[(df["DATE"].dt.year == year)]

    return df


def extract_invoices(mdb_file, year, month=None, day=None):
    """Extract INVOICE table for a given month and day."""
    df = filter_table_by_time(mdb_file, "INVOICE", year, month, day)
    return df


def extract_sales(mdb_file, year, month=None, day=None):
    """Extract SALE table for a given month and day."""
    df = filter_table_by_time(mdb_file, "SALE", year, month, day)
    return df


def get_data_by_time(year, month=None, day=None):
    """
    Get invoice and sales data for a specific month.
    Returns dictionary with DataFrames.
    """
    backup_folder = find_latest_backup()
    print(f"Using backup: {backup_folder}")

    mdb_file = backup_folder / config.MDB_FILENAME
    if not mdb_file.exists():
        raise FileNotFoundError(f"MDB file not found: {mdb_file}")

    invoices = extract_invoices(mdb_file, year, month, day)
    sales = extract_sales(mdb_file, year, month, day)

    print(f"Extracted {len(invoices)} invoices and {len(sales)} sales records")
    return {"invoices": invoices, "sales": sales, "backup_folder": backup_folder}


if __name__ == "__main__":
    data = get_data_by_time(year=2025, month=9, day=17)
    print("\nInvoices sample:")
    print(data["invoices"].head())
    print("\nSales sample:")
    print(data["sales"].head())
