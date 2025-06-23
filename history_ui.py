#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录UI组件
提供历史记录的界面展示和交互功能
"""

import gradio as gr
from typing import List, Dict, Any, Optional, Tuple
from history_service import HistoryService
from memory_manager import MemoryManager
from ui_translations import ui_translations
import logging

logger = logging.getLogger(__name__)

class HistoryUI:
    """历史记录UI管理器"""
    
    def __init__(self, history_service: HistoryService):
        """初始化历史记录UI
        
        Args:
            history_service: 历史记录服务实例
        """
        self.history_service = history_service
        logger.info("HistoryUI initialized")
    
    def create_history_panel(self):
        """创建简洁的历史记录面板"""
        with gr.Column(scale=1, elem_id="history-panel") as history_panel:
            # 标题
            gr.HTML(
                f"<h3 style='text-align: center; margin: 10px 0; color: #2c3e50;'>"
                f"📊 {self._get_text('history_title', ui_translations.get_current_language())}</h3>"
            )
            
            # 搜索框
            search_input = gr.Textbox(
                placeholder=self._get_text('search_placeholder', ui_translations.get_current_language()),
                label="",
                elem_id="history-search",
                scale=1,
                container=False
            )
            
            # 历史记录列表
            with gr.Row():
                history_display = gr.HTML(
                    value=self._get_history_list_html(),
                    elem_id="history-list"
                )
            
            # 底部操作按钮
            with gr.Row():
                with gr.Column(scale=1):
                    export_btn = gr.Button(
                        "📥 导出",
                        variant="secondary",
                        size="sm"
                    )
                with gr.Column(scale=1):
                    clear_btn = gr.Button(
                        "🗑️ 清空",
                        variant="secondary",
                        size="sm"
                    )
            
            # 导出文件下载
            export_file = gr.File(
                label="",
                visible=False,
                elem_id="export-file"
            )
            
            # 事件绑定
            search_input.change(
                fn=self._search_history,
                inputs=[search_input],
                outputs=[history_display]
            )
            
            export_btn.click(
                fn=self._export_history,
                outputs=[export_file]
            )
            
            clear_btn.click(
                fn=self._clear_history,
                outputs=[history_display]
            )
        
        # 存储组件引用
        self.history_display = history_display
        
        return history_panel
    
    def _get_text(self, key: str, language: str) -> str:
        """获取多语言文本
        
        Args:
            key: 文本键
            language: 语言代码
            
        Returns:
            str: 本地化文本
        """
        texts = {
            'zh': {
                'history_title': '查询历史',
                'search_placeholder': '搜索历史记录...',
                'search_button': '搜索',
                'recent_queries': '最近查询',
                'popular_queries': '热门查询',
                'export_history': '导出历史',
                'session_stats': '会话统计',
                'query_suggestions': '查询建议',
                'no_history': '暂无历史记录',
                'no_suggestions': '暂无建议',
                'query_time': '查询时间',
                'query_type': '查询类型',
                'execution_time': '执行时间',
                'success': '成功',
                'failed': '失败',
                'total_queries': '总查询数',
                'success_rate': '成功率',
                'avg_time': '平均执行时间',
                'sql_queries': 'SQL查询',
                'viz_queries': '可视化查询'
            },
            'en': {
                'history_title': 'Query History',
                'search_placeholder': 'Search history...',
                'search_button': 'Search',
                'recent_queries': 'Recent Queries',
                'popular_queries': 'Popular Queries',
                'export_history': 'Export History',
                'session_stats': 'Session Statistics',
                'query_suggestions': 'Query Suggestions',
                'no_history': 'No history records',
                'no_suggestions': 'No suggestions',
                'query_time': 'Query Time',
                'query_type': 'Query Type',
                'execution_time': 'Execution Time',
                'success': 'Success',
                'failed': 'Failed',
                'total_queries': 'Total Queries',
                'success_rate': 'Success Rate',
                'avg_time': 'Average Execution Time',
                'sql_queries': 'SQL Queries',
                'viz_queries': 'Visualization Queries'
            }
        }
        
        return texts.get(language, texts['zh']).get(key, key)
    
    def _render_empty_history(self, language: str) -> str:
        """渲染空历史记录
        
        Args:
            language: 语言代码
            
        Returns:
            str: HTML内容
        """
        return f"""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <p>{self._get_text('no_history', language)}</p>
        </div>
        """
    
    def _render_empty_suggestions(self, language: str) -> str:
        """渲染空建议列表
        
        Args:
            language: 语言代码
            
        Returns:
            str: HTML内容
        """
        return f"""
        <div style="text-align: center; padding: 1rem; color: #666;">
            <p>{self._get_text('no_suggestions', language)}</p>
        </div>
        """
    
    def _render_session_stats(self) -> str:
        """渲染会话统计信息
        
        Returns:
            str: HTML内容
        """
        try:
            summary = self.history_service.get_session_summary()
            stats = summary['session_stats']
            recent = summary['recent_activity']
            
            current_lang = ui_translations.get_current_language()
            
            html = f"""
            <div style="padding: 1rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px;">
                        <div style="font-weight: bold; color: #333;">{self._get_text('total_queries', current_lang)}</div>
                        <div style="font-size: 1.5rem; color: #007bff;">{stats['total_queries']}</div>
                    </div>
                    <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px;">
                        <div style="font-weight: bold; color: #333;">{self._get_text('success_rate', current_lang)}</div>
                        <div style="font-size: 1.5rem; color: #28a745;">{stats['success_rate']:.1f}%</div>
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px;">
                    <div style="font-weight: bold; color: #333; margin-bottom: 0.5rem;">{self._get_text('avg_time', current_lang)}</div>
                    <div style="color: #666;">{stats['avg_execution_time']:.2f}秒</div>
                </div>
            </div>
            """
            
            return html
        
        except Exception as e:
            logger.error(f"Error rendering session stats: {e}")
            return "<div style='padding: 1rem; color: #666;'>统计信息加载失败</div>"
    
    def _search_history(self, keyword: str) -> str:
        """搜索历史记录
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            str: HTML内容
        """
        try:
            if not keyword.strip():
                return self._get_history_list_html()
            
            results = self.history_service.search_queries(keyword, limit=20)
            if not results:
                return f"<div style='text-align: center; color: #666; padding: 20px;'>未找到相关记录</div>"
            
            html = "<div style='max-height: 400px; overflow-y: auto;'>"
            for query in results:
                status_icon = "✅" if query.get('success', False) else "❌"
                query_type = query.get('query_type', 'unknown')
                type_icon = "📊" if query_type == 'visualization' else "💬"
                
                # 高亮搜索关键词
                query_text = query.get('query_text', '')
                if keyword.lower() in query_text.lower():
                    query_text = query_text.replace(keyword, f"<mark>{keyword}</mark>")
                
                # 截取查询文本
                if len(query_text) > 60:
                    query_text = query_text[:60] + "..."
                
                # 格式化时间
                timestamp = query.get('timestamp', '')
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%m-%d %H:%M')
                    except:
                        time_str = timestamp[:16]
                else:
                    time_str = ''
                
                html += f"""
                <div style='margin: 8px 0; padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid {"#28a745" if query.get('success', False) else "#dc3545"};'>
                    <div style='font-weight: 500; margin-bottom: 4px;'>{type_icon} {query_text}</div>
                    <div style='font-size: 0.75em; color: #666; display: flex; justify-content: space-between;'>
                        <span>{status_icon} {time_str}</span>
                        <span>{query.get('execution_time', 0):.1f}s</span>
                    </div>
                </div>
                """
            html += "</div>"
            return html
        
        except Exception as e:
            logger.error(f"Error searching history: {e}")
            return f"<div style='color: red; text-align: center; padding: 20px;'>搜索失败</div>"
    
    def _show_recent_queries(self) -> str:
        """显示最近查询
        
        Returns:
            str: HTML内容
        """
        try:
            queries = self.history_service.get_recent_queries(days=7, limit=20)
            return self._render_history_list(queries)
        
        except Exception as e:
            logger.error(f"Error showing recent queries: {e}")
            return f"<div style='padding: 1rem; color: #dc3545;'>加载失败: {str(e)}</div>"
    
    def _show_popular_queries(self) -> str:
        """显示热门查询
        
        Returns:
            str: HTML内容
        """
        try:
            popular = self.history_service.memory_manager.get_popular_queries(limit=15)
            
            if not popular:
                current_lang = ui_translations.get_current_language()
                return self._render_empty_history(current_lang)
            
            html = "<div style='padding: 0.5rem;'>"
            
            for item in popular:
                html += f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; margin-bottom: 0.8rem; background: #fafafa;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem; color: #333;">{item['query']}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #666;">
                        <span>使用次数: {item['usage_count']}</span>
                        <span>最后使用: {item['last_used'][:10]}</span>
                    </div>
                </div>
                """
            
            html += "</div>"
            return html
        
        except Exception as e:
            logger.error(f"Error showing popular queries: {e}")
            return f"<div style='padding: 1rem; color: #dc3545;'>加载失败: {str(e)}</div>"
    
    def _get_history_list_html(self) -> str:
        """获取历史记录列表的HTML"""
        try:
            recent_queries = self.history_service.get_recent_queries(limit=10)
            if not recent_queries:
                return f"<div style='text-align: center; color: #666; padding: 20px;'>暂无历史记录</div>"
            
            html = "<div style='max-height: 400px; overflow-y: auto;'>"
            for query in recent_queries:
                status_icon = "✅" if query.get('success', False) else "❌"
                query_type = query.get('query_type', 'unknown')
                type_icon = "📊" if query_type == 'visualization' else "💬"
                
                # 截取查询文本
                query_text = query.get('query_text', '')[:60]
                if len(query.get('query_text', '')) > 60:
                    query_text += "..."
                
                # 格式化时间
                timestamp = query.get('timestamp', '')
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%m-%d %H:%M')
                    except:
                        time_str = timestamp[:16]
                else:
                    time_str = ''
                
                html += f"""
                <div style='margin: 8px 0; padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid {"#28a745" if query.get('success', False) else "#dc3545"};'>
                    <div style='font-weight: 500; margin-bottom: 4px;'>{type_icon} {query_text}</div>
                    <div style='font-size: 0.75em; color: #666; display: flex; justify-content: space-between;'>
                        <span>{status_icon} {time_str}</span>
                        <span>{query.get('execution_time', 0):.1f}s</span>
                    </div>
                </div>
                """
            html += "</div>"
            return html
        except Exception as e:
            logger.error(f"Error getting history list HTML: {e}")
            return f"<div style='color: red; text-align: center; padding: 20px;'>加载失败</div>"
    
    def _export_history(self) -> str:
        """导出历史记录
        
        Returns:
            str: 导出文件路径
        """
        try:
            filename = self.history_service.export_history(format_type='csv', days=30)
            return filename
        
        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            return None
    
    def _clear_history(self) -> str:
        """清空历史记录
        
        Returns:
            str: HTML内容
        """
        try:
            # 这里可以添加确认对话框的逻辑
            # 暂时直接清空
            self.history_service.clear_history()
            return f"<div style='text-align: center; color: #666; padding: 20px;'>历史记录已清空</div>"
        
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return f"<div style='color: red; text-align: center; padding: 20px;'>清空失败</div>"
    
    def get_query_suggestions(self, current_query: str) -> str:
        """获取查询建议
        
        Args:
            current_query: 当前查询
            
        Returns:
            str: HTML内容
        """
        try:
            if not current_query.strip():
                current_lang = ui_translations.get_current_language()
                return self._render_empty_suggestions(current_lang)
            
            suggestions = self.history_service.get_query_suggestions(current_query, limit=5)
            
            if not suggestions:
                current_lang = ui_translations.get_current_language()
                return self._render_empty_suggestions(current_lang)
            
            html = "<div style='padding: 0.5rem;'>"
            
            for suggestion in suggestions:
                type_color = "#007bff" if suggestion['type'] == 'popular' else "#6c757d"
                type_icon = "🔥" if suggestion['type'] == 'popular' else "💡"
                
                html += f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 6px; padding: 0.8rem; margin-bottom: 0.5rem; background: white; cursor: pointer;" 
                     onclick="document.querySelector('input[placeholder*=\"输入\"]').value = '{suggestion['query']}';">
                    <div style="display: flex; align-items: center; margin-bottom: 0.3rem;">
                        <span style="margin-right: 0.5rem;">{type_icon}</span>
                        <span style="font-weight: bold; color: #333; flex: 1;">{suggestion['query']}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: {type_color};">{suggestion['reason']}</div>
                </div>
                """
            
            html += "</div>"
            return html
        
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return f"<div style='padding: 1rem; color: #dc3545;'>建议加载失败: {str(e)}</div>"