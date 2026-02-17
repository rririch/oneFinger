import { useState, useEffect } from 'react'
import { Form, DatePicker, Select, InputNumber, Button, Card, Space, message, Collapse } from 'antd'
import { PlayCircleOutlined } from '@ant-design/icons'
import { BacktestParams } from '../types'
import axios from 'axios'

const { Option } = Select
const { Panel } = Collapse

interface BacktestFormProps {
  onSubmit: (params: BacktestParams) => void
  loading: boolean
}

export default function BacktestForm({ onSubmit, loading }: BacktestFormProps) {
  const [form] = Form.useForm()
  const [strategies, setStrategies] = useState<any[]>([])
  const [stockResults, setStockResults] = useState<any[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<string>('')

  useEffect(() => {
    fetchStrategies()
  }, [])

  const fetchStrategies = async () => {
    try {
      const response = await axios.get('/api/v1/strategies')
      setStrategies(response.data.strategies || [])
    } catch (error) {
      message.error('获取策略列表失败')
    }
  }

  const searchStocks = async (keyword: string) => {
    if (!keyword) {
      setStockResults([])
      return
    }
    try {
      const response = await axios.get('/api/v1/stocks/search', { params: { keyword } })
      setStockResults(response.data.results || [])
    } catch (error) {
      message.error('搜索股票失败')
    }
  }

  const handleStrategyChange = (value: string) => {
    setSelectedStrategy(value)
    // 重置策略参数
    if (value === 'ma_cross') {
      form.setFieldsValue({ shortWindow: 5, longWindow: 20 })
    } else if (value === 'rsi') {
      form.setFieldsValue({ rsiPeriod: 14, rsiOversold: 30, rsiOverbought: 70 })
    }
  }

  const handleSubmit = async (values: any) => {
    let strategyParams = {}
    
    if (values.strategy === 'ma_cross') {
      strategyParams = {
        short_window: values.shortWindow || 5,
        long_window: values.longWindow || 20
      }
    } else if (values.strategy === 'rsi') {
      strategyParams = {
        period: values.rsiPeriod || 14,
        oversold: values.rsiOversold || 30,
        overbought: values.rsiOverbought || 70
      }
    }

    const params: BacktestParams = {
      symbol: values.symbol?.split(' ')[0] || values.symbol,
      strategy: values.strategy,
      start_date: values.dateRange[0].format('YYYY-MM-DD'),
      end_date: values.dateRange[1].format('YYYY-MM-DD'),
      initial_capital: values.initialCapital || 100000,
      fee_rate: values.feeRate || 0.0003,
      adjustment: values.adjustment || 'qfq',
      params: strategyParams
    }
    onSubmit(params)
  }

  const renderStrategyParams = () => {
    if (selectedStrategy === 'ma_cross') {
      return (
        <Space wrap>
          <Form.Item label="短期均线" name="shortWindow" initialValue={5}>
            <InputNumber min={2} max={60} style={{ width: 80 }} />
          </Form.Item>
          <Form.Item label="长期均线" name="longWindow" initialValue={20}>
            <InputNumber min={5} max={120} style={{ width: 80 }} />
          </Form.Item>
        </Space>
      )
    } else if (selectedStrategy === 'rsi') {
      return (
        <Space wrap>
          <Form.Item label="RSI周期" name="rsiPeriod" initialValue={14}>
            <InputNumber min={2} max={50} style={{ width: 80 }} />
          </Form.Item>
          <Form.Item label="超卖线" name="rsiOversold" initialValue={30}>
            <InputNumber min={10} max={50} style={{ width: 80 }} />
          </Form.Item>
          <Form.Item label="超买线" name="rsiOverbought" initialValue={70}>
            <InputNumber min={50} max={90} style={{ width: 80 }} />
          </Form.Item>
        </Space>
      )
    }
    return null
  }

  return (
    <Card title="回测配置" style={{ marginBottom: 24 }}>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item label="股票代码" name="symbol" rules={[{ required: true, message: '请输入股票代码' }]}>
          <Select
            showSearch
            placeholder="输入股票代码或名称搜索"
            defaultActiveFirstOption={false}
            showArrow={false}
            filterOption={false}
            onSearch={searchStocks}
            notFoundContent={stockResults.length > 0 ? (
              <ul style={{ margin: 0, padding: '8px 12px', listStyle: 'none' }}>
                {stockResults.map((stock: any) => (
                  <li
                    key={stock.code}
                    style={{ padding: '4px 0', cursor: 'pointer' }}
                    onClick={() => {
                      form.setFieldsValue({ symbol: `${stock.code} ${stock.name}` })
                      setStockResults([])
                    }}
                  >
                    <strong>{stock.code}</strong> {stock.name}
                  </li>
                ))}
              </ul>
            ) : null}
          >
            {stockResults.map((stock: any) => (
              <Option key={stock.code} value={`${stock.code} ${stock.name}`}>
                {stock.code} - {stock.name}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item label="交易策略" name="strategy" rules={[{ required: true, message: '请选择策略' }]}>
          <Select placeholder="选择交易策略" onChange={handleStrategyChange}>
            {strategies.map((s: any) => (
              <Option key={s.id} value={s.id}>{s.name}</Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item label="回测时间段" name="dateRange" rules={[{ required: true, message: '请选择时间范围' }]}>
          <DatePicker.RangePicker style={{ width: '100%' }} />
        </Form.Item>

        <Collapse defaultActiveKey={['basic']} ghost>
          <Panel header="基本设置" key="basic">
            <Space wrap>
              <Form.Item label="初始资金" name="initialCapital" initialValue={100000}>
                <InputNumber min={10000} step={10000} formatter={(value) => `¥ ${value}`} style={{ width: 150 }} />
              </Form.Item>

              <Form.Item label="手续费率" name="feeRate" initialValue={0.0003}>
                <InputNumber min={0} max={0.01} step={0.0001} precision={4} style={{ width: 120 }} />
              </Form.Item>

              <Form.Item label="复权方式" name="adjustment" initialValue="qfq">
                <Select style={{ width: 100 }}>
                  <Option value="qfq">前复权</Option>
                  <Option value="hfq">后复权</Option>
                  <Option value="none">不复权</Option>
                </Select>
              </Form.Item>
            </Space>
          </Panel>

          <Panel header="策略参数" key="strategy">
            {renderStrategyParams()}
          </Panel>
        </Collapse>

        <Form.Item style={{ marginTop: 16 }}>
          <Button type="primary" htmlType="submit" icon={<PlayCircleOutlined />} loading={loading} size="large">
            运行回测
          </Button>
        </Form.Item>
      </Form>
    </Card>
  )
}
