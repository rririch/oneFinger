import pytest
from datetime import datetime
from src.models.order import Order, OrderSide, OrderType, Trade


def test_order_creation():
    order = Order(
        symbol="000001",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100,
        price=10.5,
        timestamp=datetime(2024, 1, 2, 9, 30, 0)
    )
    assert order.side == OrderSide.BUY
    assert order.quantity == 100
    assert order.is_buy is True


def test_trade_from_order():
    order = Order(
        symbol="000001",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100,
        price=10.5,
        timestamp=datetime(2024, 1, 2, 9, 30, 0)
    )
    trade = Trade(
        order=order,
        executed_price=10.52,
        executed_quantity=100,
        commission=3.15,
        timestamp=datetime(2024, 1, 2, 9, 30, 5)
    )
    assert trade.executed_price == 10.52
    assert trade.gross_value == pytest.approx(1052.0)


def test_order_is_market_order():
    market_order = Order(
        symbol="000001",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100,
        price=None,
        timestamp=datetime(2024, 1, 2, 9, 30, 0)
    )
    assert market_order.is_market_order is True

    limit_order = Order(
        symbol="000001",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=100,
        price=11.0,
        timestamp=datetime(2024, 1, 2, 9, 30, 0)
    )
    assert limit_order.is_market_order is False
