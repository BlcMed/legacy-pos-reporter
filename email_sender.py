"""
Send email with PDF report attachment.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import config


def send_report_email(pdf_buffer, report_date_str, recipient=None, report_type="monthly"):
    """
    Send report (monthly or daily) via email.

    Args:
        pdf_buffer: BytesIO object containing PDF
        report_date_str: Date string for the report, e.g. "November 2025" or "March 8, 2025"
        recipient: Optional recipient email (defaults to config.EMAIL_TO)
        report_type: "monthly" or "daily" or any string to describe report type
    """
    recipient = recipient or config.EMAIL_TO

    # Validate config
    if not all([config.EMAIL_FROM, config.EMAIL_PASSWORD, recipient]):
        raise ValueError("Email configuration incomplete. Check .env file.")

    # Use "Monthly" or "Daily" or given type (capitalize)
    report_type_cap = report_type.capitalize()

    msg = MIMEMultipart()
    msg["From"] = config.EMAIL_FROM
    msg["To"] = recipient
    msg["Subject"] = f"{config.REPORT_TITLE} - {report_type_cap} Report - {report_date_str}"

    # Email body
    body = f"""
Dear Restaurant Owner,

Please find attached the {report_type} sales report for {report_date_str}.

Best regards,
{config.RESTAURANT_NAME} Reporting System

---
This is an automated email. Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M")}
    """.strip()

    msg.attach(MIMEText(body, "plain"))

    # Attach PDF
    pdf_buffer.seek(0)
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_buffer.read())
    encoders.encode_base64(part)

    filename_safe = report_date_str.replace(" ", "_").replace(",", "")
    filename = f"Sales_Report_{report_type_cap}_{filename_safe}.pdf"
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)

    # Send email
    try:
        print(f"Connecting to {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()

        print("Logging in...")
        server.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)

        print(f"Sending email to {recipient}...")
        server.send_message(msg)
        server.quit()

        print(f"✓ Email sent successfully to {recipient}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("✗ Authentication failed. Check EMAIL_FROM and EMAIL_PASSWORD in .env")
        raise
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


def test_email_connection():
    """Test email configuration without sending a report."""
    try:
        print(f"Testing connection to {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()

        print("Testing authentication...")
        server.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)
        server.quit()

        print("✓ Email configuration is valid!")
        return True

    except Exception as e:
        print(f"✗ Email test failed: {e}")
        return False


if __name__ == "__main__":
    # Test email connection
    print("Testing email configuration...\n")
    test_email_connection()

    # Test send_report_email with a PDF file from a known path
    print("\nTesting send_report_email with PDF from file path...")
    import os

    pdf_path = "reports/monthly-report-11.pdf"  # Change this path to your known PDF location
    test_month_name = "November 2025"

    if not os.path.exists(pdf_path):
        print(f"✗ Test PDF not found at {pdf_path}. Please generate it first.")
    else:
        from io import BytesIO
        try:
            with open(pdf_path, "rb") as f:
                pdf_buffer = BytesIO(f.read())
            pdf_buffer.seek(0)
            send_report_email(pdf_buffer, test_month_name)
            print("✓ send_report_email test completed successfully.")
        except Exception as e:
            print(f"✗ send_report_email test failed: {e}")

