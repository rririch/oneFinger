from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    return_rate: float = Field(..., description="总收益率")
    annual_return: float = Field(..., description="年化收益率")
    volatility: float = Field(..., description="波动率")
    sharpe_ratio: float = Field(..., description="夏普比率")
    max_drawdown: float = Field(..., description="最大回撤")
    win_rate: float = Field(..., description="胜率")
    profit_loss_ratio: float = Field(..., description="盈亏比")


class TradeRecord(BaseModel):
    trade_id: str = Field(..., description="交易ID")
    symbol: str = Field(..., description="股票代码")
    entry_date: date = Field(..., description="入场日期")
    entry_price: float = Field(..., description="入场价格")
    exit_date: date = Field(..., description="出场日期")
    exit_price: float = Field(..., description="出场价格")
    quantity: int = Field(..., description="数量")
    pnl: float = Field(..., description="盈亏")
    pnl_rate: float = Field(..., description="盈亏比例")
    side: str = Field(..., description="方向")
    commission: float = Field(default=0.0, description="手续费")
    reason: str = Field(default="", description="触发条件")


class BacktestResult(BaseModel):
    symbol: str = Field(..., description="股票代码")
    strategy_name: str = Field(..., description="策略名称")
    start_date: date = Field(..., description="回测起始日期")
    end_date: date = Field(..., description="回测结束日期")
    initial_capital: float = Field(..., description="初始资金")
    final_value: float = Field(..., description="最终资产")
    total_return: float = Field(..., description="总收益率")
    metrics: PerformanceMetrics = Field(..., description="性能指标")
    total_trades: int = Field(..., description="总交易次数")
    win_rate: float = Field(..., description="胜率")
    sharpe_ratio: float = Field(..., description="夏普比率")
    max_drawdown: float = Field(..., description="最大回撤")
    trades: list[TradeRecord] = Field(default_factory=list, description="交易记录")
    equity_curve: list[float] = Field(default_factory=list, description="资金曲线")
