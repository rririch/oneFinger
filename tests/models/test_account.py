import pytest
from datetime import datetime
from src.models.account import Position, Account


def test_position_creation():
    position = Position(
        symbol="000001",
        quantity=100,
        avg_cost=10.5
    )
    assert position.quantity == 100
    mv = position.get_market_value(current_price=10.5)
    assert mv == 1050.0
    pnl = position.get_unrealized_pnl(current_price=10.5)
    assert pnl == 0.0  # At cost price


def test_position_with_price():
    position = Position(
        symbol="000001",
        quantity=100,
        avg_cost=10.5
    )
    mv = position.get_market_value(current_price=11.0)
    assert mv == 1100.0
    pnl = position.get_unrealized_pnl(current_price=11.0)
    assert pnl == pytest.approx(50.0)


def test_account_initialization():
    account = Account(
        initial_capital=100000.0,
        fee_rate=0.0003
    )
    assert account.cash == 100000.0
    assert len(account.positions) == 0


def test_account_update_with_buy():
    account = Account(initial_capital=100000.0, fee_rate=0.0003)
    account.update_cash(-10500.0)
    assert account.cash == pytest.approx(89500.0)


def test_account_get_position():
    account = Account(initial_capital=100000.0, fee_rate=0.0003)
    pos = account.get_position("000001")
    assert pos.symbol == "000001"
    assert pos.quantity == 0
