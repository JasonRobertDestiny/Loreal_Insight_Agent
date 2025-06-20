# 安装指南

本文档提供了 L'Oreal Insight Agent 的详细安装说明和常见问题解决方案。

## 系统要求

- Python 3.8 或更高版本
- pip 包管理器
- 足够的磁盘空间（约 500MB 用于依赖包）

## 快速安装

### 方法1: 使用自动安装脚本（推荐）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd Loreal_Insight_Agent
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **运行自动安装脚本**
   ```bash
   python install_dependencies.py
   ```

### 方法2: 手动安装

1. **升级基础工具**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

## 问题诊断

您遇到的numpy安装错误是由于GCC编译器版本过低导致的。numpy 1.26.2需要GCC >= 8.4，但您的系统使用的是GCC 4.9.2。

## 解决方案

### 方案1：使用兼容版本（推荐）

我们已经更新了requirements.txt，使用兼容的numpy版本：

```bash
pip install -r requirements.txt
```

### 方案2：使用开发版本依赖

如果仍有问题，使用更灵活的版本要求：

```bash
pip install -r requirements-dev.txt
```

### 方案3：使用预编译包

对于Windows用户，可以使用预编译的二进制包：

```bash
pip install --only-binary=numpy numpy
pip install -r requirements.txt
```

### 方案4：升级编译环境

如果您需要最新版本的numpy，可以考虑：

1. **安装Visual Studio Build Tools**（Windows推荐）：
   - 下载并安装 Visual Studio Build Tools
   - 选择C++构建工具

2. **使用conda环境**：
   ```bash
   conda create -n loreal python=3.10
   conda activate loreal
   conda install numpy pandas matplotlib
   pip install -r requirements.txt
   ```

## 验证安装

安装完成后，运行测试脚本验证：

```bash
python api_test.py
```

如果API测试成功，启动主应用：

```bash
python app.py
```

## 常见问题解决方案

### 1. setuptools 兼容性问题

**错误信息：**
```
AttributeError: module 'pkgutil' has no attribute 'ImpImporter'
```

**解决方案：**

**选项 A: 使用自动安装脚本（推荐）**
```bash
python install_dependencies.py
```

**选项 B: 手动修复**
```bash
# 升级基础工具
python -m pip install --upgrade pip setuptools wheel

# 安装预编译的NumPy
pip install --only-binary=all numpy

# 然后安装其他依赖
pip install -r requirements.txt
```

**选项 C: 使用conda环境**
```bash
conda create -n loreal python=3.9
conda activate loreal
conda install numpy pandas matplotlib
pip install -r requirements.txt
```

### 2. NumPy 安装失败（GCC 版本问题）

**错误信息：**
```
ERROR: Could not build wheels for numpy
NumPy requires GCC >= 8.4
```

**解决方案：**

**选项 A: 使用兼容版本（推荐）**
```bash
pip install -r requirements-dev.txt
```

**选项 B: 安装预编译包**
```bash
# Windows 用户
pip install --only-binary=all numpy

# 或者使用 conda
conda install numpy
```

**选项 C: 升级编译环境**
- 升级 GCC 到 8.4 或更高版本
- 或者使用更新的 Python 发行版

## 常见问题

### Q: 仍然遇到编译错误？
A: 尝试使用conda环境或预编译包

### Q: API调用失败？
A: 检查.env文件中的API_KEY是否正确

### Q: 界面无法启动？
A: 确保所有依赖都已正确安装

## 技术支持

如果遇到其他问题，请检查：
1. Python版本是否为3.10.x
2. 网络连接是否正常
3. API密钥是否有效