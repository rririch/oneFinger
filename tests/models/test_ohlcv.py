import pytest
from datetime import date
from src.models.ohlcv import OHLCV, BarData


def test_ohlcv_creation():
    bar = OHLCV(
        symbol="000001",
        trade_date=date(2024, 1, 2),
        open_price=10.5,
        high_price=11.0,
        low_price=10.3,
        close_price=10.8,
        volume=1000000,
        turnover=10800000.0,
        adjustment="qfq"
    )
    assert bar.symbol == "000001"
    assert bar.close_price == 10.8
    assert bar.adjustment == "qfq"
    assert bar.is_up is True


def test_bar_data_from_list():
    bars = [
        OHLCV(
            symbol="000001",
            trade_date=date(2024, 1, i + 1),
            open_price=10.0 + i * 0.1,
            high_price=10.5 + i * 0.1,
            low_price=9.8 + i * 0.1,
            close_price=10.2 + i * 0.1,
            volume=1000000,
            turnover=10200000.0,
            adjustment="qfq"
        )
        for i in range(5)
    ]
    data = BarData(symbol="000001", bars=bars)
    assert len(data.bars) == 5
    assert data.symbol == "000001"
    assert data.total_bars == 5


def test_price_range():
    bar = OHLCV(
        symbol="000001",
        trade_date=date(2024, 1, 2),
        open_price=10.0,
        high_price=11.0,
        low_price=9.5,
        close_price=10.5,
        volume=1000000,
        turnover=10500000.0,
        adjustment="qfq"
    )
    assert bar.price_range == pytest.approx(1.5)
