# oneFinger 项目开发指南

本项目是 A 股交易策略回测工具，采用前后端分离架构。后端使用 Python + FastAPI，前端使用 React + TypeScript + Vite。

---

## 一、构建与测试命令

### 1.1 Python 后端

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/strategy/test_rsi.py

# 运行单个测试函数
pytest tests/strategy/test_rsi.py::test_rsi_oversold_golden_cross

# 代码格式化
black src/ tests/

# 代码检查
ruff check src/ tests/

# 类型检查
mypy src/
```

### 1.2 前端

```bash
# 安装依赖
cd frontend && npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

### 1.3 启动完整项目

```bash
# 启动后端 (在项目根目录)
uvicorn src.main:app --reload

# 启动前端 (在 frontend 目录)
npm run dev
```

---

## 二、代码风格指南

### 2.1 Python 代码规范

#### 导入规范
- 标准库导入放在顶部
- 第三方库导入在标准库之后
- 本地模块导入使用相对路径，如 `from src.models.ohlcv import OHLCV`
- 分组之间用空行分隔

```python
from abc import ABC, abstractmethod
from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from src.models.ohlcv import BarData
```

#### 类型注解
- 使用 Python 标准 `typing` 模块
- 优先使用具体类型而非 `Any`
- 使用 `Optional[T]` 而非 `Union[T, None]`

#### 命名规范
- 类名：`PascalCase`（如 `RSIStrategy`、`Order`）
- 函数/变量：`snake_case`（如 `generate_signals`、`backtest_result`）
- 常量：`UPPER_SNAKE_CASE`（如 `DEFAULT_FEE_RATE`）
- 私有成员：前缀下划线（如 `_internal_state`）

#### Pydantic 模型
- 所有模型必须继承 `BaseModel`
- 使用 `Field` 定义字段，包含 `description` 参数
- 使用 `Enum` 定义枚举类型
- 数值字段添加验证（如 `gt=0`、`ge=0`）
- 在模型中使用 `@property` 定义计算属性

```python
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class Order(BaseModel):
    symbol: str = Field(..., description="股票代码")
    quantity: int = Field(..., gt=0, description="数量")
    price: Optional[float] = Field(None, ge=0, description="限价")

    @property
    def is_market_order(self) -> bool:
        return self.order_type == OrderType.MARKET
```

#### 抽象类
- 使用 `abc.ABC` 和 `@abstractmethod`
- 策略类必须继承 `Strategy` 抽象基类

```python
class Strategy(ABC):
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}

    @abstractmethod
    def generate_signals(self, data: BarData) -> list[Signal]:
        pass
```

#### 错误处理
- 使用自定义异常类
- 捕获具体异常而非通用 `Exception`
- 记录关键错误信息

### 2.2 TypeScript 代码规范

#### 导入规范
- React 相关导入在最前
- 第三方库次之
- 本地模块最后
- 保持一行一个导入

```typescript
import { useState, useEffect } from 'react'
import { Form, DatePicker, Select } from 'antd'
import { PlayCircleOutlined } from '@ant-design/icons'
import { BacktestParams } from '../types'
import axios from 'axios'
```

#### 类型定义
- 使用 TypeScript 接口定义组件 props
- 启用严格模式（`strict: true`）
- 避免使用 `any`，使用具体类型或 `unknown`
- 使用泛型提高代码复用性

```typescript
interface BacktestFormProps {
  onSubmit: (params: BacktestParams) => void
  loading: boolean
}

export default function BacktestForm({ onSubmit, loading }: BacktestFormProps) {
  // 组件实现
}
```

#### 命名规范
- 组件：`PascalCase`（如 `BacktestForm`）
- 函数/变量：`camelCase`（如 `handleSubmit`、`stockResults`）
- 常量：`UPPER_SNAKE_CASE` 或 `camelCase`（如 `API_BASE_URL`）

#### 组件设计
- 使用函数组件和 Hooks
- props 类型单独定义在组件上方
- 保持组件职责单一
- 使用解构赋值获取 props

#### Ant Design 使用
- 使用中文标签和提示信息
- 表单验证规则清晰明确
- 组件布局合理使用 `Space`、`Card` 等容器

---

## 三、目录结构

```
oneFinger/
├── src/                    # 后端源码
│   ├── api/               # FastAPI 路由
│   ├── core/              # 核心引擎
│   ├── data/              # 数据提供者
│   ├── models/            # 数据模型
│   ├── strategy/          # 策略实现
│   └── main.py            # 应用入口
├── tests/                  # 测试用例
│   ├── api/
│   ├── core/
│   ├── data/
│   ├── models/
│   └── strategy/
├── frontend/              # 前端源码
│   ├── src/
│   │   ├── components/    # React 组件
│   │   ├── types.ts       # 类型定义
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── pyproject.toml
└── requirements.txt
```

---

## 四、开发注意事项

1. **后端端口**: 8000，API 前缀 `/api/v1/`
2. **前端端口**: 3000，代理 `/api` 到后端
3. **Python 版本**: >= 3.11
4. **测试覆盖**: 新功能需添加对应测试用例
5. **代码质量**: 提交前运行 `black`、`ruff`、`mypy`
6. **类型安全**: 避免使用 `any`，保持类型推断准确
