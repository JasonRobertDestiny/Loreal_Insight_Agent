# 🎯 L'Oréal Insight Agent 

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.44.1-orange)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/JasonRobertDestiny/Loreal_Insight_Agent)](https://github.com/JasonRobertDestiny/Loreal_Insight_Agent/issues)
[![Stars](https://img.shields.io/github/stars/JasonRobertDestiny/Loreal_Insight_Agent)](https://github.com/JasonRobertDestiny/Loreal_Insight_Agent/stargazers)

**🚀 基于大语言模型的智能数据分析助手，专为企业数据洞察而设计**

[🎮 在线演示]([https://your-demo-link.com](https://www.modelscope.cn/studios/JasonRobert/loreal-insight-agent/files)) | [📖 文档](https://deepwiki.com/JasonRobertDestiny/Loreal_Insight_Agent) | [🤝 贡献指南](CONTRIBUTING.md)

</div>

## ✨ 核心特性

### 🎯 智能数据分析
- �️ **自然语言转SQL** - 用中文或英文直接询问数据
- 📊 **智能数据可视化** - 自动生成专业图表
- 🔍 **深度数据分析** - AI驱动的业务洞察
- 📝 **完整历史记录** - 查询历史管理和导出

### 🌍 用户体验
- 🌐 **多语言支持** - 完美支持中文/英文双语交互
- 🎨 **优雅UI设计** - 适配明暗主题，符合欧莱雅品牌风格
- 📱 **响应式界面** - 完美适配桌面和移动设备
- ⚡ **实时交互** - 即时查询反馈和错误提示

### 🔧 企业级特性
- 🔒 **安全可靠** - 环境变量管理，API密钥安全
- 📈 **性能优化** - 高效SQL执行和缓存机制
- 🔄 **易于扩展** - 模块化架构，支持多种数据源
- 📊 **丰富图表** - 柱状图、折线图、饼图、散点图等

## 🎯 适用场景

- 📈 **销售数据分析** - 产品销量、趋势分析
- �️ **市场洞察** - 消费者行为、偏好分析  
- 📊 **业务报表** - 自动化报表生成
- 🎨 **数据可视化** - 专业图表展示

## 🛠️ 技术架构

| 组件 | 技术栈 | 版本 |
|------|--------|------|
| **前端** | Gradio | 4.44.1 |
| **后端** | Python | 3.8+ |
| **AI模型** | Qwen/Qwen2.5-Coder-32B-Instruct | Latest |
| **数据库** | SQLite/MySQL/PostgreSQL | - |
| **可视化** | Matplotlib + Seaborn | Latest |
| **框架** | LangChain | 0.3.25 |

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/JasonRobertDestiny/Loreal_Insight_Agent.git
cd Loreal_Insight_Agent
```

### 2. 安装依赖
```bash
# 推荐使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量
创建 `.env` 文件并配置以下参数：
```env
API_KEY=your_api_key_here
BASE_URL=https://api.siliconflow.cn/v1
MODEL_NAME=Qwen/QwQ-32B
DATABASE_URL=sqlite:///data/order_database.db
DEBUG=False
LOG_LEVEL=INFO
```

### 4. 启动应用
```bash
python app.py
```

应用将在 `http://localhost:7860` 启动。

## 📖 使用说明

### 中文查询示例
- "显示各个渠道的销售额排名"
- "查询各省份的销售数据"
- "按终端名称统计订单数量"
- "最近一个月的销售趋势如何？"

### English Query Examples
- "Show sales ranking by channel"
- "Query sales data by province"
- "Count orders by terminal name"
- "What's the sales trend for the last month?"

### 可视化查询示例
- "可视化各省份的销售分布"
- "绘制各渠道的销售对比图"
- "显示材料销售的饼图"
- "Visualize sales distribution by province"
- "Create a comparison chart of sales by channel"
- "Show material sales pie chart"

## 📁 项目结构

```
Loreal_Insight_Agent/
├── app.py              # 主应用入口
├── text2sql.py         # SQL查询核心模块
├── text2viz.py         # 数据可视化模块
├── llm_client.py       # LLM客户端
├── config.py           # 配置管理
├── sql_logger.py       # SQL日志记录
├── utils.py            # 工具函数
├── exceptions.py       # 异常处理
├── requirements.txt    # 依赖包列表
├── INSTALL.md          # 详细安装说明
├── data/               # 数据文件
│   ├── data.csv
│   └── order_database.db
├── logs/               # 日志文件
└── viz_images/         # 生成的图表
```

## 🔧 高级配置

### 自定义数据库
修改 `config.py` 中的 `DATABASE_URL` 或在 `.env` 文件中设置：
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 更换LLM模型
在 `.env` 文件中配置：
```env
MODEL_NAME=gpt-4
BASE_URL=https://api.openai.com/v1
```

## 🐛 故障排除

详细的安装和故障排除指南请参考 [INSTALL.md](INSTALL.md)

## 📄 许可证

Apache License 2.0

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**注意**: 请确保在使用前正确配置API密钥和数据库连接。
