# -*- coding: utf-8 -*-
"""
英文支持功能演示脚本
展示系统如何处理英文输入查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import process_query, is_visualization_query
from language_utils import language_detector
from llm_client import SiliconFlow

def demo_english_queries():
    """演示英文查询处理"""
    print("=== 英文支持功能演示 ===")
    print("注意：以下演示需要配置有效的API密钥才能完整运行\n")
    
    # 测试查询列表
    test_queries = [
        # 英文可视化查询
        "Show me a chart of monthly sales trends",
        "Create a visualization for product performance",
        "Plot the revenue distribution by category",
        
        # 英文数据查询
        "What is the total sales amount?",
        "How many orders were placed last month?",
        "Show me the top selling products",
        
        # 英文普通对话
        "Hello, what can you do?",
        "Thank you for your help",
        "What are your capabilities?",
        
        # 中文查询（对比）
        "显示月度销售趋势图",
        "查询总销售额",
        "你好，你能做什么？"
    ]
    
    llm_client = SiliconFlow()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 查询: '{query}'")
        
        # 检测语言
        detected_language = language_detector.detect_language(query)
        print(f"   检测语言: {detected_language}")
        
        # 检测查询类型
        is_viz = is_visualization_query(query)
        print(f"   可视化查询: {is_viz}")
        
        # 检测对话类型（如果有API密钥）
        try:
            chat_type, response = llm_client.classify_and_respond(query)
            print(f"   对话类型: {chat_type}")
            if response:
                print(f"   回答: {response[:100]}...")
        except Exception as e:
            print(f"   对话分类失败: {str(e)[:50]}...")
        
        print("-" * 50)

def demo_language_switching():
    """演示语言切换功能"""
    print("\n=== 语言切换演示 ===")
    
    # 混合语言查询
    mixed_queries = [
        "Hello, 请显示销售图表",
        "Show me 月度趋势 chart",
        "可视化 sales data please"
    ]
    
    for query in mixed_queries:
        print(f"\n混合语言查询: '{query}'")
        detected_language = language_detector.detect_language(query)
        is_viz = is_visualization_query(query)
        print(f"检测语言: {detected_language}")
        print(f"可视化查询: {is_viz}")

def demo_keyword_detection():
    """演示关键词检测功能"""
    print("\n=== 关键词检测演示 ===")
    
    # 英文可视化关键词测试
    viz_keywords_test = [
        "visualize", "chart", "plot", "graph", "trend", "dashboard",
        "bar chart", "line chart", "pie chart", "scatter plot"
    ]
    
    print("\n英文可视化关键词检测:")
    for keyword in viz_keywords_test:
        test_query = f"Please {keyword} the sales data"
        is_viz = is_visualization_query(test_query)
        status = "✓" if is_viz else "✗"
        print(f"{status} '{test_query}' -> {is_viz}")
    
    # 英文普通对话关键词测试
    general_keywords_test = [
        "hello", "thank", "help", "what", "how", "who are you"
    ]
    
    print("\n英文普通对话关键词检测:")
    from language_utils import multilingual_keywords
    for keyword in general_keywords_test:
        test_query = f"{keyword} there"
        is_general = multilingual_keywords.is_general_conversation(test_query)
        status = "✓" if is_general else "✗"
        print(f"{status} '{test_query}' -> {is_general}")

if __name__ == "__main__":
    print("L'Oreal Insight Agent - 英文支持功能演示\n")
    
    demo_english_queries()
    demo_language_switching()
    demo_keyword_detection()
    
    print("\n演示完成！")
    print("\n功能总结:")
    print("✓ 支持英文语言检测")
    print("✓ 支持英文可视化关键词识别")
    print("✓ 支持英文普通对话识别")
    print("✓ 支持混合语言处理")
    print("✓ 支持多语言提示模板")
    print("✓ 保持向后兼容性（中文功能不受影响）")