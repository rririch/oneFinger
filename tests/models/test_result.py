import pytest
from datetime import date, datetime
from src.models.result import BacktestResult, PerformanceMetrics, TradeRecord


def test_backtest_result():
    metrics = PerformanceMetrics(
        return_rate=0.20,
        annual_return=0.18,
        volatility=0.15,
        sharpe_ratio=1.2,
        max_drawdown=0.10,
        win_rate=0.60,
        profit_loss_ratio=1.5
    )
    result = BacktestResult(
        symbol="000001",
        strategy_name="ma_cross",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        initial_capital=100000.0,
        final_value=120000.0,
        total_return=0.20,
        metrics=metrics,
        total_trades=50,
        win_rate=0.60,
        sharpe_ratio=1.5,
        max_drawdown=0.10
    )
    assert result.total_return == 0.20
    assert result.final_value == 120000.0


def test_performance_metrics():
    metrics = PerformanceMetrics(
        return_rate=0.25,
        annual_return=0.22,
        volatility=0.15,
        sharpe_ratio=1.47,
        max_drawdown=0.08,
        win_rate=0.65,
        profit_loss_ratio=2.0
    )
    assert 0 <= metrics.win_rate <= 1


def test_trade_record():
    trade = TradeRecord(
        trade_id="t1",
        symbol="000001",
        entry_date=date(2024, 1, 15),
        entry_price=10.5,
        exit_date=date(2024, 3, 20),
        exit_price=12.0,
        quantity=1000,
        pnl=1500.0,
        pnl_rate=0.1429,
        side="long",
        commission=31.5
    )
    assert trade.pnl > 0
    assert trade.entry_price == 10.5
