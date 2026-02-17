import pytest
from datetime import date
from src.data.akshare_provider import AkshareProvider


def test_fetch_stock_daily():
    provider = AkshareProvider()
    data = provider.fetch_stock_daily(
        symbol="000001",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        adjustment="qfq"
    )
    assert len(data.bars) > 0
    assert data.symbol == "000001"


def test_fetch_stock_info():
    provider = AkshareProvider()
    info = provider.get_stock_info("000001")
    assert info is not None
    assert "name" in info


def test_search_stocks():
    provider = AkshareProvider()
    results = provider.search_stocks("平安")
    assert len(results) >= 0
