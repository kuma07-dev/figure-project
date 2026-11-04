import pytest

from crawler.rakuten_crawler import EXCLUDE_KEYWORDS, calculate_popularity_score, clean_items


def make_item(title="一番くじ 呪術廻戦 A賞 五条悟 フィギュア", price=3000):
    return {"title": title, "price_jpy": price}


def test_normal_item_is_kept():
    item = make_item()

    assert clean_items([item]) == [item]


@pytest.mark.parametrize("keyword", EXCLUDE_KEYWORDS)
def test_excluded_keywords_are_removed(keyword):
    item = make_item(title=f"一番くじ 呪術廻戦 {keyword}")

    assert clean_items([item]) == []


@pytest.mark.parametrize(
    ("price", "kept"),
    [
        (499, False),
        (500, True),
        (30000, True),
        (30001, False),
    ],
)
def test_price_range_boundaries(price, kept):
    item = make_item(price=price)

    assert (clean_items([item]) == [item]) is kept


@pytest.mark.parametrize(
    "item",
    [
        {"title": "", "price_jpy": 3000},
        {"title": None, "price_jpy": 3000},
        {"title": "一番くじ 五条悟", "price_jpy": None},
        {"price_jpy": 3000},
    ],
)
def test_items_missing_title_or_price_are_removed(item):
    assert clean_items([item]) == []


def test_custom_price_range():
    item = make_item(price=800)

    assert clean_items([item], min_price=1000, max_price=5000) == []


def test_popularity_score_is_between_1_and_5():
    for total_count in (0, 1, 10, 100, 1000, 10000, 100000):
        assert 1 <= calculate_popularity_score(total_count) <= 5
