"""
Generate PDF report from analyzed data.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from io import BytesIO
import config


def create_header(styles, report_data):
    """Create report header."""
    elements = []

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    elements.append(Paragraph(config.RESTAURANT_NAME, title_style))

    # Subtitle
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=16,
        textColor=colors.HexColor("#666666"),
        spaceAfter=12,
        alignment=TA_CENTER,
    )

    period_start = report_data["period"]["start_date"].strftime("%B %Y")
    elements.append(
        Paragraph(f"{config.REPORT_TITLE} - {period_start}", subtitle_style)
    )

    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_summary_section(report_data):
    """Create executive summary section."""
    elements = []

    # Section title
    elements.append(
        Paragraph("<b>EXECUTIVE SUMMARY</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    inv_metrics = report_data["invoices"]

    # Summary table
    summary_data = [
        ["Total Revenue", f"{inv_metrics['total_revenue']:,.2f}"],
        ["Total Transactions", f"{inv_metrics['total_transactions']:,}"],
        ["Average Transaction", f"{inv_metrics['average_transaction']:.2f}"],
        ["Total VAT Collected", f"{inv_metrics['total_vat']:.2f}"],
    ]

    # Add growth if available
    if "growth" in report_data and report_data["growth"] is not None:
        growth = report_data["growth"]
        arrow = "↑" if growth > 0 else "↓"
        summary_data.append(["Growth vs Previous Month", f"{growth:+.1f}% {arrow}"])

    summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.white),
            ]
        )
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_payment_section(report_data):
    """Create payment breakdown section."""
    elements = []

    elements.append(
        Paragraph("<b>PAYMENT BREAKDOWN</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    payment_data = [["Payment Method", "Transactions", "Amount", "Percentage"]]

    total_amount = report_data["invoices"]["total_revenue"]

    for method, amount in report_data["invoices"]["payment_breakdown"][
        "amounts"
    ].items():
        count = report_data["invoices"]["payment_breakdown"]["counts"].get(method, 0)
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        payment_data.append(
            [method, f"{count:,}", f"{amount:,.2f}", f"{percentage:.1f}%"]
        )

    payment_table = Table(
        payment_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch]
    )
    payment_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(payment_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_service_section(report_data):
    """Create service type breakdown section."""
    elements = []

    elements.append(
        Paragraph("<b>SERVICE TYPE BREAKDOWN</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    service_data = [["Service Type", "Orders", "Amount", "Percentage"]]

    total_amount = report_data["invoices"]["total_revenue"]

    for service, amount in report_data["invoices"]["service_breakdown"][
        "amounts"
    ].items():
        count = report_data["invoices"]["service_breakdown"]["counts"].get(service, 0)
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        service_data.append(
            [service, f"{count:,}", f"{amount:,.2f}", f"{percentage:.1f}%"]
        )

    service_table = Table(
        service_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch]
    )
    service_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(service_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_top_items_section(report_data):
    """Create top selling items section."""
    elements = []

    elements.append(
        Paragraph(
            "<b>RANKED SELLING ITEMS</b>",
            getSampleStyleSheet()["Heading2"],
        )
    )
    elements.append(Spacer(1, 0.1 * inch))

    items_data = [["Rank", "Item", "Qty Sold", "Revenue", "Profit"]]

    for i, item in enumerate(report_data["sales"]["top_items"], 1):
        items_data.append(
            [
                str(i),
                item["ITEMS"],
                f"{int(item['QTY']):,}",
                f"{item['AMOUNT']:,.2f}",
                f"{item['PROFIT']:,.2f}",
            ]
        )

    items_table = Table(
        items_data, colWidths=[0.5 * inch, 2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.beige, colors.white]),
            ]
        )
    )

    elements.append(items_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_category_section(report_data):
    """Create category performance section."""
    elements = []

    elements.append(
        Paragraph("<b>CATEGORY PERFORMANCE</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    category_data = [["Category", "Items Sold", "Revenue", "Profit", "Margin %"]]

    for cat in report_data["sales"]["category_performance"]:
        margin = (cat["PROFIT"] / cat["AMOUNT"] * 100) if cat["AMOUNT"] > 0 else 0
        category_data.append(
            [
                cat["CATOGERY"],
                f"{int(cat['QTY']):,}",
                f"{cat['AMOUNT']:,.2f}",
                f"{cat['PROFIT']:,.2f}",
                f"{margin:.1f}%",
            ]
        )

    category_table = Table(
        category_data,
        colWidths=[2 * inch, 1.2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch],
    )
    category_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.beige, colors.white]),
            ]
        )
    )

    elements.append(category_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_footer(canvas, doc):
    """Add footer to each page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(
        inch, 0.75 * inch, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    canvas.drawRightString(letter[0] - inch, 0.75 * inch, f"Page {doc.page}")
    canvas.restoreState()


def create_invoice_table(data_invoices, styles):
    """
    Create a detailed invoice table to include all invoices for detailed reports.

    Args:
        data_invoices: pandas DataFrame with invoice data. Expected columns include:
            - "DATE" (datetime/date)
            - "TABLE_NO" (str/int)
            - "WAITOR" (str)
            - "AMOUNT" (float, total for invoice)
            - "DISCOUNT" (float)
            - "SERVICE" (float)
            - "VAT" (float)
            - "TOTAL" (float, optional; if not present, computed as AMOUNT - DISCOUNT + SERVICE + VAT)
        styles: reportlab style dictionary

    Returns:
        List of Flowable elements (Table with all invoices)
    """
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer

    # Choose relevant columns and friendly headers
    COLUMNS = [
        ("DATE", "Date"),
        ("TABLE_NO", "Table"),
        ("WAITOR", "Waiter"),
        ("AMOUNT", "Amount"),
        ("DISCOUNT", "Discount"),
        ("SERVICE", "Service"),
        ("VAT", "VAT"),
        ("TOTAL", "Total"),
    ]

    # Check if required columns exist, if TOTAL not, calculate it
    df = data_invoices.copy()
    if "TOTAL" not in df:
        # Try to calculate TOTAL as AMOUNT - DISCOUNT + SERVICE + VAT (if all present)
        cols_needed = {"AMOUNT", "DISCOUNT", "SERVICE", "VAT"}
        if cols_needed.issubset(df.columns):
            df["TOTAL"] = (
                df["AMOUNT"].fillna(0)
                - df["DISCOUNT"].fillna(0)
                + df["SERVICE"].fillna(0)
                + df["VAT"].fillna(0)
            )
        else:
            df["TOTAL"] = None  # fallback

    # Prepare table data: headers first, then per-row values
    headers = [label for _, label in COLUMNS]
    table_data = [headers]
    date_fmt = "%Y-%m-%d"

    for _, row in df.iterrows():
        row_data = []
        for col, _ in COLUMNS:
            val = row.get(col, "")
            if col == "DATE":
                # Try to format date
                if hasattr(val, "strftime"):
                    val = val.strftime(date_fmt)
                else:
                    val = str(val)
            elif col in ["AMOUNT", "DISCOUNT", "SERVICE", "VAT", "TOTAL"]:
                try:
                    val = f"{float(val):.2f}"
                except Exception:
                    val = ""
            row_data.append(val)
        table_data.append(row_data)

    # Create the table
    invoice_table = Table(table_data, repeatRows=1, hAlign="LEFT")

    # Table style
    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FAFAFA")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#333333")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#F3F3F3")],
            ),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]
    )
    invoice_table.setStyle(table_style)

    caption_style = styles["Normal"]
    caption_style.textColor = colors.HexColor("#555555")
    caption = Paragraph("Detailed Invoices", caption_style)

    elements = [Spacer(1, 0.2 * inch), caption, Spacer(1, 0.08 * inch), invoice_table]
    return elements


