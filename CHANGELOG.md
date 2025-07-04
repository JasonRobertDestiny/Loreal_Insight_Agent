# 更新日志 Changelog

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 支持更多数据库类型（MySQL, PostgreSQL）
- 添加数据导出功能
- 增强图表定制选项
- 用户权限管理系统

## [1.2.0] - 2025-06-23

### 新增
- ✨ 完整的历史记录系统
  - 查询历史保存和管理
  - 历史记录搜索和过滤
  - 历史数据导出功能
- 🎨 深色主题完全支持
  - 明暗主题切换
  - 优化深色模式文字可见性
  - 主题状态持久化
- 🌐 增强的多语言支持
  - 完善中英文切换
  - 优化翻译质量
  - 添加更多示例查询

### 改进
- 🔧 优化LLM客户端错误处理
- 📊 增强数据可视化功能
- 🚀 提升应用性能和稳定性
- 📱 改进移动端适配

### 修复
- 🐛 修复深色主题下文字不可见问题
- 🐛 修复历史记录保存失败的问题
- 🐛 修复多语言切换时的显示异常

## [1.1.0] - 2025-06-21

### 新增
- 🌍 英文支持完整实现
- 📝 添加详细的英文文档
- 🔧 环境变量配置优化
- 🧪 完善的测试套件

### 改进
- 🎨 UI界面优化
- 📊 图表生成算法改进
- ⚡ 查询性能提升

## [1.0.0] - 2025-06-20

### 新增
- 🎯 初始版本发布
- 🗣️ 自然语言转SQL功能
- 📊 数据可视化系统
- 🎨 Gradio Web界面
- 🔍 基础查询功能
- 📝 SQL日志记录

### 技术栈
- Python 3.8+
- Gradio 4.44.1
- LangChain 0.3.25
- Matplotlib + Seaborn
- SQLite 数据库

---

## 版本说明

- **[Unreleased]**: 正在开发中的功能
- **[X.Y.Z]**: 已发布的版本
  - **X**: 主版本号（重大变更）
  - **Y**: 次版本号（新功能）
  - **Z**: 修订版本号（问题修复）

## 变更类型

- `新增` - 新功能
- `改进` - 现有功能的改进
- `修复` - 问题修复
- `移除` - 移除的功能
- `安全` - 安全相关更新
- `弃用` - 即将移除的功能
