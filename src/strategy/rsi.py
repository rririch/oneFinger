import pandas as pd
from typing import Optional
from src.strategy.base import Strategy, Signal, SignalType
from src.models.ohlcv import BarData


class RSIStrategy(Strategy):
    def __init__(
        self,
        period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        position_ratio: float = 1.0
    ):
        super().__init__(
            name="rsi",
            params={
                "period": period,
                "oversold": oversold,
                "overbought": overbought,
                "position_ratio": position_ratio
            }
        )
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.position_ratio = position_ratio
        self._previous_rsi: Optional[float] = None
    
    def generate_signals(self, data: BarData) -> list[Signal]:
        if len(data.bars) < self.period:
            return []
        
        closes = [float(bar.close_price) for bar in data.bars]
        df = pd.DataFrame({"close": closes})
        
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        df["rsi"] = rsi
        
        signals = []
        for i, row in df.iterrows():
            if pd.isna(row["rsi"]):
                continue
            
            curr_rsi = float(row["rsi"])
            
            if self._previous_rsi is not None:
                prev_rsi = self._previous_rsi
                
                if prev_rsi <= self.oversold and curr_rsi > self.oversold:
                    signals.append(Signal(
                        symbol=data.symbol,
                        signal_type=SignalType.BUY,
                        price=data.bars[i].close_price,
                        timestamp=data.bars[i].trade_date,
                        strength=self.position_ratio,
                        reason=f"RSI超卖金叉: RSI({curr_rsi:.2f})上穿{self.oversold}"
                    ))
                elif prev_rsi >= self.overbought and curr_rsi < self.overbought:
                    signals.append(Signal(
                        symbol=data.symbol,
                        signal_type=SignalType.SELL,
                        price=data.bars[i].close_price,
                        timestamp=data.bars[i].trade_date,
                        strength=self.position_ratio,
                        reason=f"RSI超买死叉: RSI({curr_rsi:.2f})下穿{self.overbought}"
                    ))
            
            self._previous_rsi = curr_rsi
        
        return signals
