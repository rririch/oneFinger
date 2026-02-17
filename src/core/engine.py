from datetime import datetime
from typing import Optional
import numpy as np
from src.strategy.base import Strategy, SignalType
from src.models.ohlcv import BarData
from src.models.order import Order, OrderSide, OrderType, Trade
from src.models.account import Account, Position
from src.models.result import BacktestResult, PerformanceMetrics, TradeRecord


class BacktestEngine:
    def __init__(
        self,
        initial_capital: float = 100000.0,
        fee_rate: float = 0.0003,
        slippage: float = 0.0
    ):
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self.slippage = slippage
        self.account: Optional[Account] = None
        self.trades: list[Trade] = []
        self.equity_curve: list[float] = []
        self.completed_trades: list[TradeRecord] = []
        self.open_trades: dict[str, dict] = {}
    
    def run(self, data: BarData, strategy: Strategy) -> BacktestResult:
        self.account = Account(
            initial_capital=self.initial_capital,
            fee_rate=self.fee_rate
        )
        self.trades = []
        self.completed_trades = []
        self.open_trades = {}
        self.equity_curve = [self.initial_capital]
        
        signals = strategy.generate_signals(data)
        signals_by_date = {}
        for signal in signals:
            date_key = signal.timestamp.isoformat()
            if date_key not in signals_by_date:
                signals_by_date[date_key] = []
            signals_by_date[date_key].append(signal)
        
        for bar in data.bars:
            date_key = bar.trade_date.isoformat()
            day_signals = signals_by_date.get(date_key, [])
            
            for signal in day_signals:
                if signal.signal_type == SignalType.BUY:
                    self._execute_buy(bar, signal)
                elif signal.signal_type == SignalType.SELL:
                    self._execute_sell(bar, signal)
            
            current_price = bar.close_price
            total_value = self.account.cash + self._calculate_positions_value(current_price)
            self.equity_curve.append(total_value)
        
        self._close_all_positions(data.bars[-1])
        result = self._build_result(data, strategy)
        return result
    
    def _calculate_positions_value(self, current_price: float) -> float:
        total = 0.0
        for symbol, pos in self.open_trades.items():
            total += pos["quantity"] * current_price
        return total
    
    def _execute_buy(self, bar, signal):
        symbol = signal.symbol
        price = signal.price * (1 + self.slippage)

        max_quantity = int(self.account.cash / price * signal.strength * 0.95)
        quantity = (max_quantity // 100) * 100
        quantity = quantity if quantity >= 100 else 0

        if quantity <= 0:
            return

        commission = price * quantity * self.fee_rate
        total_cost = price * quantity + commission
        if self.account.cash >= total_cost:
            self.account.cash -= total_cost
            self.account.total_commission += commission

            if symbol not in self.open_trades:
                self.open_trades[symbol] = {
                    "quantity": 0,
                    "avg_cost": 0,
                    "entries": [],
                    "reason": signal.reason,
                    "position_ratio": signal.strength
                }

            pos = self.open_trades[symbol]
            pos["entries"].append({
                "price": price,
                "quantity": quantity,
                "date": bar.trade_date,
                "reason": signal.reason,
                "position_ratio": signal.strength
            })

            total_shares = pos["quantity"] + quantity
            total_cost_basis = pos["quantity"] * pos["avg_cost"] + price * quantity
            pos["quantity"] = total_shares
            pos["avg_cost"] = total_cost_basis / total_shares if total_shares > 0 else 0
    
    def _execute_sell(self, bar, signal):
        symbol = signal.symbol
        if symbol not in self.open_trades or self.open_trades[symbol]["quantity"] == 0:
            return

        pos = self.open_trades[symbol]

        price = signal.price * (1 - self.slippage)
        target_quantity = int(pos["quantity"] * signal.strength)
        sell_quantity = (target_quantity // 100) * 100
        sell_quantity = min(sell_quantity, pos["quantity"])
        sell_quantity = sell_quantity if sell_quantity >= 100 else pos["quantity"]

        if sell_quantity <= 0:
            return

        remaining_quantity = sell_quantity
        entry_price_sum = 0
        total_commission = 0
        position_ratio = signal.strength

        for entry in list(pos["entries"]):
            if remaining_quantity <= 0:
                break

            entry_quantity = min(entry["quantity"], remaining_quantity)
            entry_commission = entry["price"] * entry_quantity * self.fee_rate

            sell_commission = price * sell_quantity * self.fee_rate

            entry_value = entry["price"] * entry_quantity
            sell_value = price * entry_quantity
            pnl = sell_value - entry_value - entry_commission - sell_commission
            pnl_rate = pnl / entry_value if entry_value > 0 else 0

            position_decision = (
                f"仓位管理: position_ratio={position_ratio:.2f}, "
                f"目标卖出={int(pos['quantity'] * position_ratio)}股, "
                f"实际成交={sell_quantity}股(100股整数倍), "
                f"卖出比例={position_ratio*100:.1f}%"
            )

            self.completed_trades.append(TradeRecord(
                trade_id=f"t{len(self.completed_trades) + 1}",
                symbol=symbol,
                entry_date=entry["date"],
                entry_price=entry["price"],
                exit_date=bar.trade_date,
                exit_price=price,
                quantity=entry_quantity,
                pnl=round(pnl, 2),
                pnl_rate=round(pnl_rate, 4),
                side="long",
                commission=round(entry_commission + sell_commission, 2),
                reason=f"{signal.reason or entry.get('reason', '')} | {position_decision}",
                position_ratio=position_ratio,
                avg_cost=entry["price"]
            ))

            entry_price_sum += entry["price"] * entry_quantity
            total_commission += entry_commission + sell_commission
            remaining_quantity -= entry_quantity

            entry["quantity"] -= entry_quantity
            if entry["quantity"] <= 0:
                pos["entries"].remove(entry)

        commission = price * sell_quantity * self.fee_rate
        self.account.cash += price * sell_quantity - commission
        self.account.total_commission += commission

        pos["quantity"] -= sell_quantity
        pos["avg_cost"] = self._calculate_avg_cost(pos)

        position_decision = (
            f"仓位管理: position_ratio={signal.strength:.2f}, "
            f"当前持仓={pos['quantity'] + sell_quantity}股, "
            f"卖出比例={signal.strength*100:.1f}%, "
            f"实际卖出={sell_quantity}股(取整到100的倍数)"
        )

        for entry in list(pos["entries"]):
            entry["position_decision"] = position_decision

    def _calculate_avg_cost(self, pos: dict) -> float:
        if pos["quantity"] <= 0:
            return 0
        total_cost = sum(e["price"] * e["quantity"] for e in pos["entries"])
        return total_cost / pos["quantity"]
    
    def _close_all_positions(self, bar):
        for symbol, pos in list(self.open_trades.items()):
            if pos["quantity"] > 0:
                price = bar.close_price * (1 - self.slippage)
                remaining = pos["quantity"]

                position_decision = (
                    f"仓位管理: 回测结束强制平仓, "
                    f"剩余持仓={remaining}股, "
                    f"以收盘价{price:.2f}全部卖出"
                )

                for entry in list(pos["entries"]):
                    entry_commission = entry["price"] * entry["quantity"] * self.fee_rate
                    sell_commission = price * entry["quantity"] * self.fee_rate

                    entry_value = entry["price"] * entry["quantity"]
                    sell_value = price * entry["quantity"]
                    pnl = sell_value - entry_value - entry_commission - sell_commission
                    pnl_rate = pnl / entry_value if entry_value > 0 else 0

                    self.completed_trades.append(TradeRecord(
                        trade_id=f"t{len(self.completed_trades) + 1}",
                        symbol=symbol,
                        entry_date=entry["date"],
                        entry_price=entry["price"],
                        exit_date=bar.trade_date,
                        exit_price=price,
                        quantity=entry["quantity"],
                        pnl=round(pnl, 2),
                        pnl_rate=round(pnl_rate, 4),
                        side="long",
                        commission=round(entry_commission + sell_commission, 2),
                        reason=position_decision,
                        position_ratio=1.0,
                        avg_cost=entry["price"]
                    ))

                    remaining -= entry["quantity"]

                pos["quantity"] = 0
                pos["entries"] = []
    
    def _build_result(self, data: BarData, strategy: Strategy) -> BacktestResult:
        final_value = self.equity_curve[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        trades = self.completed_trades
        wins = sum(1 for t in trades if t.pnl > 0)
        win_rate = wins / len(trades) if trades else 0.0
        
        returns_series = self._calculate_returns()
        annual_return, volatility, sharpe = self._calculate_risk_metrics(returns_series)
        max_drawdown = self._calculate_max_drawdown()
        
        metrics = PerformanceMetrics(
            return_rate=total_return,
            annual_return=annual_return,
            volatility=volatility,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_loss_ratio=self._calculate_profit_loss_ratio(trades)
        )
        
        return BacktestResult(
            symbol=data.symbol,
            strategy_name=strategy.name,
            start_date=data.start_date or data.bars[0].trade_date,
            end_date=data.end_date or data.bars[-1].trade_date,
            initial_capital=self.initial_capital,
            final_value=final_value,
            total_return=total_return,
            metrics=metrics,
            total_trades=len(trades),
            win_rate=win_rate,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            trades=trades,
            equity_curve=self.equity_curve
        )
    
    def _calculate_returns(self) -> list[float]:
        returns = []
        for i in range(1, len(self.equity_curve)):
            ret = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            returns.append(ret)
        return returns
    
    def _calculate_risk_metrics(self, returns: list[float]):
        if not returns:
            return 0.0, 0.0, 0.0
        
        annual_factor = 252
        mean_return = np.mean(returns) * annual_factor
        std_return = np.std(returns) * (annual_factor ** 0.5)
        sharpe = mean_return / std_return if std_return > 0 else 0.0
        
        return mean_return, std_return, sharpe
    
    def _calculate_max_drawdown(self) -> float:
        if not self.equity_curve:
            return 0.0
        
        max_drawdown = 0.0
        peak = self.equity_curve[0]
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def _calculate_profit_loss_ratio(self, trades: list[TradeRecord]) -> float:
        profits = [t.pnl for t in trades if t.pnl > 0]
        losses = [abs(t.pnl) for t in trades if t.pnl < 0]
        
        avg_profit = sum(profits) / len(profits) if profits else 0
        avg_loss = sum(losses) / len(losses) if losses else 1
        
        return avg_profit / avg_loss if avg_loss > 0 else 0.0
