import pytest
from datetime import date, timedelta
from src.strategy.rsi import RSIStrategy
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


def test_rsi_oversold_golden_cross():
    prices = [10.0] * 20 + [8.0] * 5 + [10.0] * 10  # 下跌后反弹
    data = create_test_bars(prices)
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    signals = strategy.generate_signals(data)
    buy_signals = [s for s in signals if s.signal_type.value == "buy"]
    assert len(buy_signals) > 0


def test_rsi_overbought_death_cross():
    prices = [10.0] * 20 + [12.0] * 5 + [10.0] * 10  # 上涨后回调
    data = create_test_bars(prices)
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    signals = strategy.generate_signals(data)
    sell_signals = [s for s in signals if s.signal_type.value == "sell"]
    assert len(sell_signals) > 0


def test_rsi_insufficient_data():
    prices = [10.0, 10.1, 10.2, 10.3, 10.4]
    data = create_test_bars(prices)
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    signals = strategy.generate_signals(data)
    assert len(signals) == 0


def test_rsi_no_signal_in_stable_market():
    prices = [10.0] * 30  # 震荡市场，RSI在50附近
    data = create_test_bars(prices)
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    signals = strategy.generate_signals(data)
    assert len(signals) == 0
