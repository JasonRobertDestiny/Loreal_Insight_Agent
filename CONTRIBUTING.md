# 贡献指南 Contributing Guide

感谢你对 L'Oréal Insight Agent 项目的关注！我们欢迎任何形式的贡献。

## 🤝 如何贡献

### 报告问题 Issues
- 使用我们的 [Issue 模板](https://github.com/JasonRobertDestiny/Loreal_Insight_Agent/issues/new/choose)
- 详细描述问题，包括复现步骤
- 提供运行环境信息（Python版本、操作系统等）

### 功能建议 Feature Requests
- 在 Issues 中提出功能建议
- 描述使用场景和预期效果
- 如果可能，提供设计草图或原型

### 代码贡献 Pull Requests

#### 开发环境设置
```bash
# 1. Fork 并克隆仓库
git clone https://github.com/JasonRobertDestiny/Loreal_Insight_Agent.git
cd Loreal_Insight_Agent

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 设置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的 API_KEY

# 5. 初始化数据库
python init_memory_db.py

# 6. 运行测试
python test_basic.py
```

#### 开发流程
1. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释和文档字符串
   - 确保代码通过测试

3. **测试**
   ```bash
   # 运行基础测试
   python test_basic.py
   
   # 测试英文支持
   python test_english_support.py
   
   # 测试历史记录功能
   python test_history_recording.py
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 代码规范

### Python 代码风格
- 使用 4 个空格缩进
- 遵循 PEP 8 标准
- 函数和类使用 docstring 文档
- 变量和函数使用描述性命名

### 提交信息格式
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Type:**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建或工具相关

**例子:**
```
feat(ui): 添加深色主题支持

- 实现主题切换功能
- 优化深色模式下的文字可见性
- 添加主题状态持久化

Closes #123
```

## 🧪 测试要求

### 单元测试
- 新功能必须包含相应的测试用例
- 确保测试覆盖率不降低
- 测试文件命名为 `test_*.py`

### 集成测试
- 测试与数据库的交互
- 测试API调用功能
- 测试UI组件的集成

## 📚 文档要求

- 更新相关文档（README.md、INSTALL.md等）
- 为新功能添加使用示例
- 更新API文档（如适用）

## 🔒 安全注意事项

- 不要在代码中硬编码API密钥或敏感信息
- 使用环境变量管理配置
- 注意SQL注入和XSS攻击防护

## 📦 发布流程

1. 更新版本号（setup.py, requirements.txt）
2. 更新 CHANGELOG.md
3. 创建 release tag
4. 发布到相应平台

## 🆘 获得帮助

- 📧 邮箱：johnrobertdestiny@gmail.com
- 💬 讨论：[GitHub Issues](https://github.com/JasonRobertDestiny/Loreal_Insight_Agent/issues)
- 📖 文档：[项目文档](https://deepwiki.com/JasonRobertDestiny/Loreal_Insight_Agent)

## 📄 许可证

通过贡献代码，你同意你的贡献将在 [MIT License](LICENSE) 下授权。

---

再次感谢你的贡献！🎉
