"""
Monthly report runner - generates sales report for the current month.
"""

from datetime import datetime
import sys
import traceback

from extract import get_data_by_time
from analyze import generate_report_data
from report import generate_pdf
from email_sender import send_report_email
import config as config


def get_current_month():
    """Get the current year and month."""
    now = datetime.now()
    return now.year, now.month


def main():
    """Generate and send monthly report."""
    print("=" * 60)
    print(f"{config.RESTAURANT_NAME}")
    print("Monthly Sales Report")
    print("=" * 60)

    try:
        # Get current year and month
        year, month = get_current_month()
        report_date = datetime(year, month, 1)
        date_str = report_date.strftime("%B %Y")
        print(f"Generating report for: {date_str}")

        data = get_data_by_time(year=year, month=month)
        report = generate_report_data(data["invoices"], data["sales"])
        print(report)
        monthly_pdf_path = f"{config.MONTHLY_REPORTS_PATH}/monthly-report-{month}.pdf"

        generate_pdf(
            report_data=report,
            output_path=monthly_pdf_path,
            data_invoices=data["invoices"],
        )
        print("Monthly PDF created")

        # Send email
        print("Sending email...")

        from io import BytesIO

        try:
            with open(monthly_pdf_path, "rb") as f:
                pdf_buffer = BytesIO(f.read())
            pdf_buffer.seek(0)
            send_report_email(
                pdf_buffer=pdf_buffer, report_date_str=date_str, report_type="monthly"
            )
            print("✓ send_report_email test completed successfully.")
        except Exception as e:
            print(f"✗ send_report_email test failed: {e}")
        print("=" * 60)
        print("✓ MONTHLY REPORT SENT")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
