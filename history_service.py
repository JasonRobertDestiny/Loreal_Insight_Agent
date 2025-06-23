#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录服务模块
提供历史记录的高级管理和分析功能
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from memory_manager import MemoryManager, QueryRecord
from language_utils import language_detector
import re

logger = logging.getLogger(__name__)

class HistoryService:
    """历史记录服务"""
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """初始化历史记录服务
        
        Args:
            memory_manager: 记忆管理器实例
        """
        self.memory_manager = memory_manager or MemoryManager()
        logger.info("HistoryService initialized")
    
    def record_query(self, 
                    user_query: str, 
                    query_type: str,
                    sql_generated: str = "",
                    result_summary: str = "",
                    success: bool = True,
                    execution_time: float = 0.0,
                    user_feedback: Optional[str] = None) -> int:
        """记录用户查询
        
        Args:
            user_query: 用户查询
            query_type: 查询类型 ('sql' 或 'visualization')
            sql_generated: 生成的SQL
            result_summary: 结果摘要
            success: 是否成功
            execution_time: 执行时间
            user_feedback: 用户反馈
            
        Returns:
            int: 记录ID
        """
        # 检测查询语言
        language = language_detector.detect_language(user_query)
        
        record = QueryRecord(
            user_query=user_query,
            query_type=query_type,
            sql_generated=sql_generated,
            result_summary=result_summary,
            language=language,
            success=success,
            execution_time=execution_time,
            user_feedback=user_feedback
        )
        
        return self.memory_manager.save_query(record)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取对话历史记录（格式化为聊天界面使用）
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            List[Dict]: 格式化的对话历史
        """
        records = self.memory_manager.get_session_history(limit=limit)
        
        conversation = []
        for record in reversed(records):  # 按时间正序排列
            conversation.append({
                'user': record.user_query,
                'assistant': record.result_summary,
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'query_type': record.query_type,
                'success': record.success,
                'execution_time': record.execution_time
            })
        
        return conversation
    
    def get_recent_queries(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最近的查询记录
        
        Args:
            days: 天数范围
            limit: 返回记录数限制
            
        Returns:
            List[Dict]: 查询记录列表
        """
        records = self.memory_manager.get_recent_history(days=days, limit=limit)
        
        queries = []
        for record in records:
            queries.append({
                'id': record.id,
                'query': record.user_query,
                'type': record.query_type,
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'success': record.success,
                'language': record.language,
                'execution_time': record.execution_time
            })
        
        return queries
    
    def search_queries(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索查询记录
        
        Args:
            keyword: 搜索关键词
            limit: 返回记录数限制
            
        Returns:
            List[Dict]: 匹配的查询记录
        """
        records = self.memory_manager.search_history(keyword, limit)
        
        results = []
        for record in records:
            # 高亮匹配的关键词
            highlighted_query = self._highlight_keyword(record.user_query, keyword)
            highlighted_summary = self._highlight_keyword(record.result_summary, keyword)
            
            results.append({
                'id': record.id,
                'query': record.user_query,
                'highlighted_query': highlighted_query,
                'summary': record.result_summary,
                'highlighted_summary': highlighted_summary,
                'type': record.query_type,
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'success': record.success,
                'language': record.language
            })
        
        return results
    
    def _highlight_keyword(self, text: str, keyword: str) -> str:
        """高亮关键词
        
        Args:
            text: 原文本
            keyword: 关键词
            
        Returns:
            str: 高亮后的文本
        """
        if not text or not keyword:
            return text
        
        # 使用正则表达式进行不区分大小写的替换
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        return pattern.sub(f'**{keyword}**', text)
    
    def get_query_suggestions(self, current_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """基于当前查询获取建议
        
        Args:
            current_query: 当前查询
            limit: 返回建议数限制
            
        Returns:
            List[Dict]: 查询建议列表
        """
        suggestions = []
        
        # 1. 基于关键词的相似查询
        keywords = self._extract_keywords(current_query)
        for keyword in keywords[:3]:  # 取前3个关键词
            similar_records = self.memory_manager.search_history(keyword, limit=3)
            for record in similar_records:
                if record.user_query.lower() != current_query.lower():
                    suggestions.append({
                        'query': record.user_query,
                        'type': 'similar',
                        'reason': f'包含关键词: {keyword}',
                        'usage_count': 1,
                        'last_used': record.timestamp.strftime('%Y-%m-%d')
                    })
        
        # 2. 热门查询推荐
        popular_queries = self.memory_manager.get_popular_queries(limit=5)
        for query_info in popular_queries:
            if query_info['query'].lower() != current_query.lower():
                suggestions.append({
                    'query': query_info['query'],
                    'type': 'popular',
                    'reason': f"热门查询 (使用{query_info['usage_count']}次)",
                    'usage_count': query_info['usage_count'],
                    'last_used': query_info['last_used'][:10]  # 只取日期部分
                })
        
        # 3. 去重并排序
        seen_queries = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion['query'] not in seen_queries:
                seen_queries.add(suggestion['query'])
                unique_suggestions.append(suggestion)
        
        # 按使用次数和类型排序
        unique_suggestions.sort(key=lambda x: (x['type'] == 'popular', x['usage_count']), reverse=True)
        
        return unique_suggestions[:limit]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """从查询中提取关键词
        
        Args:
            query: 查询字符串
            
        Returns:
            List[str]: 关键词列表
        """
        # 简单的关键词提取（可以后续优化为更复杂的NLP处理）
        # 移除常见的停用词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        # 分词（简单按空格和标点分割）
        words = re.findall(r'\w+', query.lower())
        
        # 过滤停用词和短词
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:5]  # 返回前5个关键词
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取当前会话摘要
        
        Returns:
            Dict[str, Any]: 会话摘要信息
        """
        stats = self.memory_manager.get_session_stats()
        recent_queries = self.get_recent_queries(days=1, limit=10)
        
        # 分析查询类型分布
        query_types = {}
        languages = {}
        
        for query in recent_queries:
            query_type = query['type']
            language = query['language']
            
            query_types[query_type] = query_types.get(query_type, 0) + 1
            languages[language] = languages.get(language, 0) + 1
        
        return {
            'session_stats': stats,
            'recent_activity': {
                'total_queries_today': len(recent_queries),
                'query_types': query_types,
                'languages': languages
            },
            'recommendations': self._get_session_recommendations(recent_queries)
        }
    
    def _get_session_recommendations(self, recent_queries: List[Dict[str, Any]]) -> List[str]:
        """基于会话历史生成推荐
        
        Args:
            recent_queries: 最近的查询记录
            
        Returns:
            List[str]: 推荐建议
        """
        recommendations = []
        
        if not recent_queries:
            recommendations.append("开始您的第一个数据查询吧！")
            return recommendations
        
        # 分析查询模式
        sql_count = sum(1 for q in recent_queries if q['type'] == 'sql')
        viz_count = sum(1 for q in recent_queries if q['type'] == 'visualization')
        
        if sql_count > viz_count * 2:
            recommendations.append("您经常使用SQL查询，不妨尝试一些数据可视化功能")
        elif viz_count > sql_count * 2:
            recommendations.append("您喜欢数据可视化，可以尝试更复杂的SQL分析")
        
        # 检查失败的查询
        failed_queries = [q for q in recent_queries if not q['success']]
        if failed_queries:
            recommendations.append(f"有{len(failed_queries)}个查询未成功，您可以重新尝试或寻求帮助")
        
        # 检查执行时间
        slow_queries = [q for q in recent_queries if q['execution_time'] > 5.0]
        if slow_queries:
            recommendations.append("有些查询执行较慢，考虑优化查询条件")
        
        return recommendations
    
    def export_history(self, format_type: str = 'csv', days: int = 30) -> str:
        """导出历史记录
        
        Args:
            format_type: 导出格式 ('csv', 'json')
            days: 导出最近几天的记录
            
        Returns:
            str: 导出文件路径
        """
        try:
            # 获取历史记录
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = """
            SELECT query_text, query_type, success, execution_time, timestamp, result_summary
            FROM query_history 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
            """
            
            cursor = self.db_connection.cursor()
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            records = cursor.fetchall()
            
            if not records:
                logger.warning("No history records found for export")
                return None
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"history_export_{timestamp}.{format_type}"
            filepath = os.path.join(os.getcwd(), filename)
            
            if format_type == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['查询内容', '查询类型', '是否成功', '执行时间(秒)', '时间戳', '结果摘要'])
                    for record in records:
                        writer.writerow(record)
            
            elif format_type == 'json':
                import json
                data = []
                for record in records:
                    data.append({
                        'query_text': record[0],
                        'query_type': record[1],
                        'success': bool(record[2]),
                        'execution_time': record[3],
                        'timestamp': record[4],
                        'result_summary': record[5]
                    })
                
                with open(filepath, 'w', encoding='utf-8') as jsonfile:
                    json.dump(data, jsonfile, ensure_ascii=False, indent=2)
            
            logger.info(f"History exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            raise
    
    def clear_history(self) -> bool:
        """清空历史记录
        
        Returns:
            bool: 是否成功清空
        """
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM query_history")
            self.db_connection.commit()
            
            logger.info("History cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False
    
    def add_user_feedback(self, query_id: int, feedback: str):
        """添加用户反馈
        
        Args:
            query_id: 查询记录ID
            feedback: 用户反馈
        """
        # 这里需要在MemoryManager中添加更新反馈的方法
        # 暂时记录日志
        logger.info(f"User feedback for query {query_id}: {feedback}")
    
    def clear_history(self, days: Optional[int] = None):
        """清除历史记录
        
        Args:
            days: 清除多少天前的记录，None表示清除当前会话
        """
        if days is None:
            self.memory_manager.clear_session_history()
            logger.info("Current session history cleared")
        else:
            # 这里需要在MemoryManager中添加按日期清除的方法
            logger.info(f"History older than {days} days would be cleared")