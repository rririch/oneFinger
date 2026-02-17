from abc import ABC, abstractmethod
from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.models.ohlcv import BarData


class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class Signal(BaseModel):
    symbol: str = Field(..., description="股票代码")
    signal_type: SignalType = Field(..., description="信号类型")
    price: float = Field(..., description="信号价格")
    timestamp: date = Field(..., description="信号时间")
    strength: float = Field(default=1.0, ge=0, le=1.0, description="信号强度")
    reason: Optional[str] = Field(None, description="信号原因")


class Strategy(ABC):
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}
    
    @abstractmethod
    def generate_signals(self, data: BarData) -> list[Signal]:
        pass
    
    def validate_params(self) -> bool:
        return True
