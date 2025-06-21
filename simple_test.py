# -*- coding: utf-8 -*-
from language_utils import language_detector, multilingual_keywords

print("=== 英文支持功能测试 ===")

# 测试语言检测
print("\n1. 语言检测测试:")
test_texts = [
    "Hello, show me sales data",
    "你好，显示销售数据",
    "Create a chart please"
]

for text in test_texts:
    lang = language_detector.detect_language(text)
    print(f"'{text}' -> {lang}")

# 测试可视化关键词
print("\n2. 可视化关键词测试:")
viz_tests = [
    "Show me a chart",
    "Create visualization",
    "Plot the data",
    "显示图表",
    "Hello there"
]

for text in viz_tests:
    is_viz = multilingual_keywords.is_visualization_query(text)
    print(f"'{text}' -> 可视化: {is_viz}")

print("\n测试完成！")