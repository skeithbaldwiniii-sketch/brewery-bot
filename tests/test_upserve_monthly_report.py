from reports.upserve_monthly import (
    format_upserve_monthly_sales_report,
)


def test_format_upserve_monthly_sales_report():
    report = {
        "reporting_period": "09-01-2026 to 09-30-2026",
        "pint_sales": [
            {
                "rank": 1,
                "product": "O'Fest",
                "sold": 653,
            },
            {
                "rank": 2,
                "product": "Ghost Fleet",
                "sold": 527,
            },
        ],
        "four_pack_sales": [
            {
                "rank": 1,
                "product": "Electroplasm 4 pack",
                "sold": 55,
            },
        ],
        "bottle_750ml_sales": [
            {
                "rank": 1,
                "product": "River Run Bottle",
                "sold": 17,
            },
        ],
        "thc_sales": [
            {
                "rank": 1,
                "product": "Peach Mimosa THC",
                "sold": 86,
            },
        ],
    }

    message = format_upserve_monthly_sales_report(report)

    assert "*Upserve Monthly Sales*" in message
    assert "09-01-2026 to 09-30-2026" in message

    assert "*Pint Sales*" in message
    assert "1. O'Fest — 653" in message
    assert "2. Ghost Fleet — 527" in message

    assert "*4-Pack Sales*" in message
    assert "1. Electroplasm 4 pack — 55" in message

    assert "*750ml Bottle Sales*" in message
    assert "1. River Run Bottle — 17" in message

    assert "*THC Drinks*" in message
    assert "1. Peach Mimosa THC — 86" in message