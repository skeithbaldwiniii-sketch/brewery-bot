"""
Formatting for weekly Upserve sales reports.
"""


def format_upserve_sales_report(report: dict) -> str:
    """
    Format parsed Upserve sales data for Slack.

    The number of products is dynamic. The report includes every
    qualifying product returned by the parser.
    """

    reporting_period = report.get("reporting_period")
    products = report.get("products", [])

    if reporting_period:
        header = f"🍺 *Upserve Weekly Sales*\n{reporting_period}"
    else:
        header = "🍺 *Upserve Weekly Sales*"

    if not products:
        return (
            f"{header}\n\n"
            "No B - Full or C - Full products were reported this week."
        )

    lines = [
        header,
        "",
        "*B - Full / C - Full Sales*",
        "",
    ]

    for product in products:
        lines.append(
            f"{product['rank']}. {product['product']} — "
            f"{product['sold']}"
        )

    return "\n".join(lines)

from integrations.upserve import parse_upserve_sales_report


def generate_upserve_sales_report(file_path) -> str:
    """
    Parse an Upserve CSV and generate the Slack-ready weekly sales report.
    """
    report = parse_upserve_sales_report(file_path)
    return format_upserve_sales_report(report)