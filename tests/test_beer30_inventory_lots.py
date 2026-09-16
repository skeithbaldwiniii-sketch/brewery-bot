from integrations import beer30


def test_get_inventory_lots_uses_item_type_and_id(monkeypatch):
    captured = {}

    def fake_request(endpoint, params=None):
        captured["endpoint"] = endpoint
        captured["params"] = params
        return {"inventory": [{"AdjunctsName": "Citra Incognito"}]}

    monkeypatch.setattr(beer30, "_request", fake_request)

    result = beer30.get_inventory_lots("adjuncts", "1039472")

    assert captured["endpoint"] == "inventory/items/lots"
    assert captured["params"] == {
        "type": "adjuncts",
        "id": "1039472",
    }
    assert result == {
        "inventory": [{"AdjunctsName": "Citra Incognito"}]
    }


def test_get_inventory_lots_rejects_invalid_type():
    try:
        beer30.get_inventory_lots("invalid", "1039472")
    except ValueError as exc:
        assert "Invalid Beer30 inventory type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_get_inventory_lots_rejects_empty_item_id():
    try:
        beer30.get_inventory_lots("adjuncts", "")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
