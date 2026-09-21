from integrations import beer30


def test_get_wholesale_inventory_normalizes_finished_goods(monkeypatch):
    def fake_finished_goods():
        return {
            "finished-goods": [
                {
                    "product-id": "123",
                    "brand": "Test Beer",
                    "package": "16-oz Can [4pk x 6]",
                    "package-unit": "Cans",
                    "package-size": "16-oz",
                    "package-size-oz": 16,
                    "units-per-case": "24.0000",
                    "locations": [
                        {
                            "location-id": "313",
                            "location-name": "Coldbox",
                            "total": 12,
                            "allocated": 2,
                            "available": 10,
                        }
                    ],
                }
            ]
        }

    monkeypatch.setattr(
        beer30,
        "get_finished_goods",
        fake_finished_goods,
    )

    result = beer30.get_wholesale_inventory()

    assert result == [
        {
            "product_id": "123",
            "brand": "Test Beer",
            "package": "16-oz Can [4pk x 6]",
            "package_unit": "Cans",
            "package_size": "16-oz",
            "package_size_oz": 16,
            "units_per_case": 24.0,
            "total": 12,
            "allocated": 2,
            "available": 10,
            "location_id": "313",
            "location_name": "Coldbox",
        }
    ]


def test_get_wholesale_inventory_returns_empty_when_no_finished_goods(
    monkeypatch,
):
    monkeypatch.setattr(
        beer30,
        "get_finished_goods",
        lambda: None,
    )

    assert beer30.get_wholesale_inventory() == []


def test_get_wholesale_inventory_handles_empty_finished_goods(
    monkeypatch,
):
    monkeypatch.setattr(
        beer30,
        "get_finished_goods",
        lambda: {"finished-goods": []},
    )

    assert beer30.get_wholesale_inventory() == []
