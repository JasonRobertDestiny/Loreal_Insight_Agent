#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建历史记录和记忆功能所需的数据库表
"""

import sqlite3
import os
import logging
from config import Config

logger = logging.getLogger(__name__)

def init_memory_database(db_path: str = None):
    """初始化记忆数据库
    
    Args:
        db_path: 数据库路径，如果为None则使用配置文件中的路径
    """
    if db_path is None:
        config = Config()
        # 从DATABASE_URL中提取SQLite数据库路径
        db_url = config.DATABASE_URL
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
        else:
            db_path = 'data/memory_database.db'  # 默认路径
    
    # 确保数据库目录存在
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created database directory: {db_dir}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建查询历史表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_query TEXT NOT NULL,
            query_type TEXT NOT NULL,  -- 'sql', 'visualization', 'general'
            sql_query TEXT,
            result_summary TEXT,
            success BOOLEAN DEFAULT TRUE,
            execution_time REAL DEFAULT 0.0,
            session_id TEXT,
            user_feedback INTEGER,  -- 1: positive, 0: neutral, -1: negative
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 创建用户偏好表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preference_key TEXT NOT NULL UNIQUE,
            preference_value TEXT NOT NULL,
            preference_type TEXT DEFAULT 'string',  -- 'string', 'number', 'boolean', 'json'
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 创建查询嵌入表（用于语义搜索）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id INTEGER NOT NULL,
            embedding_vector TEXT,  -- JSON格式存储向量
            embedding_model TEXT DEFAULT 'text-embedding-ada-002',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (query_id) REFERENCES query_history (id) ON DELETE CASCADE
        )
        """)
        
        # 创建查询统计表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            total_queries INTEGER DEFAULT 0,
            successful_queries INTEGER DEFAULT 0,
            failed_queries INTEGER DEFAULT 0,
            avg_execution_time REAL DEFAULT 0.0,
            sql_queries INTEGER DEFAULT 0,
            viz_queries INTEGER DEFAULT 0,
            general_queries INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date)
        )
        """)
        
        # 创建会话表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL UNIQUE,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            total_queries INTEGER DEFAULT 0,
            successful_queries INTEGER DEFAULT 0,
            user_agent TEXT,
            ip_address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 创建查询模式表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT NOT NULL,
            pattern_description TEXT,
            pattern_regex TEXT,
            pattern_keywords TEXT,  -- JSON格式存储关键词列表
            usage_count INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            avg_execution_time REAL DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 创建索引以提高查询性能
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_query_history_timestamp ON query_history(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_query_history_type ON query_history(query_type)",
            "CREATE INDEX IF NOT EXISTS idx_query_history_success ON query_history(success)",
            "CREATE INDEX IF NOT EXISTS idx_query_history_session ON query_history(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_preferences_key ON user_preferences(preference_key)",
            "CREATE INDEX IF NOT EXISTS idx_query_embeddings_query_id ON query_embeddings(query_id)",
            "CREATE INDEX IF NOT EXISTS idx_query_stats_date ON query_stats(date)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_query_patterns_name ON query_patterns(pattern_name)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # 插入默认用户偏好
        default_preferences = [
            ('language', 'zh', 'string', '用户界面语言'),
            ('theme', 'light', 'string', '界面主题'),
            ('max_history_days', '30', 'number', '历史记录保留天数'),
            ('enable_suggestions', 'true', 'boolean', '是否启用查询建议'),
            ('auto_save_queries', 'true', 'boolean', '是否自动保存查询'),
            ('show_sql_details', 'true', 'boolean', '是否显示SQL详情'),
            ('enable_analytics', 'true', 'boolean', '是否启用使用分析')
        ]
        
        for pref_key, pref_value, pref_type, description in default_preferences:
            cursor.execute("""
            INSERT OR IGNORE INTO user_preferences 
            (preference_key, preference_value, preference_type, description)
            VALUES (?, ?, ?, ?)
            """, (pref_key, pref_value, pref_type, description))
        
        # 插入默认查询模式
        default_patterns = [
            ('sales_query', '销售相关查询', r'销售|sales|revenue|收入', '["销售", "sales", "revenue", "收入", "营收"]'),
            ('time_series', '时间序列查询', r'趋势|trend|时间|time|日期|date', '["趋势", "trend", "时间", "time", "日期", "date"]'),
            ('comparison', '对比分析查询', r'对比|比较|compare|vs|versus', '["对比", "比较", "compare", "vs", "versus"]'),
            ('top_ranking', '排名查询', r'排名|排行|top|最|best|worst', '["排名", "排行", "top", "最", "best", "worst"]'),
            ('visualization', '可视化查询', r'图表|图|chart|plot|可视化|visualize', '["图表", "图", "chart", "plot", "可视化", "visualize"]')
        ]
        
        for pattern_name, description, regex, keywords in default_patterns:
            cursor.execute("""
            INSERT OR IGNORE INTO query_patterns 
            (pattern_name, pattern_description, pattern_regex, pattern_keywords)
            VALUES (?, ?, ?, ?)
            """, (pattern_name, description, regex, keywords))
        
        conn.commit()
        logger.info(f"Memory database initialized successfully at: {db_path}")
        
        # 验证表创建
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"Created tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        logger.error(f"Error initializing memory database: {e}")
        raise
    
    finally:
        if conn:
            conn.close()

def check_database_schema(db_path: str = None):
    """检查数据库模式
    
    Args:
        db_path: 数据库路径
        
    Returns:
        dict: 数据库模式信息
    """
    if db_path is None:
        config = Config()
        # 从DATABASE_URL中提取SQLite数据库路径
        db_url = config.DATABASE_URL
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
        else:
            db_path = 'data/memory_database.db'  # 默认路径
    
    if not os.path.exists(db_path):
        return {"exists": False, "tables": [], "error": "Database file not found"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        # 获取每个表的结构
        table_schemas = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            table_schemas[table] = columns
        
        # 获取索引信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [index[0] for index in cursor.fetchall()]
        
        return {
            "exists": True,
            "tables": tables,
            "schemas": table_schemas,
            "indexes": indexes,
            "error": None
        }
    
    except Exception as e:
        return {"exists": True, "tables": [], "error": str(e)}
    
    finally:
        if conn:
            conn.close()

def upgrade_database_schema(db_path: str = None):
    """升级数据库模式
    
    Args:
        db_path: 数据库路径
    """
    if db_path is None:
        config = Config()
        # 从DATABASE_URL中提取SQLite数据库路径
        db_url = config.DATABASE_URL
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
        else:
            db_path = 'data/memory_database.db'  # 默认路径
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否需要添加新列
        cursor.execute("PRAGMA table_info(query_history)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加缺失的列
        if 'user_feedback' not in columns:
            cursor.execute("ALTER TABLE query_history ADD COLUMN user_feedback INTEGER")
            logger.info("Added user_feedback column to query_history table")
        
        if 'session_id' not in columns:
            cursor.execute("ALTER TABLE query_history ADD COLUMN session_id TEXT")
            logger.info("Added session_id column to query_history table")
        
        conn.commit()
        logger.info("Database schema upgraded successfully")
    
    except Exception as e:
        logger.error(f"Error upgrading database schema: {e}")
        raise
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Initializing memory database...")
    
    # 初始化数据库
    init_memory_database()
    
    # 检查数据库模式
    schema_info = check_database_schema()
    print(f"Database schema check: {schema_info}")
    
    print("Memory database initialization completed!")