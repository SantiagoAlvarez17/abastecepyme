"""
Integration tests for GET /dashboard/summary (Feature 4), with in-memory SQLite.
They use the `client` fixture from conftest.py.
"""
import pytest


def create_element(client, name, element_type):
    response = client.post("/elements", json={"name": name, "element_type": element_type})
    assert response.status_code == 201
    return response.json()


def register_dependency(client, requiring, required):
    response = client.post(
        "/dependencies",
        json={"requiring_element_id": requiring["id"], "required_element_id": required["id"]},
    )
    assert response.status_code == 201


@pytest.fixture
def bakery(client):
    """
    Pan -> Masa madre -> Harina -> Molinos SA
    Torta -> Harina, Torta -> Huevos -> Granja El Roble        Panela (isolated)
    """
    e = {
        name: create_element(client, name, kind)
        for name, kind in [
            ("Molinos SA", "proveedor"),
            ("Granja El Roble", "proveedor"),
            ("Harina", "insumo"),
            ("Huevos", "insumo"),
            ("Panela", "insumo"),
            ("Masa madre", "producto"),
            ("Pan", "producto"),
            ("Torta", "producto"),
        ]
    }
    for requiring, required in [
        ("Harina", "Molinos SA"),
        ("Huevos", "Granja El Roble"),
        ("Masa madre", "Harina"),
        ("Pan", "Masa madre"),
        ("Torta", "Harina"),
        ("Torta", "Huevos"),
    ]:
        register_dependency(client, e[requiring], e[required])
    return e


def test_empty_catalog_reports_empty_status(client):
    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_elements"] == 0
    assert body["total_dependencies"] == 0
    assert body["by_type"] == {"proveedor": 0, "insumo": 0, "producto": 0}
    assert body["isolated"] == []
    assert body["critical_points"] == []
    assert body["production"]["status"] == "empty"


@pytest.mark.usefixtures("bakery")
def test_valid_chain_reports_totals_isolated_and_valid_order(client):
    body = client.get("/dashboard/summary").json()

    assert body["total_elements"] == 8
    assert body["total_dependencies"] == 6
    assert body["by_type"] == {"proveedor": 2, "insumo": 3, "producto": 3}
    assert [e["name"] for e in body["isolated"]] == ["Panela"]
    assert body["production"]["status"] == "valid"
    assert body["production"]["stage_count"] == 4
    assert body["production"]["cycles"] == []


@pytest.mark.usefixtures("bakery")
def test_critical_points_are_ranked_by_affected_products(client):
    points = client.get("/dashboard/summary").json()["critical_points"]

    # Molinos SA and Harina stop 3 products; Molinos also reaches Harina, so it ranks first.
    assert [(p["name"], p["affected_products"], p["affected_total"]) for p in points] == [
        ("Molinos SA", 3, 4),
        ("Harina", 3, 3),
        ("Granja El Roble", 1, 2),
        ("Huevos", 1, 1),
    ]
    assert points[0]["products"] == ["Masa madre", "Pan", "Torta"]
    # Products are never failure candidates and isolated inputs reach nothing.
    assert all(p["element_type"] != "producto" for p in points)
    assert "Panela" not in [p["name"] for p in points]


@pytest.mark.usefixtures("bakery")
def test_limit_truncates_the_ranking(client):
    points = client.get("/dashboard/summary?limit=2").json()["critical_points"]

    assert [p["name"] for p in points] == ["Molinos SA", "Harina"]


@pytest.mark.parametrize("limit", ["0", "51", "abc"])
def test_invalid_limit_is_rejected_with_validation_error(client, limit):
    response = client.get(f"/dashboard/summary?limit={limit}")

    assert response.status_code == 422
    assert response.json()["error_code"] == "ERR_VALIDATION"


def test_cycle_is_reported_as_status_not_as_error(client, bakery):
    # Masa madre -> Pan closes Pan -> Masa madre -> Pan.
    register_dependency(client, bakery["Masa madre"], bakery["Pan"])

    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    production = response.json()["production"]
    assert production["status"] == "cycle"
    assert production["stage_count"] == 0
    assert production["blocked_count"] == 2
    assert [c["text"] for c in production["cycles"]] == ["Masa madre → Pan → Masa madre"]
    assert "Ciclo detectado" in production["message"]
    # The rest of the dashboard keeps working while the catalog is contradictory.
    assert response.json()["critical_points"][0]["name"] == "Molinos SA"
