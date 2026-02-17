import pytest
from datetime import date, timedelta
from src.core.engine import BacktestEngine
from src.strategy.base import Strategy, Signal, SignalType
from src.models.ohlcv import OHLCV, BarData


def create_simple_bars() -> BarData:
    base_price = 10.0
    bars = []
    for i in range(100):
        price = base_price + i * 0.1
        bars.append(OHLCV(
            symbol="000001",
            trade_date=date(2024, 1, 1) + timedelta(days=i),
            open_price=price,
            high_price=price * 1.02,
            low_price=price * 0.98,
            close_price=price + 0.05,
            volume=1000000,
            turnover=(price + 0.05) * 1000000,
            adjustment="qfq"
        ))
    return BarData(symbol="000001", bars=bars)


class DummyStrategy(Strategy):
    def generate_signals(self, data: BarData) -> list[Signal]:
        signals = []
        for i, bar in enumerate(data.bars):
            if i < 10:
                signals.append(Signal(
                    symbol=data.symbol,
                    signal_type=SignalType.BUY,
                    price=bar.close_price,
                    timestamp=bar.trade_date,
                    strength=1.0,
                    reason="dummy_buy"
                ))
            elif i == 50:
                signals.append(Signal(
                    symbol=data.symbol,
                    signal_type=SignalType.SELL,
                    price=bar.close_price,
                    timestamp=bar.trade_date,
                    strength=1.0,
                    reason="dummy_sell"
                ))
        return signals


def test_engine_basic_run():
    data = create_simple_bars()
    strategy = DummyStrategy(name="dummy")
    engine = BacktestEngine(
        initial_capital=100000.0,
        fee_rate=0.0003
    )
    result = engine.run(data, strategy)
    assert result.initial_capital == 100000.0
    assert result.final_value > 0
    assert result.total_trades >= 0


def test_engine_calculates_metrics():
    data = create_simple_bars()
    strategy = DummyStrategy(name="dummy")
    engine = BacktestEngine(
        initial_capital=100000.0,
        fee_rate=0.0003
    )
    result = engine.run(data, strategy)
    assert result.metrics is not None
    assert result.metrics.sharpe_ratio is not None
