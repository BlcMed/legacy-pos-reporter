"""
Daily report runner - generates yesterday's sales report.
"""

from datetime import datetime, timedelta
import sys
import traceback

from extract import get_daily_data
from analyze import generate_report_data
from report import generate_pdf
from email_sender import send_report_email
import config as config


def get_yesterday():
    """Get yesterday's date."""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.year, yesterday.month, yesterday.day


def main():
    """Generate and send daily report."""
    print("=" * 60)
    print(f"{config.RESTAURANT_NAME}")
    print("Daily Sales Report")
    print("=" * 60)

    try:
        # Get yesterday's date
        year, month, day = get_yesterday()
        report_date = datetime(year, month, day)
        date_str = report_date.strftime("%B %d, %Y")
        print(f"Generating report for: {date_str}")

        data = get_daily_data(year=year, month=month, day=day)
        report = generate_report_data(data["invoices"], data["sales"])
        print(report)
        daily_pdf_path=f"{config.DAILY_REPORTS_PATH}/daily-report-{month}-{day}.pdf"
        pdf_buffer = generate_pdf(
            report_data=report,
            output_path=daily_pdf_path,
            data_invoices=data["invoices"],
        )
        print("Daily PDF created")

        # Send email
        print("Sending email...")

        from io import BytesIO
        try:
            with open(daily_pdf_path, "rb") as f:
                pdf_buffer = BytesIO(f.read())
            pdf_buffer.seek(0)
            send_report_email(
                pdf_buffer=pdf_buffer, report_date_str=date_str, report_type="daily"
            )
            print("✓ send_report_email test completed successfully.")
        except Exception as e:
            print(f"✗ send_report_email test failed: {e}")
        print("=" * 60)
        print("✓ DAILY REPORT SENT")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
