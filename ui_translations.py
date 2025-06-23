# -*- coding: utf-8 -*-
"""
界面多语言文本管理模块
支持中文、英文、法语三种语言的界面文本切换
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class UITranslations:
    """界面多语言文本管理类"""
    
    def __init__(self):
        self.translations = {
            'zh': {
                # 主标题和描述
                'app_title': '🔍 L\'Oréal 数据洞察助手',
                'app_description': '让数据洞察如钻石般闪耀，每次查询都是发现价值的旅程',
                
                # 功能卡片
                'smart_query_title': '💎 智能查询',
                'smart_query_desc': '自然语言转SQL，智能数据查询',
                'data_viz_title': '📊 数据可视化',
                'data_viz_desc': '多样图表类型，直观数据展示',
                'smart_insight_title': '🎯 智能洞察',
                'smart_insight_desc': '深度分析，专业商业洞察',
                
                # 交互界面
                'chat_history': '💬 对话历史',
                'input_placeholder': '💭 请输入您的数据查询问题...',
                'send_button': '🚀 发送查询',
                'clear_button': '🗑️ 清空对话',
                
                # 技术详情面板
                'tech_details': '🔧 技术详情',
                'sql_query_label': '📝 生成的SQL查询',
                'sql_placeholder': 'SQL查询将在这里显示...',
                'result_label': '📋 数据库返回结果',
                'result_placeholder': '查询结果将在这里显示...',
                
                # 示例查询
                'precise_query': '💎 精准查询',
                'visual_display': '🎨 视觉呈现',
                'smart_insights': '🔮 智慧洞察',
                
                # 示例查询内容 - 基于实际数据结构优化
                'examples_precise': [
                    "Count orders by province",
                    "各省份销售额排名统计",
                    "统计各渠道的销售业绩",
                    "查询广东省和江苏省的销售对比"
                ],
                'examples_visual': [
                    "绘制各省份销售额对比图",
                    " Plot monthly sales trend chart",
                    "制作渠道销售额分布饼图", 
                    "绘制Top 10产品销售量排行榜"
                ],
                'examples_insights': [
                    "哪个省份的销售表现最好？",
                    "What are the top selling products?",
                    "销售业绩的季节性趋势如何？",
                    "不同渠道的表现差异分析"
                ],
                
                # 设置
                'language_setting': '语言',
                'theme_setting': '显示主题',
                'light_theme': '浅色',
                'dark_theme': '深色',
                'system_theme': '系统',
                
                # 错误和状态消息
                'no_data_message': '无法生成数据可视化，请尝试其他查询。',
                'data_summary_prefix': '以下是查询结果的可视化：\n\n',
                'data_rows_info': '数据包含 {count} 行记录。\n',
                'date_range_info': '• {col} 范围: {min_date} 到 {max_date}\n',
                'numeric_stats_info': '• {col} 统计: 总和={sum:.2f}, 平均值={avg:.2f}\n',
                
                # 历史记录相关
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
                'viz_queries': '可视化查询',
                'clear_history': '清空历史',
                'export_success': '导出成功',
                'export_failed': '导出失败',
                'refresh_button': '刷新',
                'back_to_chat': '返回对话',
                
                # 记忆功能
                'memory_title': '智能记忆',
                'user_preferences': '用户偏好',
                'query_patterns': '查询模式',
                'learned_insights': '学习洞察',
                'personalization': '个性化设置',
                'memory_stats': '记忆统计',
                'clear_memory': '清空记忆',
                'memory_cleared': '记忆已清空'
            },
            
            'en': {
                # Main title and description
                'app_title': '🔍 L\'Oréal Data Insight Assistant',
                'app_description': 'Let data insights shine like diamonds, every query is a journey to discover value',
                
                # Feature cards
                'smart_query_title': '💎 Smart Query',
                'smart_query_desc': 'Natural language to SQL, intelligent data querying',
                'data_viz_title': '📊 Data Visualization',
                'data_viz_desc': 'Diverse chart types, intuitive data display',
                'smart_insight_title': '🎯 Smart Insights',
                'smart_insight_desc': 'Deep analysis, professional business insights',
                
                # Interactive interface
                'chat_history': '💬 Chat History',
                'input_placeholder': '💭 Please enter your data query question...',
                'send_button': '🚀 Send Query',
                'clear_button': '🗑️ Clear Chat',
                
                # Technical details panel
                'tech_details': '🔧 Technical Details',
                'sql_query_label': '📝 Generated SQL Query',
                'sql_placeholder': 'SQL query will be displayed here...',
                'result_label': '📋 Database Results',
                'result_placeholder': 'Query results will be displayed here...',
                
                # Example queries
                'precise_query': '💎 Precise Query',
                'visual_display': '🎨 Visual Display',
                'smart_insights': '🔮 Smart Insights',
                
                # Example query content - optimized based on actual data structure
                'examples_precise': [
                    "Query total sales amount and order count for 2024",
                    "Show sales ranking by province",
                    "Count orders by channel",
                    "Compare sales between Guangdong and Jiangsu provinces"
                ],
                'examples_visual': [
                    "Plot provincial sales comparison chart",
                    "Visualize monthly sales trend changes",
                    "Create channel sales distribution pie chart",
                    "Draw Top 10 product sales ranking chart"
                ],
                'examples_insights': [
                    "Which province has the best sales performance?",
                    "Which products are most popular?",
                    "What are the seasonal trends in sales?",
                    "Performance comparison analysis across different channels"
                ],
                
                # Settings
                'language_setting': 'Language',
                'theme_setting': 'Display Theme',
                'light_theme': 'Light',
                'dark_theme': 'Dark',
                'system_theme': 'System',
                
                # 错误和状态消息
                'no_data_message': 'Unable to generate data visualization, please try other queries.',
                'data_summary_prefix': 'Here is the visualization of query results:\n\n',
                'data_rows_info': 'Data contains {count} rows.\n',
                'date_range_info': '• {col} range: {min_date} to {max_date}\n',
                'numeric_stats_info': '• {col} statistics: Sum={sum:.2f}, Average={avg:.2f}\n',
                
                # 历史记录相关
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
                'viz_queries': 'Visualization Queries',
                'clear_history': 'Clear History',
                'export_success': 'Export Successful',
                'export_failed': 'Export Failed',
                'refresh_button': 'Refresh',
                'back_to_chat': 'Back to Chat',
                
                # 记忆功能
                'memory_title': 'Smart Memory',
                'user_preferences': 'User Preferences',
                'query_patterns': 'Query Patterns',
                'learned_insights': 'Learned Insights',
                'personalization': 'Personalization',
                'memory_stats': 'Memory Statistics',
                'clear_memory': 'Clear Memory',
                'memory_cleared': 'Memory Cleared'
            }
        }
        
        # 当前语言设置
        self.current_language = 'zh'
    
    def set_language(self, language: str) -> bool:
        """设置当前语言
        
        Args:
            language: 语言代码 ('zh', 'en')
            
        Returns:
            设置是否成功
        """
        if language in self.translations:
            self.current_language = language
            logger.info(f"Language set to: {language}")
            return True
        else:
            logger.warning(f"Unsupported language: {language}")
            return False
    
    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """获取指定语言的文本
        
        Args:
            key: 文本键名
            language: 语言代码，如果为None则使用当前语言
            **kwargs: 格式化参数
            
        Returns:
            本地化文本
        """
        if language is None:
            language = self.current_language
        
        if language not in self.translations:
            language = 'zh'  # 默认回退到中文
        
        text = self.translations[language].get(key, key)
        
        # 如果提供了格式化参数，进行格式化
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Text formatting error for key '{key}': {e}")
        
        return text
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用语言列表"""
        return {
            'zh': '中文',
            'en': 'English'
        }
    
    def get_language_name(self, language: str) -> str:
        """获取语言的显示名称"""
        language_names = self.get_available_languages()
        return language_names.get(language, language)

# 全局实例
ui_translations = UITranslations()