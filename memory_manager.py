#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆管理模块
提供查询历史记录、会话记忆和智能推荐功能
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class QueryRecord:
    """查询记录数据类"""
    id: Optional[int] = None
    session_id: str = ""
    timestamp: datetime = None
    user_query: str = ""
    query_type: str = ""  # 'sql' or 'visualization'
    sql_generated: str = ""
    result_summary: str = ""
    language: str = "zh"
    success: bool = True
    execution_time: float = 0.0
    user_feedback: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class UserPreference:
    """用户偏好数据类"""
    user_id: str
    preference_key: str
    preference_value: str
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, db_path: str = None):
        """初始化记忆管理器
        
        Args:
            db_path: 数据库路径，如果为None则使用默认路径
        """
        if db_path is None:
            # 直接使用chat_history.db作为历史记录数据库
            self.db_path = 'chat_history.db'
        else:
            self.db_path = db_path
        self.current_session_id = self._generate_session_id()
        self._init_database()
        logger.info(f"MemoryManager initialized with session: {self.current_session_id}")
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_obj = hashlib.md5(timestamp.encode())
        return f"session_{timestamp}_{hash_obj.hexdigest()[:8]}"
    
    def _init_database(self):
        """初始化数据库表"""
        # 确保数据目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建查询历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    sql_generated TEXT,
                    result_summary TEXT,
                    language TEXT DEFAULT 'zh',
                    success BOOLEAN DEFAULT 1,
                    execution_time REAL DEFAULT 0.0,
                    user_feedback TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建用户偏好表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, preference_key)
                )
            """)
            
            # 创建查询统计表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE NOT NULL,
                    query_pattern TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TEXT DEFAULT CURRENT_TIMESTAMP,
                    avg_execution_time REAL DEFAULT 0.0
                )
            """)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
    
    def save_query(self, record: QueryRecord) -> int:
        """保存查询记录
        
        Args:
            record: 查询记录对象
            
        Returns:
            int: 记录ID
        """
        record.session_id = self.current_session_id
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO query_history (
                    session_id, timestamp, user_query, query_type,
                    sql_generated, result_summary, language, success,
                    execution_time, user_feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.session_id,
                record.timestamp.isoformat(),
                record.user_query,
                record.query_type,
                record.sql_generated,
                record.result_summary,
                record.language,
                record.success,
                record.execution_time,
                record.user_feedback
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            
            # 更新查询统计
            self._update_query_stats(record)
            
            logger.info(f"Query record saved with ID: {record_id}")
            return record_id
    
    def _update_query_stats(self, record: QueryRecord):
        """更新查询统计信息"""
        query_hash = hashlib.md5(record.user_query.lower().encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute(
                "SELECT usage_count, avg_execution_time FROM query_stats WHERE query_hash = ?",
                (query_hash,)
            )
            result = cursor.fetchone()
            
            if result:
                # 更新现有记录
                usage_count, avg_time = result
                new_count = usage_count + 1
                new_avg_time = (avg_time * usage_count + record.execution_time) / new_count
                
                cursor.execute("""
                    UPDATE query_stats 
                    SET usage_count = ?, avg_execution_time = ?, last_used = ?
                    WHERE query_hash = ?
                """, (new_count, new_avg_time, datetime.now().isoformat(), query_hash))
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO query_stats (query_hash, query_pattern, usage_count, avg_execution_time)
                    VALUES (?, ?, 1, ?)
                """, (query_hash, record.user_query, record.execution_time))
            
            conn.commit()
    
    def get_session_history(self, session_id: Optional[str] = None, limit: int = 50) -> List[QueryRecord]:
        """获取会话历史记录
        
        Args:
            session_id: 会话ID，默认为当前会话
            limit: 返回记录数限制
            
        Returns:
            List[QueryRecord]: 查询记录列表
        """
        if session_id is None:
            session_id = self.current_session_id
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM query_history 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (session_id, limit))
            
            records = []
            for row in cursor.fetchall():
                record = QueryRecord(
                    id=row[0],
                    session_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_query=row[3],
                    query_type=row[4],
                    sql_generated=row[5],
                    result_summary=row[6],
                    language=row[7],
                    success=bool(row[8]),
                    execution_time=row[9],
                    user_feedback=row[10]
                )
                records.append(record)
            
            return records
    
    def get_recent_history(self, days: int = 7, limit: int = 100) -> List[QueryRecord]:
        """获取最近的历史记录
        
        Args:
            days: 天数范围
            limit: 返回记录数限制
            
        Returns:
            List[QueryRecord]: 查询记录列表
        """
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM query_history 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (since_date.isoformat(), limit))
            
            records = []
            for row in cursor.fetchall():
                record = QueryRecord(
                    id=row[0],
                    session_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_query=row[3],
                    query_type=row[4],
                    sql_generated=row[5],
                    result_summary=row[6],
                    language=row[7],
                    success=bool(row[8]),
                    execution_time=row[9],
                    user_feedback=row[10]
                )
                records.append(record)
            
            return records
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门查询
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            List[Dict]: 热门查询列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT query_pattern, usage_count, avg_execution_time, last_used
                FROM query_stats 
                ORDER BY usage_count DESC, last_used DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'query': row[0],
                    'usage_count': row[1],
                    'avg_execution_time': row[2],
                    'last_used': row[3]
                })
            
            return results
    
    def search_history(self, keyword: str, limit: int = 20) -> List[QueryRecord]:
        """搜索历史记录
        
        Args:
            keyword: 搜索关键词
            limit: 返回记录数限制
            
        Returns:
            List[QueryRecord]: 匹配的查询记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM query_history 
                WHERE user_query LIKE ? OR result_summary LIKE ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (f"%{keyword}%", f"%{keyword}%", limit))
            
            records = []
            for row in cursor.fetchall():
                record = QueryRecord(
                    id=row[0],
                    session_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_query=row[3],
                    query_type=row[4],
                    sql_generated=row[5],
                    result_summary=row[6],
                    language=row[7],
                    success=bool(row[8]),
                    execution_time=row[9],
                    user_feedback=row[10]
                )
                records.append(record)
            
            return records
    
    def save_user_preference(self, user_id: str, key: str, value: str):
        """保存用户偏好
        
        Args:
            user_id: 用户ID
            key: 偏好键
            value: 偏好值
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value, updated_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, key, value, datetime.now().isoformat()))
            
            conn.commit()
            logger.info(f"User preference saved: {user_id}.{key} = {value}")
    
    def get_user_preference(self, user_id: str, key: str, default: str = None) -> Optional[str]:
        """获取用户偏好
        
        Args:
            user_id: 用户ID
            key: 偏好键
            default: 默认值
            
        Returns:
            Optional[str]: 偏好值
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT preference_value FROM user_preferences WHERE user_id = ? AND preference_key = ?",
                (user_id, key)
            )
            
            result = cursor.fetchone()
            return result[0] if result else default
    
    def clear_session_history(self, session_id: Optional[str] = None):
        """清除会话历史
        
        Args:
            session_id: 会话ID，默认为当前会话
        """
        if session_id is None:
            session_id = self.current_session_id
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM query_history WHERE session_id = ?", (session_id,))
            conn.commit()
            
            logger.info(f"Session history cleared: {session_id}")
    
    def get_session_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取会话统计信息
        
        Args:
            session_id: 会话ID，默认为当前会话
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        if session_id is None:
            session_id = self.current_session_id
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_queries,
                    AVG(execution_time) as avg_execution_time,
                    COUNT(DISTINCT query_type) as query_types
                FROM query_history 
                WHERE session_id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            
            return {
                'session_id': session_id,
                'total_queries': result[0] or 0,
                'successful_queries': result[1] or 0,
                'success_rate': (result[1] / result[0] * 100) if result[0] > 0 else 0,
                'avg_execution_time': result[2] or 0,
                'query_types': result[3] or 0
            }