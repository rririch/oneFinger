import { useState } from 'react'
import { Layout, Typography, message } from 'antd'
import BacktestForm from './components/BacktestForm'
import ResultsPanel from './components/ResultsPanel'
import { BacktestResult } from './types'

const { Header, Content } = Layout
const { Title } = Typography

function App() {
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleBacktest = async (params: any) => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      const data = await response.json()
      if (data.success) {
        setResult(data.result)
        message.success('回测完成')
      } else {
        message.error(data.error || '回测失败')
      }
    } catch (error) {
      message.error('请求失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <Title level={3} style={{ color: 'white', margin: 0 }}>oneFinger 回测工具</Title>
      </Header>
      <Content style={{ padding: '24px' }}>
        <BacktestForm onSubmit={handleBacktest} loading={loading} />
        {result && <ResultsPanel result={result} />}
      </Content>
    </Layout>
  )
}

export default App
