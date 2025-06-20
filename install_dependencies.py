#!/usr/bin/env python3
"""
依赖安装脚本
解决NumPy和其他依赖的安装问题
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"\n正在执行: {description}")
    print(f"命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ 成功: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 失败: {description}")
        print(f"错误输出: {e.stderr}")
        return False

def upgrade_pip_setuptools():
    """升级pip和setuptools"""
    commands = [
        ("python -m pip install --upgrade pip", "升级pip"),
        ("pip install --upgrade setuptools wheel", "升级setuptools和wheel"),
        ("pip install --upgrade pip setuptools wheel", "再次确保升级")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"警告: {description} 失败，继续尝试其他方法")

def install_numpy_precompiled():
    """安装预编译的NumPy"""
    commands = [
        ("pip install --only-binary=all numpy", "安装预编译NumPy"),
        ("pip install numpy --force-reinstall --no-deps", "强制重装NumPy"),
    ]
    
    for command, description in commands:
        if run_command(command, description):
            return True
    return False

def install_requirements():
    """安装requirements.txt中的依赖"""
    # 先尝试安装核心依赖
    core_packages = [
        "gradio==5.29.1",
        "pandas==2.2.3",
        "matplotlib==3.10.3",
        "openai==1.79.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0"
    ]
    
    print("\n=== 安装核心依赖 ===")
    for package in core_packages:
        run_command(f"pip install {package}", f"安装 {package}")
    
    # 然后安装LangChain相关
    langchain_packages = [
        "langchain-core==0.3.60",
        "langchain==0.3.25",
        "langchain-community==0.3.24"
    ]
    
    print("\n=== 安装LangChain依赖 ===")
    for package in langchain_packages:
        run_command(f"pip install {package}", f"安装 {package}")

def main():
    """主安装流程"""
    print("L'Oreal Insight Agent 依赖安装脚本")
    print("=" * 50)
    
    # 步骤1: 升级基础工具
    print("\n步骤1: 升级pip和setuptools")
    upgrade_pip_setuptools()
    
    # 步骤2: 安装NumPy
    print("\n步骤2: 安装NumPy")
    if not install_numpy_precompiled():
        print("NumPy安装失败，请手动安装或使用conda")
        print("建议命令:")
        print("  conda install numpy")
        print("  或者")
        print("  pip install numpy --no-build-isolation")
    
    # 步骤3: 安装其他依赖
    print("\n步骤3: 安装其他依赖")
    install_requirements()
    
    # 步骤4: 验证安装
    print("\n步骤4: 验证安装")
    try:
        import numpy
        import pandas
        import gradio
        import matplotlib
        print("✓ 核心依赖验证成功")
        
        # 显示版本信息
        print(f"NumPy版本: {numpy.__version__}")
        print(f"Pandas版本: {pandas.__version__}")
        print(f"Gradio版本: {gradio.__version__}")
        
    except ImportError as e:
        print(f"✗ 依赖验证失败: {e}")
        print("请检查安装日志并手动安装失败的包")
    
    print("\n安装完成！")
    print("如果仍有问题，请参考 INSTALL.md 文件")

if __name__ == "__main__":
    main()