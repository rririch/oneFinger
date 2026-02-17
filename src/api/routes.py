from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import date
from pydantic import BaseModel
import logging

from src.data.akshare_provider import AkshareProvider
from src.strategy.ma_cross import MACrossStrategy
from src.strategy.rsi import RSIStrategy
from src.core.engine import BacktestEngine

logger = logging.getLogger(__name__)

router = APIRouter()
data_provider = AkshareProvider()


class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    start_date: date
    end_date: date
    initial_capital: float = 100000.0
    fee_rate: float = 0.0003
    adjustment: str = "qfq"
    params: Optional[dict] = None


class BacktestResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@router.get("/strategies")
async def list_strategies():
    return {
        "strategies": [
            {"id": "ma_cross", "name": "均线交叉策略", "params": ["short_window", "long_window", "position_ratio"]},
            {"id": "rsi", "name": "RSI策略(14周期,30/70)", "params": ["period", "oversold", "overbought", "position_ratio"]},
        ]
    }


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    try:
        data = data_provider.fetch_stock_daily(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            adjustment=request.adjustment
        )
        
        if request.strategy == "ma_cross":
            params = request.params or {}
            strategy = MACrossStrategy(
                short_window=params.get("short_window", 5),
                long_window=params.get("long_window", 20),
                position_ratio=params.get("position_ratio", 1.0)
            )
        elif request.strategy == "rsi":
            params = request.params or {}
            strategy = RSIStrategy(
                period=params.get("period", 14),
                oversold=params.get("oversold", 30.0),
                overbought=params.get("overbought", 70.0),
                position_ratio=params.get("position_ratio", 1.0)
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy}")
        
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            fee_rate=request.fee_rate
        )
        
        result = engine.run(data, strategy)
        
        return BacktestResponse(
            success=True,
            result={
                "symbol": result.symbol,
                "strategy_name": result.strategy_name,
                "start_date": str(result.start_date),
                "end_date": str(result.end_date),
                "initial_capital": result.initial_capital,
                "final_value": result.final_value,
                "total_return": result.total_return,
                "total_trades": result.total_trades,
                "win_rate": result.win_rate,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "metrics": result.metrics.model_dump(),
                "equity_curve": result.equity_curve,
                "trades": [t.model_dump() for t in result.trades]
            }
        )
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        return BacktestResponse(success=False, error=str(e))


@router.get("/stock/{symbol}")
async def get_stock_info(symbol: str):
    info = data_provider.get_stock_info(symbol)
    return info


@router.get("/stocks/search")
async def search_stocks(keyword: str):
    results = data_provider.search_stocks(keyword)
    return {"results": results}
