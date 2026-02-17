import pytest
from datetime import date, timedelta
from src.strategy.ma_cross import MACrossStrategy
from src.models.ohlcv import OHLCV, BarData


def create_test_bars(prices) -> BarData:
    bars = []
    for i, price in enumerate(prices):
        bars.append(OHLCV(
            symbol="000001",
            trade_date=date(2024, 1, 1) + timedelta(days=i),
            open_price=price,
            high_price=price * 1.02,
            low_price=price * 0.98,
            close_price=price,
            volume=1000000,
            turnover=price * 1000000,
            adjustment="qfq"
        ))
    return BarData(symbol="000001", bars=bars)


def test_ma_cross_golden_cross():
    prices = [10.0] * 10 + [10.5] * 10
    data = create_test_bars(prices)
    strategy = MACrossStrategy(short_window=5, long_window=10)
    signals = strategy.generate_signals(data)
    buy_signals = [s for s in signals if s.signal_type.value == "buy"]
    assert len(buy_signals) > 0


def test_ma_cross_death_cross():
    prices = [10.5] * 10 + [10.0] * 10
    data = create_test_bars(prices)
    strategy = MACrossStrategy(short_window=5, long_window=10)
    signals = strategy.generate_signals(data)
    sell_signals = [s for s in signals if s.signal_type.value == "sell"]
    assert len(sell_signals) > 0


def test_ma_cross_insufficient_data():
    prices = [10.0, 10.1, 10.2, 10.3, 10.4]
    data = create_test_bars(prices)
    strategy = MACrossStrategy(short_window=5, long_window=20)
    signals = strategy.generate_signals(data)
    assert len(signals) == 0
