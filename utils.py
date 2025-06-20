"""工具函数模块

提供通用的工具函数，提高代码复用性和可维护性。
"""

import os
import re
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory: str) -> None:
    """确保目录存在，如果不存在则创建"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def is_visualization_query(query: str) -> bool:
    """检测查询是否是可视化请求
    
    Args:
        query: 用户查询字符串
        
    Returns:
        bool: 是否为可视化查询
    """
    viz_keywords = [
        "可视化", "图表", "图形", "绘制", "画图", "展示", "趋势", "变化", 
        "统计图", "柱状图", "折线图", "饼图", "直方图", "散点图", "分布图",
        "visualize", "visualization", "chart", "plot", "graph", "trend", "变化情况"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in viz_keywords)

def clean_sql_query(sql_response: str) -> str:
    """清洗SQL响应，移除前缀和格式化
    
    Args:
        sql_response: 原始SQL响应
        
    Returns:
        str: 清洗后的SQL查询
    """
    if "SQLQuery:" in sql_response:
        return sql_response.split("SQLQuery:", 1)[1].strip()
    elif "SELECT" in sql_response.upper():
        start_idx = sql_response.upper().find("SELECT")
        return sql_response[start_idx:].strip()
    
    logger.warning(f"无法清洗SQL响应: {sql_response[:100]}...")
    return sql_response.strip()

def format_data_summary(df: pd.DataFrame) -> str:
    """生成数据摘要信息
    
    Args:
        df: 数据框
        
    Returns:
        str: 格式化的数据摘要
    """
    if df.empty:
        return "无法生成数据可视化，请尝试其他查询。"
    
    summary = "以下是查询结果的可视化：\n\n"
    summary += f"数据包含 {len(df)} 行记录。\n"
    
    for col in df.columns:
        if pd.api.types.is_datetime64_dtype(df[col]):
            summary += f"• {col} 范围: {df[col].min().date()} 到 {df[col].max().date()}\n"
        elif pd.api.types.is_numeric_dtype(df[col]):
            summary += f"• {col} 统计: 总和={df[col].sum():.2f}, 平均值={df[col].mean():.2f}\n"
    
    return summary

def extract_column_names_from_sql(sql_query: str) -> List[str]:
    """从SQL查询中提取列名
    
    Args:
        sql_query: SQL查询语句
        
    Returns:
        List[str]: 列名列表
    """
    column_names = []
    
    # 使用正则表达式匹配SELECT子句
    matches = re.findall(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE)
    if matches:
        cols = matches[0].split(',')
        for col in cols:
            col = col.strip()
            if ' AS ' in col.upper():
                # 提取别名
                alias = col.split(' AS ', 1)[1].strip().strip('"')
                column_names.append(alias)
            else:
                # 提取列名（去除表前缀）
                name = col.strip().split('.')[-1].strip('"')
                column_names.append(name)
    
    return column_names

def safe_convert_to_numeric(series: pd.Series) -> pd.Series:
    """安全地将Series转换为数值类型
    
    Args:
        series: pandas Series
        
    Returns:
        pd.Series: 转换后的Series
    """
    try:
        # 检查是否为数值格式
        sample_values = series.dropna().head(5).astype(str)
        numeric_pattern = r'^-?\d+(\.\d+)?$'
        
        if sample_values.str.match(numeric_pattern).all():
            return pd.to_numeric(series, errors='coerce')
    except Exception as e:
        logger.warning(f"数值转换失败: {e}")
    
    return series

def safe_convert_to_datetime(series: pd.Series) -> pd.Series:
    """安全地将Series转换为日期类型
    
    Args:
        series: pandas Series
        
    Returns:
        pd.Series: 转换后的Series
    """
    try:
        sample_values = series.dropna().head(5).astype(str)
        date_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}'
        
        if sample_values.str.match(date_pattern).any():
            return pd.to_datetime(series, errors='coerce')
    except Exception as e:
        logger.warning(f"日期转换失败: {e}")
    
    return series

def generate_timestamp_filename(prefix: str = "viz", extension: str = "png") -> str:
    """生成带时间戳的文件名
    
    Args:
        prefix: 文件名前缀
        extension: 文件扩展名
        
    Returns:
        str: 生成的文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def validate_dataframe_for_visualization(df: pd.DataFrame) -> Tuple[bool, str]:
    """验证DataFrame是否适合可视化
    
    Args:
        df: 数据框
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if df.empty:
        return False, "数据框为空"
    
    if len(df.columns) < 2:
        return False, "数据列数不足（需要至少2列）"
    
    # 检查是否有数值列
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) == 0:
        return False, "没有找到数值类型的列"
    
    return True, ""

def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."