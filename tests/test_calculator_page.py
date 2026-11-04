import pytest

from app import app
from tests.test_cost import DEFAULT_FORM


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_calculator_page_loads(client):
    response = client.get("/calculator")

    assert response.status_code == 200


def test_calculator_shows_result(client):
    response = client.post("/calculator", data=DEFAULT_FORM)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "NT$ 1309" in html
    assert "投資模型良好" in html


def test_calculator_shows_error_for_invalid_input(client):
    response = client.post("/calculator", data={**DEFAULT_FORM, "price_jpy": "-5"})
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "所有欄位都必須是大於或等於 0 的有限數字。" in html
