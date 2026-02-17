export interface OHLCV {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  turnover?: number
}

export interface Trade {
  trade_id: string
  entry_date: string
  entry_price: number
  exit_date: string
  exit_price: number
  quantity: number
  pnl: number
  pnl_rate: number
  side: string
  commission: number
  reason: string
}

export interface BacktestResult {
  symbol: string
  strategy_name: string
  start_date: string
  end_date: string
  initial_capital: number
  final_value: number
  total_return: number
  total_trades: number
  win_rate: number
  sharpe_ratio: number
  max_drawdown: number
  metrics: {
    return_rate: number
    annual_return: number
    volatility: number
    sharpe_ratio: number
    max_drawdown: number
    win_rate: number
    profit_loss_ratio: number
  }
  equity_curve: number[]
  kline: OHLCV[]
  trades: Trade[]
}

export interface BacktestParams {
  symbol: string
  strategy: string
  start_date: string
  end_date: string
  initial_capital: number
  fee_rate: number
  adjustment: string
  params?: Record<string, any>
}
