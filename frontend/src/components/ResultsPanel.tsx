import { useMemo } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Descriptions, Tabs } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, DollarOutlined, RiseOutlined } from '@ant-design/icons'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, ComposedChart, Bar, ReferenceLine, ReferenceArea } from 'recharts'
import { BacktestResult, Trade, OHLCV } from '../types'

interface ResultsPanelProps {
  result: BacktestResult
}

export default function ResultsPanel({ result }: ResultsPanelProps) {
  const klineDates = result.kline.map((k: OHLCV) => k.date)

  const equityData = result.equity_curve.map((value, index) => ({
    day: index + 1,
    date: klineDates[index] || `Day ${index + 1}`,
    value: Math.round(value * 100) / 100
  }))

  const calculateMaxDrawdownZone = () => {
    let maxDrawdown = 0
    let peakIndex = 0
    let troughIndex = 0

    for (let i = 0; i < equityData.length; i++) {
      for (let j = 0; j < i; j++) {
        const drawdown = (equityData[j].value - equityData[i].value) / equityData[j].value
        if (drawdown > maxDrawdown) {
          maxDrawdown = drawdown
          peakIndex = j
          troughIndex = i
        }
      }
    }
    return { maxDrawdown, peakIndex, troughIndex }
  }

  const drawdownZone = calculateMaxDrawdownZone()

  const peakDate = equityData[drawdownZone.peakIndex]?.date
  const troughDate = equityData[drawdownZone.troughIndex]?.date
  const peakValue = equityData[drawdownZone.peakIndex]?.value
  const troughValue = equityData[drawdownZone.troughIndex]?.value

  const tradeColumns = [
    {
      title: '序号',
      dataIndex: 'trade_id',
      key: 'trade_id',
      width: 60
    },
    {
      title: '入场日期',
      dataIndex: 'entry_date',
      key: 'entry_date'
    },
    {
      title: '入场价格',
      dataIndex: 'entry_price',
      key: 'entry_price',
      render: (price: number) => `¥${price.toFixed(2)}`
    },
    {
      title: '出场日期',
      dataIndex: 'exit_date',
      key: 'exit_date'
    },
    {
      title: '出场价格',
      dataIndex: 'exit_price',
      key: 'exit_price',
      render: (price: number) => `¥${price.toFixed(2)}`
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (qty: number) => qty.toLocaleString()
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (pnl: number) => (
        <span style={{ color: pnl >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}
        </span>
      )
    },
    {
      title: '收益率',
      dataIndex: 'pnl_rate',
      key: 'pnl_rate',
      render: (rate: number) => (
        <Tag color={rate >= 0 ? 'green' : 'red'}>
          {rate >= 0 ? '+' : ''}{(rate * 100).toFixed(2)}%
        </Tag>
      )
    },
    {
      title: '触发条件',
      dataIndex: 'reason',
      key: 'reason',
      width: 200,
      ellipsis: true
    }
  ]

  const klineWithTrades = useMemo(() => {
    const kline = result.kline.map((k: OHLCV, index: number) => ({
      ...k,
      day: index,
      isUp: k.close >= k.open,
      body: k.close - k.open,
      shadow: Math.max(k.high - k.close, k.open - k.low)
    }))

    const buySignals = new Set(result.trades.map((t: Trade) => t.entry_date))
    const sellSignals = new Set(result.trades.map((t: Trade) => t.exit_date))

    return kline.map((k: any) => ({
      ...k,
      hasBuy: buySignals.has(k.date),
      hasSell: sellSignals.has(k.date)
    }))
  }, [result.kline, result.trades])

  const buyPoints = useMemo(() => {
    return result.trades.map((t: Trade) => ({
      date: t.entry_date,
      price: t.entry_price,
      day: result.kline.findIndex((k: OHLCV) => k.date === t.entry_date)
    })).filter(p => p.day >= 0)
  }, [result.trades, result.kline])

  const sellPoints = useMemo(() => {
    return result.trades.map((t: Trade) => ({
      date: t.exit_date,
      price: t.exit_price,
      day: result.kline.findIndex((k: OHLCV) => k.date === t.exit_date)
    })).filter(p => p.day >= 0)
  }, [result.trades, result.kline])

  const KLineChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={klineWithTrades}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={Math.floor(klineWithTrades.length / 10)} />
        <YAxis yAxisId="price" domain={['auto', 'auto']} />
        <YAxis yAxisId="volume" orientation="right" />
        <RechartsTooltip
          formatter={(value: any, name: string) => {
            if (name === '资产') return [`¥${value.toFixed(2)}`, name];
            if (name === '买入') return [`¥${value.toFixed(2)}`, name];
            if (name === '卖出') return [`¥${value.toFixed(2)}`, name];
            return [value, name];
          }}
          labelFormatter={(label) => `日期: ${label}`}
        />
        <Legend />
        <Bar yAxisId="volume" dataKey="volume" fill="#f0f0f0" opacity={0.5} />
        <Line yAxisId="price" type="monotone" dataKey="close" stroke="#1890ff" dot={false} name="收盘价" />
        <Line yAxisId="price" type="monotone" dataKey="open" stroke="transparent" dot={false} />
        <Line yAxisId="price" type="monotone" dataKey="high" stroke="transparent" dot={false} />
        <Line yAxisId="price" type="monotone" dataKey="low" stroke="transparent" dot={false} />
        {buyPoints.map((p: any, i: number) => (
          <ReferenceLine
            key={`buy-${i}`}
            yAxisId="price"
            y={p.price}
            stroke="#52c41a"
            strokeDasharray="5 5"
            label={{ value: '买入', position: 'insideTopRight', fill: '#52c41a', fontSize: 12 }}
          />
        ))}
        {sellPoints.map((p: any, i: number) => (
          <ReferenceLine
            key={`sell-${i}`}
            yAxisId="price"
            y={p.price}
            stroke="#ff4d4f"
            strokeDasharray="5 5"
            label={{ value: '卖出', position: 'insideBottomRight', fill: '#ff4d4f', fontSize: 12 }}
          />
        ))}
      </ComposedChart>
    </ResponsiveContainer>
  )

  const EquityChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={equityData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={Math.floor(equityData.length / 10)} />
        <YAxis />
        <RechartsTooltip
          formatter={(value: number) => [`¥${value.toFixed(2)}`, '资产']}
          labelFormatter={(label) => `日期: ${label}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="value"
          stroke="#1890ff"
          name="资产"
          dot={false}
        />
        {drawdownZone.maxDrawdown > 0 && (
          <>
            <ReferenceLine x={equityData[drawdownZone.peakIndex]?.date} stroke="#52c41a" strokeDasharray="3 3" label={{ value: '峰值', position: 'top', fill: '#52c41a', fontSize: 11 }} />
            <ReferenceLine x={equityData[drawdownZone.troughIndex]?.date} stroke="#ff4d4f" strokeDasharray="3 3" label={{ value: '谷值', position: 'bottom', fill: '#ff4d4f', fontSize: 11 }} />
            <ReferenceArea x1={equityData[drawdownZone.peakIndex]?.date} x2={equityData[drawdownZone.troughIndex]?.date} strokeOpacity={0.3} fill="#ff4d4f" fillOpacity={0.1} />
          </>
        )}
      </LineChart>
    </ResponsiveContainer>
  )

  const tabItems = [
    {
      key: 'kline',
      label: 'K线图',
      children: (
        <div>
          <KLineChart />
          {result.trades.length > 0 && (
            <Card title="交易详情" size="small" style={{ marginTop: 16 }}>
              <Table
                dataSource={result.trades}
                columns={tradeColumns}
                rowKey="trade_id"
                pagination={{ pageSize: 5 }}
                size="small"
                expandable={{
                  expandedRowRender: (record: Trade) => (
                    <div style={{ padding: '8px 0' }}>
                      <p><strong>触发条件:</strong> {record.reason || '无'}</p>
                      <p><strong>手续费:</strong> ¥{record.commission.toFixed(2)}</p>
                      <p><strong>入场金额:</strong> ¥{(record.entry_price * record.quantity).toFixed(2)}</p>
                      <p><strong>出场金额:</strong> ¥{(record.exit_price * record.quantity).toFixed(2)}</p>
                    </div>
                  )
                }}
              />
            </Card>
          )}
        </div>
      )
    },
    {
      key: 'equity',
      label: '资金曲线',
      children: <EquityChart />
    }
  ]

  return (
    <>
      <Card title="回测结果" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="总收益率"
              value={result.total_return * 100}
              precision={2}
              suffix="%"
              valueStyle={{ color: result.total_return >= 0 ? '#52c41a' : '#ff4d4f' }}
              prefix={result.total_return >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="最终资产"
              value={result.final_value}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="夏普比率"
              value={result.sharpe_ratio}
              precision={2}
              prefix={<RiseOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="最大回撤"
              value={result.max_drawdown * 100}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Col>
        </Row>

        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col span={6}>
            <Statistic
              title="交易次数"
              value={result.total_trades}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="胜率"
              value={result.win_rate * 100}
              precision={2}
              suffix="%"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="年化收益率"
              value={result.metrics.annual_return * 100}
              precision={2}
              suffix="%"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="盈亏比"
              value={result.metrics.profit_loss_ratio}
              precision={2}
            />
          </Col>
        </Row>
      </Card>

      <Row gutter={24} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="图表分析">
            <Tabs items={tabItems} />
          </Card>
          <Card title="最大回撤详情" size="small" style={{ marginTop: 16 }}>
            <Descriptions column={2} size="small">
              <Descriptions.Item label="回撤率">{(drawdownZone.maxDrawdown * 100).toFixed(2)}%</Descriptions.Item>
              <Descriptions.Item label="峰值日期">{peakDate}</Descriptions.Item>
              <Descriptions.Item label="峰值金额">¥{peakValue?.toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="谷值日期">{troughDate}</Descriptions.Item>
              <Descriptions.Item label="谷值金额">¥{troughValue?.toLocaleString()}</Descriptions.Item>
            </Descriptions>
            <p style={{ color: '#888', fontSize: 12, marginTop: 8 }}>
              最大回撤期间在资金曲线图中以红色区域标注
            </p>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="策略信息">
            <Descriptions column={1}>
              <Descriptions.Item label="股票代码">{result.symbol}</Descriptions.Item>
              <Descriptions.Item label="策略名称">{result.strategy_name}</Descriptions.Item>
              <Descriptions.Item label="起始日期">{result.start_date}</Descriptions.Item>
              <Descriptions.Item label="结束日期">{result.end_date}</Descriptions.Item>
              <Descriptions.Item label="初始资金">¥{result.initial_capital.toLocaleString()}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </>
  )
}
