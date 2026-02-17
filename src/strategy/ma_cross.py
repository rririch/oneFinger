import pandas as pd
from typing import Optional
from src.strategy.base import Strategy, Signal, SignalType
from src.models.ohlcv import BarData


class MACrossStrategy(Strategy):
    def __init__(
        self,
        short_window: int = 5,
        long_window: int = 20,
        position_ratio: float = 1.0
    ):
        super().__init__(
            name="ma_cross",
            params={
                "short_window": short_window,
                "long_window": long_window,
                "position_ratio": position_ratio
            }
        )
        self.short_window = short_window
        self.long_window = long_window
        self.position_ratio = position_ratio
        self._previous_short_ma: Optional[float] = None
        self._previous_long_ma: Optional[float] = None
    
    def generate_signals(self, data: BarData) -> list[Signal]:
        if len(data.bars) < self.long_window:
            return []
        
        closes = [float(bar.close_price) for bar in data.bars]
        df = pd.DataFrame({"close": closes})
        df["short_ma"] = df["close"].rolling(window=self.short_window).mean()
        df["long_ma"] = df["close"].rolling(window=self.long_window).mean()
        
        signals = []
        for i, row in df.iterrows():
            if pd.isna(row["short_ma"]) or pd.isna(row["long_ma"]):
                continue
            
            if self._previous_short_ma is not None and self._previous_long_ma is not None:
                prev_short = self._previous_short_ma
                curr_short = float(row["short_ma"])
                curr_long = float(row["long_ma"])
                
                if prev_short <= self._previous_long_ma and curr_short > curr_long:
                    signals.append(Signal(
                        symbol=data.symbol,
                        signal_type=SignalType.BUY,
                        price=data.bars[i].close_price,
                        timestamp=data.bars[i].trade_date,
                        strength=self.position_ratio,
                        reason=f"金叉: 短期MA({curr_short:.2f})上穿长期MA({curr_long:.2f})"
                    ))
                elif prev_short >= self._previous_long_ma and curr_short < curr_long:
                    signals.append(Signal(
                        symbol=data.symbol,
                        signal_type=SignalType.SELL,
                        price=data.bars[i].close_price,
                        timestamp=data.bars[i].trade_date,
                        strength=self.position_ratio,
                        reason=f"死叉: 短期MA({curr_short:.2f})下穿长期MA({curr_long:.2f})"
                    ))
            
            self._previous_short_ma = float(row["short_ma"])
            self._previous_long_ma = float(row["long_ma"])
        
        return signals
