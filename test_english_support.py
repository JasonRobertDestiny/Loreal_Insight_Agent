# -*- coding: utf-8 -*-
"""
英文支持功能测试脚本
测试语言检测、关键词匹配和多语言提示模板功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from language_utils import language_detector, multilingual_keywords, multilingual_prompts
from text2sql import Text2SQL
from llm_client import SiliconFlow

def test_language_detection():
    """测试语言检测功能"""
    print("=== 测试语言检测功能 ===")
    
    test_cases = [
        ("你好，请帮我分析销售数据", "zh"),
        ("Hello, can you help me analyze sales data?", "en"),
        ("Show me the sales trend chart", "en"),
        ("可视化销售趋势图", "zh"),
        ("Hello 你好，混合语言测试", "mixed"),
        ("123456", "zh")  # 默认返回中文
    ]
    
    for text, expected in test_cases:
        detected = language_detector.detect_language(text)
        status = "✓" if detected == expected else "✗"
        print(f"{status} 文本: '{text}' -> 检测结果: {detected} (期望: {expected})")
    print()

def test_visualization_keywords():
    """测试可视化关键词检测"""
    print("=== 测试可视化关键词检测 ===")
    
    test_cases = [
        ("请帮我可视化销售数据", True),
        ("Show me a chart of sales trends", True),
        ("Create a visualization for monthly revenue", True),
        ("Plot the data distribution", True),
        ("你好，我是谁？", False),
        ("Hello, who are you?", False),
        ("查询销售总额", False),
        ("What is the total sales?", False)
    ]
    
    for text, expected in test_cases:
        result = multilingual_keywords.is_visualization_query(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 文本: '{text}' -> 结果: {result} (期望: {expected})")
    print()

def test_general_conversation_keywords():
    """测试普通对话关键词检测"""
    print("=== 测试普通对话关键词检测 ===")
    
    test_cases = [
        ("你好", True),
        ("Hello", True),
        ("Thank you", True),
        ("What can you do?", True),
        ("查询销售数据", False),
        ("Show me sales data", False),
        ("可视化趋势图", False)
    ]
    
    for text, expected in test_cases:
        result = multilingual_keywords.is_general_conversation(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 文本: '{text}' -> 结果: {result} (期望: {expected})")
    print()

def test_prompt_templates():
    """测试提示模板获取"""
    print("=== 测试提示模板获取 ===")
    
    # 测试SQL回答提示模板
    zh_sql_prompt = multilingual_prompts.get_sql_answer_prompt('zh')
    en_sql_prompt = multilingual_prompts.get_sql_answer_prompt('en')
    
    print("中文SQL提示模板:")
    print(zh_sql_prompt[:100] + "...")
    print()
    
    print("英文SQL提示模板:")
    print(en_sql_prompt[:100] + "...")
    print()
    
    # 测试对话分类提示模板
    zh_classify_prompt = multilingual_prompts.get_classify_prompt('zh')
    en_classify_prompt = multilingual_prompts.get_classify_prompt('en')
    
    print("中文分类提示模板:")
    print(zh_classify_prompt[:100] + "...")
    print()
    
    print("英文分类提示模板:")
    print(en_classify_prompt[:100] + "...")
    print()

def test_integration():
    """集成测试 - 测试完整的英文查询流程"""
    print("=== 集成测试 ===")
    
    # 测试英文可视化查询检测
    english_viz_queries = [
        "Show me a chart of monthly sales",
        "Create a visualization for product categories",
        "Plot the sales trend over time",
        "Display a bar chart of revenue by region"
    ]
    
    print("英文可视化查询检测:")
    for query in english_viz_queries:
        is_viz = multilingual_keywords.is_visualization_query(query)
        language = language_detector.detect_language(query)
        print(f"查询: '{query}'")
        print(f"  语言: {language}, 可视化: {is_viz}")
    print()
    
    # 测试英文普通对话检测
    english_general_queries = [
        "Hello, what can you do?",
        "Thank you for your help",
        "Who are you?",
        "What are your capabilities?"
    ]
    
    print("英文普通对话检测:")
    for query in english_general_queries:
        is_general = multilingual_keywords.is_general_conversation(query)
        language = language_detector.detect_language(query)
        print(f"查询: '{query}'")
        print(f"  语言: {language}, 普通对话: {is_general}")
    print()

if __name__ == "__main__":
    print("开始测试英文支持功能...\n")
    
    test_language_detection()
    test_visualization_keywords()
    test_general_conversation_keywords()
    test_prompt_templates()
    test_integration()
    
    print("测试完成！")