def generate_no_sales_pdf(output_path=None):
    """
    Generate a PDF that displays a note indicating there are no sales today.
    If output_path is given, saves to that path. Otherwise, returns a BytesIO buffer.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph
    from reportlab.lib.units import inch
    styles = getSampleStyleSheet()

    note_style = styles['Title']
    note_style.textColor = "#333333"
    note = Paragraph("No sales today.", note_style)
    elements = [Spacer(1, 2 * inch), note]

    if output_path:
        pdf = SimpleDocTemplate(output_path, pagesize=letter)
        pdf.build(elements)
        print(f"Zero-sales PDF generated: {output_path}")
        return None
    else:
        from io import BytesIO
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        pdf.build(elements)
        buffer.seek(0)
        return buffer

def generate_pdf(report_data, output_path=None, data_invoices=None):
    """
    Generate PDF report from analyzed data. If is_detailed is True,
    includes a detailed invoice table using data_invoices.

    Args:
        report_data: Dict with analyzed metrics
        output_path: Optional file path. If None, returns BytesIO
        data_invoices: pandas DataFrame, Optional for detailed report

    Returns:
        BytesIO object if output_path is None, otherwise None
    """

    # Check for zero transactions and generate a "no sales" PDF if so
    if (
        not report_data
        or "invoices" not in report_data
        or report_data["invoices"].get("total_transactions", 0) == 0
    ):
        msg = "No data available: report not generated (0 transactions)."
        if output_path:
            print(f"Skipped PDF generation for {output_path} - {msg}")
        else:
            print(msg)
        # return None
        return generate_no_sales_pdf(output_path=output_path)


    # Create PDF
    if output_path:
        pdf = SimpleDocTemplate(output_path, pagesize=letter)
    else:
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Container for elements
    elements = []
    styles = getSampleStyleSheet()

    # Build report sections
    elements.extend(create_header(styles, report_data))
    elements.extend(create_summary_section(report_data))
    elements.extend(create_payment_section(report_data))
    elements.extend(create_service_section(report_data))
    elements.extend(create_top_items_section(report_data))
    elements.extend(create_category_section(report_data))

    # Optionally add detailed invoice table
    if data_invoices is not None:
        elements.append(Spacer(1, 0.1 * inch))
        elements.extend(create_invoice_table(data_invoices, styles))

    # Build PDF
    pdf.build(elements, onFirstPage=create_footer, onLaterPages=create_footer)

    if output_path:
        if data_invoices is not None:
            print(f"Detailed PDF generated: {output_path}")
        else:
            print(f"PDF generated: {output_path}")
        return None
    else:
        buffer.seek(0)
        return buffer


if __name__ == "__main__":
    # Test PDF generation
    from extract import get_data_by_time
    from analyze import generate_report_data

    month = 11
    day = None

    # Generate normal (summary) PDF report for the whole month
    data = get_data_by_time(year=2025, month=month, day=day)  # entire month data
    report = generate_report_data(data["invoices"], data["sales"])
    print(report)
    generate_pdf(report, f"{config.MONTHLY_REPORTS_PATH}/monthly-report-{month}.pdf", data_invoices=data["invoices"])
    print("Monthly PDF created")

    # Generate detailed PDF report for a single day
    day = 1
    month = 3
    data_day = get_data_by_time(2025, month, day=day)
    data_invoices = data_day["invoices"]
    data_sales = data_day["sales"]
    report_day = generate_report_data(data_invoices, data_sales)
    generate_pdf(
        report_data=report_day,
        data_invoices=data_invoices,
        output_path=f"{config.DAILY_REPORTS_PATH}/daily-report_{month}_{day}.pdf",
    )
    print("Daily PDF created")

    from calendar import monthrange

    for month in range(3, 12):
        num_days = monthrange(2025, month)[1]
        for day in range(1, num_days + 1):
            data_day = get_data_by_time(2025, month, day=day)
            data_invoices = data_day["invoices"]
            data_sales = data_day["sales"]
            report_day = generate_report_data(data_invoices, data_sales)
            generate_pdf(
                report_data=report_day,
                data_invoices=data_invoices,
                output_path=f"reports/daily/dailydetailed_report_{month}_{day}.pdf",
            )
            print(f"Detailed PDF created for {month}/{day}/2025")
