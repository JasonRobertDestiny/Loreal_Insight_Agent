#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库结构
"""

import sqlite3
import pandas as pd

def check_database_structure():
    """检查数据库结构和数据内容"""
    # 连接到数据库
    conn = sqlite3.connect('data/order_database.db')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print('数据库中的表:')
    for table in tables:
        print(f'  - {table[0]}')
    
    # 检查主要表的结构
    main_tables = ['new_fact_order_detail', 'dim_product', 'dim_province']
    
    for table_name in main_tables:
        try:
            print(f'\n=== {table_name} 表 ===')
            
            # 表结构
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = cursor.fetchall()
            print('列结构:')
            for col in columns:
                print(f'  {col[1]} ({col[2]})')
            
            # 数据样本
            print(f'\n前3行数据:')
            df = pd.read_sql_query(f'SELECT * FROM {table_name} LIMIT 3', conn)
            if not df.empty:
                print(df.to_string())
            else:
                print('  无数据')
            
            # 数据统计
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'\n总行数: {count}')
            
        except Exception as e:
            print(f'  错误: {e}')
    
    # 检查品牌信息
    print('\n=== 品牌信息 ===')
    try:
        cursor.execute("SELECT DISTINCT brand FROM dim_product WHERE brand IS NOT NULL LIMIT 10")
        brands = cursor.fetchall()
        print('可用品牌:')
        for brand in brands:
            print(f'  - {brand[0]}')
    except Exception as e:
        print(f'品牌查询错误: {e}')
    
    # 检查省份信息
    print('\n=== 省份信息 ===')
    try:
        cursor.execute("SELECT DISTINCT province_name FROM dim_province WHERE province_name IS NOT NULL LIMIT 10")
        provinces = cursor.fetchall()
        print('可用省份:')
        for province in provinces:
            print(f'  - {province[0]}')
    except Exception as e:
        print(f'省份查询错误: {e}')
    
    conn.close()

if __name__ == "__main__":
    check_database_structure()
