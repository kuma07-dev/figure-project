"""跨境購入成本與損益試算。"""

from math import isfinite

FIELD_NAMES = (
    "price_jpy",
    "shipping_jpy",
    "exchange_rate",
    "proxy_fee_rate",
    "international_shipping_twd",
    "platform_fee_rate",
    "expected_sale_price_twd",
)


class CostInputError(ValueError):
    """輸入的數值無法計算時拋出，訊息可直接顯示給使用者。"""


def parse_cost_form(form):
    """把表單欄位轉成浮點數，並檢查是否可以計算。"""
    try:
        values = {name: float(form[name]) for name in FIELD_NAMES}
    except (KeyError, TypeError, ValueError) as error:
        raise CostInputError("請輸入有效的數字。") from error

    if not all(isfinite(value) and value >= 0 for value in values.values()):
        raise CostInputError("所有欄位都必須是大於或等於 0 的有限數字。")
    if values["platform_fee_rate"] >= 100:
        raise CostInputError("平台抽成率必須小於 100%，才能計算保本售價。")
    return values


def calculate_landed_cost(
    price_jpy,
    shipping_jpy,
    exchange_rate,
    proxy_fee_rate,
    international_shipping_twd,
    platform_fee_rate,
    expected_sale_price_twd,
):
    """計算落地成本、保本售價與預估淨利。

    proxy_fee_rate 與 platform_fee_rate 為百分比（例如 10 代表 10%）。
    金額欄位四捨五入到整數台幣。
    """
    proxy_rate = proxy_fee_rate / 100
    platform_rate = platform_fee_rate / 100

    item_cost_twd = (price_jpy + shipping_jpy) * exchange_rate
    proxy_fee_twd = item_cost_twd * proxy_rate
    landed_cost_twd = item_cost_twd + proxy_fee_twd + international_shipping_twd
    platform_fee_twd = expected_sale_price_twd * platform_rate
    estimated_profit_twd = expected_sale_price_twd - landed_cost_twd - platform_fee_twd
    break_even_price_twd = landed_cost_twd / (1 - platform_rate)

    if estimated_profit_twd > 0:
        recommendation = "可觀察"
    elif estimated_profit_twd == 0:
        recommendation = "損益兩平"
    else:
        recommendation = "不建議"

    return {
        "item_cost_twd": round(item_cost_twd),
        "proxy_fee_twd": round(proxy_fee_twd),
        "landed_cost_twd": round(landed_cost_twd),
        "platform_fee_twd": round(platform_fee_twd),
        "estimated_profit_twd": round(estimated_profit_twd),
        "break_even_price_twd": round(break_even_price_twd),
        "recommendation": recommendation,
    }
