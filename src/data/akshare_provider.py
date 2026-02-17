import akshare as ak
from datetime import date as date_type
from typing import Optional
from src.models.ohlcv import OHLCV, BarData


class AkshareProvider:
    def fetch_stock_daily(
        self,
        symbol: str,
        start_date: date_type,
        end_date: date_type,
        adjustment: str = "qfq"
    ) -> BarData:
        try:
            if adjustment == "qfq":
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust="qfq"
                )
            elif adjustment == "hfq":
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust="hfq"
                )
            else:
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust=""
                )
            
            bars = []
            for _, row in df.iterrows():
                bar = OHLCV(
                    symbol=symbol,
                    trade_date=row["日期"],
                    open_price=row["开盘"],
                    high_price=row["最高"],
                    low_price=row["最低"],
                    close_price=row["收盘"],
                    volume=row["成交量"],
                    turnover=row["成交额"],
                    adjustment=adjustment
                )
                bars.append(bar)
            
            return BarData(
                symbol=symbol,
                bars=bars,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            raise ConnectionError(f"获取股票数据失败: {e}")
    
    def get_stock_info(self, symbol: str) -> dict:
        try:
            df = ak.stock_info_a_code_name()
            row = df[df["code"] == symbol]
            if row.empty:
                return {"name": symbol, "market": "unknown"}
            return {
                "name": row["name"].iloc[0],
                "market": row["market"].iloc[0] if "market" in row.columns else "A股"
            }
        except Exception:
            return {"name": symbol, "market": "unknown"}
    
    def search_stocks(self, keyword: str) -> list[dict]:
        try:
            df = ak.stock_info_a_code_name()
            filtered = df[df["name"].str.contains(keyword) | df["code"].str.contains(keyword)]
            return [
                {"code": row["code"], "name": row["name"]}
                for _, row in filtered.head(20).iterrows()
            ]
        except Exception:
            return []
