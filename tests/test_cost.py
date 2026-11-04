import pytest

from services.cost import CostInputError, calculate_landed_cost, parse_cost_form

# 計算器頁面的預設值：¥5,000、匯率 0.215、代購 5%、國際運費 NT$180、平台 8%、售價 NT$1,800
DEFAULT_FORM = {
    "price_jpy": "5000",
    "shipping_jpy": "0",
    "exchange_rate": "0.215",
    "proxy_fee_rate": "5",
    "international_shipping_twd": "180",
    "platform_fee_rate": "8",
    "expected_sale_price_twd": "1800",
}


def test_profitable_case():
    result = calculate_landed_cost(**parse_cost_form(DEFAULT_FORM))

    # 商品成本 5000 × 0.215 = 1075；代購費 1075 × 5% = 53.75
    # 落地成本 1075 + 53.75 + 180 = 1308.75；平台費 1800 × 8% = 144
    # 淨利 1800 − 1308.75 − 144 = 347.25；保本價 1308.75 ÷ 0.92 = 1422.55
    assert result == {
        "item_cost_twd": 1075,
        "proxy_fee_twd": 54,
        "landed_cost_twd": 1309,
        "platform_fee_twd": 144,
        "estimated_profit_twd": 347,
        "break_even_price_twd": 1423,
        "recommendation": "可觀察",
    }


def test_loss_is_not_recommended():
    result = calculate_landed_cost(
        price_jpy=10000,
        shipping_jpy=500,
        exchange_rate=0.215,
        proxy_fee_rate=5,
        international_shipping_twd=180,
        platform_fee_rate=8,
        expected_sale_price_twd=1500,
    )

    assert result["estimated_profit_twd"] < 0
    assert result["recommendation"] == "不建議"


def test_break_even():
    # 落地成本 1000 × 1 = 1000，無手續費，售價 1000 → 淨利剛好 0
    result = calculate_landed_cost(
        price_jpy=1000,
        shipping_jpy=0,
        exchange_rate=1,
        proxy_fee_rate=0,
        international_shipping_twd=0,
        platform_fee_rate=0,
        expected_sale_price_twd=1000,
    )

    assert result["estimated_profit_twd"] == 0
    assert result["break_even_price_twd"] == 1000
    assert result["recommendation"] == "損益兩平"


def test_selling_at_break_even_price_gives_zero_profit():
    # 用保本價（未四捨五入）賣出時，淨利應為 0
    landed_cost = (3000 + 200) * 0.21 * 1.1 + 150
    break_even = landed_cost / (1 - 0.1)
    result = calculate_landed_cost(
        price_jpy=3000,
        shipping_jpy=200,
        exchange_rate=0.21,
        proxy_fee_rate=10,
        international_shipping_twd=150,
        platform_fee_rate=10,
        expected_sale_price_twd=break_even,
    )

    assert result["estimated_profit_twd"] == 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("price_jpy", "abc", "請輸入有效的數字。"),
        ("price_jpy", "-1", "所有欄位都必須是大於或等於 0 的有限數字。"),
        ("exchange_rate", "inf", "所有欄位都必須是大於或等於 0 的有限數字。"),
        ("exchange_rate", "nan", "所有欄位都必須是大於或等於 0 的有限數字。"),
        ("platform_fee_rate", "100", "平台抽成率必須小於 100%，才能計算保本售價。"),
    ],
)
def test_invalid_input_is_rejected(field, value, message):
    form = {**DEFAULT_FORM, field: value}

    with pytest.raises(CostInputError, match=message):
        parse_cost_form(form)


def test_missing_field_is_rejected():
    form = {key: value for key, value in DEFAULT_FORM.items() if key != "price_jpy"}

    with pytest.raises(CostInputError, match="請輸入有效的數字。"):
        parse_cost_form(form)
