"""
Analyze sales and invoice data to generate metrics.
"""

import config


def analyze_invoices(invoices_df):
    """Calculate invoice-based metrics."""
    metrics = {}

    # Basic totals
    metrics["total_revenue"] = invoices_df["AMOUNT"].sum()
    metrics["total_transactions"] = len(invoices_df)
    metrics["average_transaction"] = (
        metrics["total_revenue"] / metrics["total_transactions"]
        if metrics["total_transactions"] > 0
        else 0
    )

    # Payment breakdown
    payment_counts = invoices_df["SALE_INFO"].value_counts()
    payment_amounts = invoices_df.groupby("SALE_INFO")["AMOUNT"].sum()

    metrics["payment_breakdown"] = {
        "counts": payment_counts.to_dict(),
        "amounts": payment_amounts.to_dict(),
    }

    # Service type breakdown
    service_counts = invoices_df["C_NO"].value_counts()
    service_amounts = invoices_df.groupby("C_NO")["AMOUNT"].sum()

    metrics["service_breakdown"] = {
        "counts": service_counts.to_dict(),
        "amounts": service_amounts.to_dict(),
    }

    # Daily sales
    daily_sales = invoices_df.groupby(invoices_df["DATE"].dt.date)["AMOUNT"].sum()
    metrics["daily_sales"] = daily_sales.to_dict()

    # VAT collected
    metrics["total_vat"] = invoices_df["VAT"].sum()

    return metrics


def analyze_sales(sales_df):
    """Calculate sales-based metrics."""
    metrics = {}

    # Top selling items
    top_items = (
        sales_df.groupby("ITEMS")
        .agg({"QTY": "sum", "AMOUNT": "sum", "COST": "sum"})
        .reset_index()
    )

    top_items["PROFIT"] = top_items["AMOUNT"] - top_items["COST"]
    top_items = top_items.sort_values("AMOUNT", ascending=False).head(
        config.TOP_ITEMS_COUNT
    )

    metrics["top_items"] = top_items.to_dict("records")

    # Category performance
    category_sales = (
        sales_df.groupby("CATOGERY")
        .agg({"QTY": "sum", "AMOUNT": "sum", "COST": "sum"})
        .reset_index()
    )

    category_sales["PROFIT"] = category_sales["AMOUNT"] - category_sales["COST"]
    category_sales = category_sales.sort_values("AMOUNT", ascending=False)

    metrics["category_performance"] = category_sales.to_dict("records")

    # Total items sold
    metrics["total_items_sold"] = sales_df["QTY"].sum()

    # Total cost and profit
    metrics["total_cost"] = sales_df["COST"].sum()
    metrics["total_profit"] = sales_df["AMOUNT"].sum() - sales_df["COST"].sum()

    # Average items per order
    items_per_order = sales_df.groupby("INV_NO")["QTY"].sum()
    metrics["avg_items_per_order"] = items_per_order.mean()

    return metrics


def calculate_growth(current_metrics, previous_metrics):
    """Calculate growth percentage compared to previous month."""
    if not previous_metrics:
        return None

    current_revenue = current_metrics["invoices"]["total_revenue"]
    previous_revenue = previous_metrics["invoices"]["total_revenue"]

    if previous_revenue == 0:
        return None

    growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
    return round(growth, 1)


def generate_report_data(invoices_df, sales_df, previous_data=None):
    """
    Generate complete report data from dataframes.

    Args:
        invoices_df: Invoice DataFrame
        sales_df: Sales DataFrame
        previous_data: Optional dict with previous month's data for comparison

    Returns:
        dict with all metrics for report generation
    """
    report = {
        "invoices": analyze_invoices(invoices_df),
        "sales": analyze_sales(sales_df),
        "period": {
            "start_date": invoices_df["DATE"].min(),
            "end_date": invoices_df["DATE"].max(),
        },
    }

    # Add growth if previous data available
    if previous_data:
        report["growth"] = calculate_growth(report, previous_data)

    return report


if __name__ == "__main__":
    # Test analysis
    from extract import get_monthly_data

    data = get_monthly_data(2025, 1)
    report = generate_report_data(data["invoices"], data["sales"])

    print("\n=== REPORT METRICS ===")
    print(f"Total Revenue: {report['invoices']['total_revenue']:.2f}")
    print(f"Total Transactions: {report['invoices']['total_transactions']}")
    print(f"Average Transaction: {report['invoices']['average_transaction']:.2f}")
    print("\nTop 3 Items:")
    for i, item in enumerate(report["sales"]["top_items"][:3], 1):
        print(f"  {i}. {item['ITEMS']}: {item['QTY']} sold, {item['AMOUNT']:.2f}")
