from datetime import date as date_type
from typing import Optional
from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    symbol: str = Field(..., description="股票代码")
    trade_date: date_type = Field(..., description="交易日期")
    open_price: float = Field(..., ge=0, description="开盘价")
    high_price: float = Field(..., ge=0, description="最高价")
    low_price: float = Field(..., ge=0, description="最低价")
    close_price: float = Field(..., ge=0, description="收盘价")
    volume: int = Field(..., ge=0, description="成交量")
    turnover: float = Field(..., ge=0, description="成交额")
    adjustment: str = Field(default="qfq", description="复权类型")
    
    @property
    def price_range(self) -> float:
        return self.high_price - self.low_price
    
    @property
    def is_up(self) -> bool:
        return self.close_price >= self.open_price


class BarData(BaseModel):
    symbol: str = Field(..., description="股票代码")
    bars: list[OHLCV] = Field(default_factory=list, description="K线数据列表")
    start_date: Optional[date_type] = Field(None, description="起始日期")
    end_date: Optional[date_type] = Field(None, description="结束日期")
    
    @property
    def total_bars(self) -> int:
        return len(self.bars)
    
    def __len__(self) -> int:
        return self.total_bars
    
    def __getitem__(self, index: int) -> OHLCV:
        return self.bars[index]
