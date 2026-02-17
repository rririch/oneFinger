from typing import Dict, Optional
from pydantic import BaseModel, Field


class Position(BaseModel):
    symbol: str = Field(..., description="股票代码")
    quantity: int = Field(default=0, ge=0, description="持仓数量")
    avg_cost: float = Field(default=0.0, ge=0, description="平均成本")
    
    def get_market_value(self, current_price: float = 0.0) -> float:
        return self.quantity * current_price
    
    def get_unrealized_pnl(self, current_price: float = 0.0) -> float:
        if self.quantity > 0:
            return (current_price - self.avg_cost) * self.quantity
        return 0.0


class Account(BaseModel):
    initial_capital: float = Field(..., gt=0)
    fee_rate: float = Field(default=0.0003, ge=0, le=0.01)
    cash: float = Field(default=0.0)
    positions: Dict[str, Position] = Field(default_factory=dict)
    frozen_cash: float = Field(default=0.0)
    total_commission: float = Field(default=0.0)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.cash = self.initial_capital
    
    @property
    def total_value(self) -> float:
        return self.cash
    
    def update_cash(self, amount: float):
        self.cash += amount
    
    def get_position(self, symbol: str) -> Position:
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        return self.positions[symbol]
