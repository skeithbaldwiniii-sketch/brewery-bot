"""
Formatting for monthly Upserve sales reports.
"""


def _format_sales_section(
    title: str,
    products: list[dict],
    empty_message: str,
) -> list[str]:
    """Format one monthly sales ranking section."""

    lines = [
        title,
        "",
    ]

    if not products:
        lines.append(empty_message)
        return lines

    for product in products:
        lines.append(
            f"{product['rank']}. {product['product']} — "
            f"{product['sold']}"
        )

    return lines


def format_upserve_monthly_sales_report(report: dict) -> str:
    """
    Format parsed monthly Upserve sales data for Slack or email.
    """

    reporting_period = report.get("reporting_period")

    if reporting_period:
        header = (
            f"🍺 *Upserve Monthly Sales*\n"
            f"{reporting_period}"
        )
    else:
        header = "🍺 *Upserve Monthly Sales*"

    lines = [
        header,
        "",
    ]

    lines.extend(
        _format_sales_section(
            "*Pint Sales*",
            report.get("pint_sales", []),
            "No pint sales were reported this month.",
        )
    )

    lines.extend([""])

    lines.extend(
        _format_sales_section(
            "*4-Pack Sales*",
            report.get("four_pack_sales", []),
            "No 4-pack sales were reported this month.",
        )
    )

    lines.extend([""])

    lines.extend(
        _format_sales_section(
            "*750ml Bottle Sales*",
            report.get("bottle_750ml_sales", []),
            "No 750ml bottle sales were reported this month.",
        )
    )

    lines.extend([""])

    lines.extend(
        _format_sales_section(
            "*THC Drinks*",
            report.get("thc_sales", []),
            "No THC drinks were reported this month.",
        )
    )

    return "\n".join(lines)


from integrations.upserve import parse_upserve_monthly_sales_report

def format_upserve_monthly_sales_email(report: dict) -> str:
    """
    Format parsed monthly Upserve sales data as a plain-text email.
    """

    reporting_period = report.get("reporting_period")

    if reporting_period:
        header = (
            "Upserve Monthly Sales\n"
            f"{reporting_period}"
        )
    else:
        header = "Upserve Monthly Sales"

    lines = [
        header,
        "",
        "Pint Sales",
        "----------",
    ]

    pint_sales = report.get("pint_sales", [])
    if pint_sales:
        for product in pint_sales:
            lines.append(
                f"{product['rank']}. {product['product']} — "
                f"{product['sold']}"
            )
    else:
        lines.append("No pint sales were reported this month.")

    lines.extend([
        "",
        "4-Pack Sales",
        "------------",
    ])

    four_pack_sales = report.get("four_pack_sales", [])
    if four_pack_sales:
        for product in four_pack_sales:
            lines.append(
                f"{product['rank']}. {product['product']} — "
                f"{product['sold']}"
            )
    else:
        lines.append("No 4-pack sales were reported this month.")

    lines.extend([
        "",
        "750ml Bottle Sales",
        "------------------",
    ])

    bottle_sales = report.get("bottle_750ml_sales", [])
    if bottle_sales:
        for product in bottle_sales:
            lines.append(
                f"{product['rank']}. {product['product']} — "
                f"{product['sold']}"
            )
    else:
        lines.append("No 750ml bottle sales were reported this month.")

    lines.extend([
        "",
        "THC Drinks",
        "----------",
    ])

    thc_sales = report.get("thc_sales", [])
    if thc_sales:
        for product in thc_sales:
            lines.append(
                f"{product['rank']}. {product['product']} — "
                f"{product['sold']}"
            )
    else:
        lines.append("No THC drinks were reported this month.")

    return "\n".join(lines)

def generate_upserve_monthly_sales_report(file_path) -> str:
    """
    Parse an Upserve monthly CSV and generate the Slack/email-ready report.
    """
    report = parse_upserve_monthly_sales_report(file_path)
    return format_upserve_monthly_sales_report(report)