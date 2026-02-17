import { Card, Row, Col, Statistic, Table, Tag, Descriptions } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, DollarOutlined, RiseOutlined } from '@ant-design/icons'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { BacktestResult, Trade } from '../types'

interface ResultsPanelProps {
  result: BacktestResult
}

export default function ResultsPanel({ result }: ResultsPanelProps) {
  const equityData = result.equity_curve.map((value, index) => ({
    day: index + 1,
    value: Math.round(value * 100) / 100
  }))

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
          <Card title="资金曲线">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={equityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip formatter={(value: number) => [`¥${value.toFixed(2)}`, '资产']} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#1890ff"
                  name="资产"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
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

      {result.trades.length > 0 && (
        <Card title="交易记录" style={{ marginBottom: 24 }}>
          <Table
            dataSource={result.trades}
            columns={tradeColumns}
            rowKey="trade_id"
            pagination={{ pageSize: 10 }}
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
    </>
  )
}
