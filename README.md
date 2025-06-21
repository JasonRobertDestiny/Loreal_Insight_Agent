---
# L'Oreal Insight Agent 🚀

一个基于大语言模型的智能数据分析工具，支持自然语言查询数据库和自动生成可视化图表。

## ✨ 主要功能

- 🔍 **多语言自然语言转SQL**: 支持中英文查询数据库，自动生成并执行SQL语句
- 📊 **智能数据可视化**: 根据查询意图自动生成图表（柱状图、折线图、饼图等）
- 🌐 **双语支持**: 完整支持中文和英文界面及查询
- 🎨 **美观的Web界面**: 基于Gradio构建的现代化用户界面
- 🔧 **灵活配置**: 支持多种LLM模型和数据库连接
- 📝 **完整日志**: 详细的SQL执行日志和错误追踪

## 🛠️ 技术栈

- **前端**: Gradio 5.29.1
- **后端**: Python 3.8+
- **AI模型**: 支持OpenAI API兼容的模型（默认使用Qwen/QwQ-32B）
- **数据库**: SQLite（可扩展支持其他数据库）
- **可视化**: Matplotlib + Seaborn
- **框架**: LangChain

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/JasonRobertDestiny/text2sql.git
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