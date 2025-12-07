"""
Extract data from MDB backup files using mdb-export.
Cross-platform: works on macOS, Linux, and Windows (with mdb-export.exe).
"""

import subprocess
import pandas as pd
from pathlib import Path
from io import StringIO
import config


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


def filter_table_by_time(
    mdb_file,
    table_name,
    start_datetime=None,
    end_datetime=None,
):
    """
    Filter table rows where the combined DATE and TIME fall between two timestamps
    (start_datetime and end_datetime), and optionally filter by hour.

    Args:
        mdb_file: The .mdb file path.
        table_name: Table to extract.
        start_datetime: Inclusive minimum datetime (str, datetime, or None).
        end_datetime: Inclusive maximum datetime (str, datetime, or None).

    Returns:
        pandas.DataFrame with rows filtered by the time range.

    Example usage:
        # To extract all records between 2025-11-05 08:00 and 2025-11-10 23:59, with hours from 9 to 18:
        df = filter_table_by_time(
            "resturant.mdb",
            "INVOICE",
            start_datetime="2025-11-05 08:00",
            end_datetime="2025-11-10 23:59",
        )
    """
    df = export_table(mdb_file, table_name)
    # Parse DATE (get the date part)
    df["DATE"] = pd.to_datetime(df["DATE"], format="%m/%d/%y %H:%M:%S", errors="coerce")
    # Parse TIME (get the time part only)
    time_parsed = pd.to_datetime(
        df["TIME"], format="%m/%d/%y %H:%M:%S", errors="coerce"
    )
    # Combine: date from DATE column + time from TIME column
    df["DATE"] = pd.to_datetime(
        df["DATE"].dt.date.astype(str) + " " + time_parsed.dt.time.astype(str)
    )

    # Filter by datetime range if provided
    if start_datetime is not None:
        start = pd.to_datetime(start_datetime)
        df = df[df["DATE"] >= start]
    if end_datetime is not None:
        end = pd.to_datetime(end_datetime)
        df = df[df["DATE"] <= end]

    return df


def extract_invoices(
    mdb_file,
    start_datetime=None,
    end_datetime=None,
):
    """Extract INVOICE table for a given month and day."""
    df = filter_table_by_time(
        mdb_file,
        "INVOICE",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    return df


def extract_sales(
    mdb_file,
    start_datetime=None,
    end_datetime=None,
):
    """Extract SALE table for a given month and day."""
    df = filter_table_by_time(
        mdb_file,
        "SALE",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    return df


def get_data_by_time(
    start_datetime=None,
    end_datetime=None,
):
    """
    Get invoice and sales data for a specific month.
    Returns dictionary with DataFrames.
    """
    backup_folder = Path(config.BACKUP_BASE_PATH)
    print(f"Using backup: {backup_folder}")

    mdb_file = backup_folder / config.MDB_FILENAME
    if not mdb_file.exists():
        raise FileNotFoundError(f"MDB file not found: {mdb_file}")

    invoices = extract_invoices(
        mdb_file, start_datetime=start_datetime, end_datetime=end_datetime
    )
    sales = extract_sales(
        mdb_file, start_datetime=start_datetime, end_datetime=end_datetime
    )

    print(f"Extracted {len(invoices)} invoices and {len(sales)} sales records")
    return {"invoices": invoices, "sales": sales, "backup_folder": backup_folder}


def get_monthly_data(year, month):
    """
    Get invoice and sales data for an entire month.
    Each day starts at 14:00 of the current day and ends at 04:00 of the next day.
    """
    from datetime import datetime

    # First day at 14:00
    start_datetime = datetime(year, month, 1, 14, 0)
    # Next month's 1st day at 4:00am
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    end_datetime = datetime(next_year, next_month, 1, 4, 0)
    return get_data_by_time(start_datetime=start_datetime, end_datetime=end_datetime)


def get_daily_data(year, month, day):
    """
    Get invoice and sales data for a single business day.
    A business day starts at 14:00 of (year, month, day) and ends at 04:00 the next calendar day.
    """
    from datetime import datetime, timedelta

    start_datetime = datetime(year, month, day, 14, 0)
    # Handle day roll-over for end time
    end_time = datetime(year, month, day, 4, 0) + timedelta(days=1)
    end_datetime = end_time
    return get_data_by_time(start_datetime=start_datetime, end_datetime=end_datetime)


if __name__ == "__main__":
    start_datetime = "2025-11-19 14:00"
    end_datetime = "2025-11-20 04:00"
    data = get_data_by_time(start_datetime, end_datetime)

    print(10*"=")
    print("\nInvoices sample:")
    print(data["invoices"].head())
    print("\nSales sample:")
    print(data["sales"].head())

    data = get_daily_data(2025, 11, 19)
    print(10*"=")
    print("\nInvoices sample:")
    print(data["invoices"].head())
    print("\nSales sample:")
    print(data["sales"].head())
    
    data = get_monthly_data(2025, 11)
    print(10*"=")
    print("\nInvoices sample:")
    print(data["invoices"].head())
    print("\nSales sample:")
    print(data["sales"].head())