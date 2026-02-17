import httpx
import json
from datetime import date


def test_api():
    base_url = "http://localhost:8000"
    
    # Test health check
    resp = httpx.get(f"{base_url}/health")
    print(f"Health check: {resp.json()}")
    
    # Test strategies list
    resp = httpx.get(f"{base_url}/api/v1/strategies")
    print(f"Strategies: {resp.json()}")
    
    # Test stock search
    resp = httpx.get(f"{base_url}/api/v1/stocks/search", params={"keyword": "平安"})
    print(f"Stock search: {resp.json()}")
    
    # Test backtest
    backtest_data = {
        "symbol": "000001",
        "strategy": "ma_cross",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "initial_capital": 100000.0,
        "fee_rate": 0.0003,
        "adjustment": "qfq",
        "params": {
            "short_window": 5,
            "long_window": 20
        }
    }
    resp = httpx.post(f"{base_url}/api/v1/backtest", json=backtest_data)
    result = resp.json()
    if result["success"]:
        print(f"Backtest success!")
        print(f"  Total return: {result['result']['total_return']:.2%}")
        print(f"  Final value: ¥{result['result']['final_value']:,.2f}")
        print(f"  Total trades: {result['result']['total_trades']}")
        print(f"  Win rate: {result['result']['win_rate']:.2%}")
    else:
        print(f"Backtest failed: {result['error']}")


if __name__ == "__main__":
    test_api()
