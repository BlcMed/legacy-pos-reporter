"""
Main script to generate and send monthly restaurant report.
Run this script on the 1st of each month to generate the previous month's report.
"""

from datetime import datetime, timedelta
import sys
import traceback

from extract import get_monthly_data
from analyze import generate_report_data
from report import generate_pdf
from email_sender import send_report_email
import config


def get_previous_month():
    """Get the previous month's year and month number."""
    today = datetime.now()
    first_of_month = today.replace(day=1)
    last_month = first_of_month - timedelta(days=1)
    return last_month.year, last_month.month


def get_month_name(year, month):
    """Get formatted month name (e.g., 'November 2025')."""
    return datetime(year, month, 1).strftime("%B %Y")


def main():
    """Main execution function."""
    print("=" * 60)
    print(f"{config.RESTAURANT_NAME}")
    print("Monthly Report Generator")
    print("=" * 60)
    print()

    try:
        # Determine reporting period
        year, month = get_previous_month()
        month_name = get_month_name(year, month)

        print(f"Generating report for: {month_name}")
        print()

        # Step 1: Extract data
        print("[1/4] Extracting data from backup...")
        data = get_monthly_data(year, month)

        if len(data["invoices"]) == 0:
            print("⚠ Warning: No invoice data found for this period")
            sys.exit(1)

        print(f"  ✓ Found {len(data['invoices'])} invoices")
        print(f"  ✓ Found {len(data['sales'])} sales records")
        print()

        # Step 2: Analyze data
        print("[2/4] Analyzing sales data...")
        report_data = generate_report_data(data["invoices"], data["sales"])

        print(f"  ✓ Total Revenue: ${report_data['invoices']['total_revenue']:,.2f}")
        print(
            f"  ✓ Total Transactions: {report_data['invoices']['total_transactions']:,}"
        )
        print()

        # Step 3: Generate PDF
        print("[3/4] Generating PDF report...")
        pdf_buffer = generate_pdf(report_data)
        print("  ✓ PDF generated successfully")
        print()

        # Step 4: Send email
        print("[4/4] Sending email...")
        send_report_email(pdf_buffer, month_name)
        print()

        print("=" * 60)
        print("✓ REPORT GENERATION COMPLETE")
        print("=" * 60)
        print(f"Report for {month_name} has been emailed to {config.EMAIL_TO}")

        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("Make sure the backup path is correct in config.py")
        return 1

    except Exception as e:
        print("\n✗ Unexpected error occurred:")
        print(traceback.format_exc())
        return 1


def generate_test_report():
    """Generate a test report for the current month (for testing purposes)."""
    print("=" * 60)
    print("GENERATING TEST REPORT")
    print("=" * 60)
    print()

    try:
        # Use current month for testing
        today = datetime.now()
        year, month = today.year, today.month
        month_name = get_month_name(year, month)

        print(f"Test report for: {month_name}")
        print()

        # Extract
        print("[1/4] Extracting data...")
        data = get_monthly_data(year, month)
        print(f"  ✓ Found {len(data['invoices'])} invoices")
        print()

        # Analyze
        print("[2/4] Analyzing...")
        report_data = generate_report_data(data["invoices"], data["sales"])
        print(f"  ✓ Revenue: ${report_data['invoices']['total_revenue']:,.2f}")
        print()

        # Generate PDF to file
        print("[3/4] Generating PDF...")
        from report import generate_pdf

        output_file = f"test_report_{year}_{month:02d}.pdf"
        generate_pdf(report_data, output_file)
        print(f"  ✓ Saved to {output_file}")
        print()

        print("[4/4] Skipping email (test mode)")
        print()

        print("=" * 60)
        print(f"✓ Test report saved: {output_file}")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.exit(generate_test_report())
    else:
        sys.exit(main())
