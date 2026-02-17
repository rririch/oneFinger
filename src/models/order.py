from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class Order(BaseModel):
    symbol: str = Field(..., description="股票代码")
    side: OrderSide = Field(..., description="买卖方向")
    order_type: OrderType = Field(..., description="订单类型")
    quantity: int = Field(..., gt=0, description="数量")
    price: Optional[float] = Field(None, ge=0, description="限价")
    timestamp: datetime = Field(..., description="下单时间")
    signal_id: Optional[str] = Field(None, description="信号ID")
    
    @property
    def is_buy(self) -> bool:
        return self.side == OrderSide.BUY
    
    @property
    def is_market_order(self) -> bool:
        return self.order_type == OrderType.MARKET


class Trade(BaseModel):
    order: Order = Field(..., description="源订单")
    executed_price: float = Field(..., ge=0, description="成交价格")
    executed_quantity: int = Field(..., gt=0, description="成交数量")
    commission: float = Field(..., ge=0, description="手续费")
    timestamp: datetime = Field(..., description="成交时间")
    
    @property
    def gross_value(self) -> float:
        return self.executed_price * self.executed_quantity
    
    @property
    def net_value(self) -> float:
        if self.order.is_buy:
            return self.gross_value + self.commission
        else:
            return self.gross_value - self.commission
