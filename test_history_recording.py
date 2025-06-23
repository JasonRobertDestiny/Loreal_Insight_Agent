#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试历史记录保存功能
"""

import sys
sys.path.append('.')

from memory_manager import MemoryManager
from history_service import HistoryService
import sqlite3
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)

def test_history_recording():
    """测试历史记录保存功能"""
    print("=== 测试历史记录保存功能 ===")
    
    # 初始化服务
    memory_manager = MemoryManager()
    history_service = HistoryService(memory_manager)
    
    # 检查初始记录数
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM query_history')
    initial_count = cursor.fetchone()[0]
    print(f"初始记录数: {initial_count}")
    conn.close()
    
    # 模拟不同类型的查询
    test_queries = [
        {
            "user_query": "测试可视化查询",
            "query_type": "visualization", 
            "sql_generated": "SELECT * FROM test",
            "result_summary": "可视化成功",
            "success": True,
            "execution_time": 1.5
        },
        {
            "user_query": "测试SQL查询",
            "query_type": "sql",
            "sql_generated": "SELECT COUNT(*) FROM orders",
            "result_summary": "查询结果: 100条记录",
            "success": True,
            "execution_time": 0.8
        },
        {
            "user_query": "测试普通对话",
            "query_type": "general",
            "sql_generated": "",
            "result_summary": "您好，我是您的数据助手",
            "success": True,
            "execution_time": 0.3
        }
    ]
    
    # 保存测试查询
    saved_ids = []
    for i, query in enumerate(test_queries):
        try:
            record_id = history_service.record_query(**query)
            saved_ids.append(record_id)
            print(f"查询 {i+1} 保存成功，ID: {record_id}")
        except Exception as e:
            print(f"查询 {i+1} 保存失败: {e}")
    
    # 检查最终记录数
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM query_history')
    final_count = cursor.fetchone()[0]
    print(f"最终记录数: {final_count}")
    
    # 显示新增的记录
    if saved_ids:
        placeholders = ','.join(['?' for _ in saved_ids])
        cursor.execute(f'SELECT * FROM query_history WHERE id IN ({placeholders}) ORDER BY timestamp DESC', saved_ids)
        new_records = cursor.fetchall()
        print("\n新增的记录:")
        for r in new_records:
            print(f"  ID: {r[0]}, Query: {r[3][:30]}..., Type: {r[4]}, Success: {r[8]}")
    
    conn.close()
    
    print(f"\n测试完成！新增了 {final_count - initial_count} 条记录")
    return final_count - initial_count

if __name__ == "__main__":
    test_history_recording()
