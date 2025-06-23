import os
import sys
import pandas as pd
from text2sql import Text2SQL
from text2viz import Text2Viz
import re
import logging
import gradio as gr
from language_utils import language_detector, multilingual_keywords
from ui_translations import ui_translations
from memory_manager import MemoryManager
from history_service import HistoryService
from history_ui import HistoryUI
import time
import os

# 初始化实例
text2sql = Text2SQL()
text2viz = Text2Viz()
memory_manager = MemoryManager()
history_service = HistoryService(memory_manager)
history_ui = HistoryUI(history_service)

# 检测是否是可视化请求的函数（支持多语言）
def is_visualization_query(query):
    """检测查询是否是可视化请求（支持中英文）"""
    # 使用新的多语言关键词检测
    return multilingual_keywords.is_visualization_query(query)

# 定义回调函数
def process_query(message, history):
    """处理用户查询并返回回答"""
    start_time = time.time()
    
    try:
        if is_visualization_query(message):
            # 使用Text2Viz处理可视化查询
            df, viz_path = text2viz.visualize(message)
            
            if viz_path and os.path.exists(viz_path):
                # 生成数据摘要，但不显示图片
                summary = generate_data_summary(df)
                execution_time = time.time() - start_time
                
                # 记录查询历史
                history_service.record_query(
                    user_query=message,
                    query_type="visualization",
                    result_summary=summary,
                    success=True,
                    execution_time=execution_time
                )
                
                # 更新历史记录显示
                updated_history = history_ui._get_history_list_html()
                
                return [(message, summary)]
            else:
                # 可视化失败，使用Text2SQL回退
                response = text2sql.query(message)
                execution_time = time.time() - start_time
                
                # 记录查询历史
                history_service.record_query(
                    user_query=message,
                    query_type="sql",
                    result_summary=response,
                    success=True,
                    execution_time=execution_time
                )
                
                return [(message, response)]
        else:
            # 使用Text2SQL处理普通查询
            response = text2sql.query(message)
            execution_time = time.time() - start_time
            
            # 记录查询历史
            history_service.record_query(
                user_query=message,
                query_type="sql",
                result_summary=response,
                success=True,
                execution_time=execution_time
            )
            
            return [(message, response)]
    
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = f"查询处理出错: {str(e)}"
        
        # 记录失败的查询
        history_service.record_query(
            user_query=message,
            query_type="unknown",
            result_summary=error_message,
            success=False,
            execution_time=execution_time
        )
        
        return [(message, error_message)]

# 语言切换功能
def change_language(language):
    """切换界面语言"""
    ui_translations.set_language(language)
    # 返回更新后的界面组件
    return create_interface_components()

def get_current_language():
    """获取当前语言"""
    return ui_translations.get_current_language()

# 生成数据摘要
def generate_data_summary(df):
    """生成数据摘要信息"""
    current_lang = ui_translations.get_current_language()
    
    if df.empty:
        return ui_translations.get_text('no_data_message', current_lang)
    
    summary = ui_translations.get_text('data_summary_prefix', current_lang)
    
    # 添加基本统计信息
    summary += ui_translations.get_text('data_rows_info', current_lang, count=len(df))
    
    # 根据数据类型添加更多统计信息
    for col in df.columns:
        if pd.api.types.is_datetime64_dtype(df[col]):
            summary += ui_translations.get_text('date_range_info', current_lang, 
                                              col=col, 
                                              min_date=df[col].min().date(), 
                                              max_date=df[col].max().date())
        elif pd.api.types.is_numeric_dtype(df[col]):
            summary += ui_translations.get_text('numeric_stats_info', current_lang,
                                              col=col,
                                              sum=df[col].sum(),
                                              avg=df[col].mean())
    
    return summary

# 创建界面组件
def create_interface_components():
    """创建多语言界面组件"""
    current_lang = ui_translations.get_current_language()
    
    # 返回界面文本字典
    return {
        'app_title': ui_translations.get_text('app_title', current_lang),
        'app_description': ui_translations.get_text('app_description', current_lang),
        'smart_query_title': ui_translations.get_text('smart_query_title', current_lang),
        'smart_query_desc': ui_translations.get_text('smart_query_desc', current_lang),
        'data_viz_title': ui_translations.get_text('data_viz_title', current_lang),
        'data_viz_desc': ui_translations.get_text('data_viz_desc', current_lang),
        'smart_insight_title': ui_translations.get_text('smart_insight_title', current_lang),
        'smart_insight_desc': ui_translations.get_text('smart_insight_desc', current_lang),
        'chat_history': ui_translations.get_text('chat_history', current_lang),
        'input_placeholder': ui_translations.get_text('input_placeholder', current_lang),
        'send_button': ui_translations.get_text('send_button', current_lang),
        'clear_button': ui_translations.get_text('clear_button', current_lang),
        'tech_details': ui_translations.get_text('tech_details', current_lang),
        'sql_query_label': ui_translations.get_text('sql_query_label', current_lang),
        'sql_placeholder': ui_translations.get_text('sql_placeholder', current_lang),
        'result_label': ui_translations.get_text('result_label', current_lang),
        'result_placeholder': ui_translations.get_text('result_placeholder', current_lang),
        'precise_query': ui_translations.get_text('precise_query', current_lang),
        'visual_display': ui_translations.get_text('visual_display', current_lang),
        'smart_insights': ui_translations.get_text('smart_insights', current_lang),
        'examples_precise': ui_translations.get_text('examples_precise', current_lang),
        'examples_visual': ui_translations.get_text('examples_visual', current_lang),
        'examples_insights': ui_translations.get_text('examples_insights', current_lang),
        'language_setting': ui_translations.get_text('language_setting', current_lang),
        'theme_setting': ui_translations.get_text('theme_setting', current_lang),
        'light_theme': ui_translations.get_text('light_theme', current_lang),
        'dark_theme': ui_translations.get_text('dark_theme', current_lang),
        'system_theme': ui_translations.get_text('system_theme', current_lang),
        # 历史记录相关
        'history_title': ui_translations.get_text('history_title', current_lang),
        'search_placeholder': ui_translations.get_text('search_placeholder', current_lang),
        'search_button': ui_translations.get_text('search_button', current_lang),
        'refresh_button': ui_translations.get_text('refresh_button', current_lang),
        'export_history': ui_translations.get_text('export_history', current_lang),
        'clear_history': ui_translations.get_text('clear_history', current_lang),
        'back_to_chat': ui_translations.get_text('back_to_chat', current_lang),
        'query_time': ui_translations.get_text('query_time', current_lang),
        'query_type': ui_translations.get_text('query_type', current_lang),
        'total_queries': ui_translations.get_text('total_queries', current_lang),
        'success': ui_translations.get_text('success', current_lang),
        'failed': ui_translations.get_text('failed', current_lang),
        'avg_time': ui_translations.get_text('avg_time', current_lang)
    }

# 创建Gradio界面
def create_combined_interface():
    """创建集成Text2SQL和Text2Viz的Gradio界面"""
    # 欧莱雅品牌风格的自定义CSS样式
    custom_css = """
    /* L'Oréal 品牌色彩定义 - Light主题优化 */
    :root {
        --loreal-gold: #F4C430;
        --loreal-dark-gold: #DAA520;
        --loreal-hover: #FFD700;
        --loreal-black: #2C2C2C;
        --loreal-dark-gray: #4A4A4A;
        --loreal-light-gray: #F8F9FA;
        --loreal-white: #FFFFFF;
        --loreal-accent: #CD853F;
        
        /* Light主题优化颜色 - 更明亮的配色 */
        --text-primary: #2C2C2C;
        --text-secondary: #4A4A4A;
        --text-muted: #6C757D;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8F9FA;
        --bg-tertiary: #E9ECEF;
        --border-color: #DEE2E6;
        --shadow-light: rgba(0, 0, 0, 0.08);
        --shadow-medium: rgba(0, 0, 0, 0.12);
    }
    
    /* Dark模式适配 - 优化颜色对比度和配色，使用深黄色文字和浅黑背景 */
    @media (prefers-color-scheme: dark) {
        :root {
            --loreal-gold: #FFD700;
            --loreal-dark-gold: #FFA500;
            --loreal-hover: #FFFF99;
            --text-primary: #DAA520;
            --text-secondary: #B8860B;
            --text-muted: #CD853F;
            --bg-primary: #2A2A2A;
            --bg-secondary: #3A3A3A;
            --bg-tertiary: #4A4A4A;
            --border-color: #555555;
            --shadow-light: rgba(255, 255, 255, 0.1);
            --shadow-medium: rgba(255, 255, 255, 0.15);
        }
    }
    
    /* Gradio dark主题检测 - 使用深黄色文字和浅黑背景 */
    .dark :root {
        --loreal-gold: #FFD700;
        --loreal-dark-gold: #FFA500;
        --loreal-hover: #FFFF99;
        --text-primary: #DAA520;
        --text-secondary: #B8860B;
        --text-muted: #CD853F;
        --bg-primary: #2A2A2A;
        --bg-secondary: #3A3A3A;
        --bg-tertiary: #4A4A4A;
        --border-color: #555555;
        --shadow-light: rgba(255, 255, 255, 0.1);
        --shadow-medium: rgba(255, 255, 255, 0.15);
    }
    
    /* 全局样式优化 */
    .gradio-container {
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif !important;
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
        color: var(--text-primary) !important;
    }
    
    /* 确保所有文本元素使用正确的颜色 */
    .gradio-container label,
    .gradio-container .gr-form label,
    .gradio-container .gr-box label,
    .gradio-container h1, .gradio-container h2, .gradio-container h3, .gradio-container h4,
    .gradio-container p, .gradio-container span, .gradio-container div {
        color: var(--text-primary) !important;
    }
    
    .gradio-container .secondary-text {
        color: var(--text-secondary) !important;
    }
    
    /* Dark主题下的特殊文本处理 */
    .dark .gradio-container,
    .dark .gradio-container * {
        color: var(--text-primary) !important;
    }
    
    .dark .gradio-container .secondary-text {
        color: var(--text-secondary) !important;
    }
    
    /* 确保输入框在dark主题下可见 */
    .dark .gradio-container input,
    .dark .gradio-container textarea {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }
    
    .dark .gradio-container input::placeholder,
    .dark .gradio-container textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* 主标题区域 - 欧莱雅风格 - 紧凑设计 */
    .main-header {
        background: linear-gradient(135deg, var(--loreal-black) 0%, var(--loreal-dark-gray) 50%, var(--loreal-gold) 100%);
        color: var(--loreal-white);
        padding: 1.5rem 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(212, 175, 55, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header h1, .main-header p {
        color: var(--loreal-white) !important;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23D4AF37" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
        opacity: 0.3;
        z-index: 1;
        pointer-events: none;
    }
    
    .main-header h1 {
        position: relative;
        z-index: 3;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        background: linear-gradient(45deg, var(--loreal-white), var(--loreal-gold));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        position: relative;
        z-index: 3;
        color: var(--loreal-light-gray);
    }
    
    /* 功能卡片 - 欧莱雅风格 - 紧凑设计 */
    .feature-card {
        background: linear-gradient(145deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(26, 26, 26, 0.1);
        border: 1px solid var(--loreal-gold);
        background-clip: padding-box;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card h3 {
        color: var(--text-primary) !important;
        position: relative;
        z-index: 2;
    }
    
    .feature-card p {
        color: var(--text-secondary) !important;
        position: relative;
        z-index: 2;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--loreal-gold), var(--loreal-dark-gold));
        transform: scaleX(0);
        transition: transform 0.3s ease;
        z-index: 1;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(26, 26, 26, 0.2);
        border-color: var(--loreal-gold);
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-card h3 {
        color: var(--text-primary) !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .feature-card p {
        color: var(--text-secondary) !important;
        line-height: 1.6;
    }
    
    /* 聊天界面优化 - 增大尺寸和美化 */
    .chatbot {
        border: 2px solid var(--loreal-gold) !important;
        border-radius: 20px !important;
        background: linear-gradient(145deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        box-shadow: 0 12px 40px var(--shadow-medium) !important;
        color: var(--text-primary) !important;
        min-height: 600px !important;
        padding: 1rem !important;
    }
    
    /* 聊天消息气泡优化 - 简化样式 */
    .chatbot .message {
        background: var(--bg-primary) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        margin: 0.3rem 0 !important;
        box-shadow: none !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    /* 用户消息样式 - 靠右对齐 */
    .chatbot .message.user {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-hover) 100%) !important;
        color: var(--loreal-black) !important;
        margin-left: 4rem !important;
        margin-right: 0.5rem !important;
        text-align: right !important;
    }
    
    /* 助手消息样式 - 靠左对齐 */
    .chatbot .message.bot {
        background: var(--bg-primary) !important;
        border: none !important;
        margin-left: 0.5rem !important;
        margin-right: 4rem !important;
        color: var(--text-primary) !important;
        text-align: left !important;
    }
      /* Dark主题下的消息样式优化 - 使用明亮的金黄色文字和更亮的背景 */
    .dark .chatbot .message.user {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000000 !important;
        font-weight: 700 !important;
        text-shadow: none !important;
        margin-left: 4rem !important;
        margin-right: 0.5rem !important;
        text-align: right !important;
        border: 2px solid #FFD700 !important;
    }
    
    .dark .chatbot .message.bot {
        background: #505050 !important;
        border: 2px solid #FFD700 !important;
        color: #FFD700 !important;
        font-weight: 600 !important;
        text-shadow: none !important;
        margin-left: 0.5rem !important;
        margin-right: 4rem !important;
        text-align: left !important;
    }
    
    /* 确保聊天界面在dark主题下的可见性 - 使用更亮的背景 */
    .dark .chatbot {
        background: #3A3A3A !important;
        border-color: #FFD700 !important;
        color: #FFD700 !important;
    }
    
    /* 强制覆盖Gradio默认样式 - 使用明亮的金黄色文字 */
    .dark .chatbot .message.bot,
    .dark .chatbot .message.bot *,
    .dark .chatbot .message.bot p,
    .dark .chatbot .message.bot span,
    .dark .chatbot .message.bot div,
    .dark .chatbot .message.bot pre,
    .dark .chatbot .message.bot code,
    .dark .chatbot .message.bot strong,
    .dark .chatbot .message.bot em {
        color: #FFD700 !important;
        background: transparent !important;
        font-weight: 600 !important;
    }
    
    .dark .chatbot .message.user,
    .dark .chatbot .message.user *,
    .dark .chatbot .message.user p,
    .dark .chatbot .message.user span,
    .dark .chatbot .message.user div,
    .dark .chatbot .message.user pre,
    .dark .chatbot .message.user code,
    .dark .chatbot .message.user strong,
    .dark .chatbot .message.user em {
        color: #000000 !important;
        background: transparent !important;
        font-weight: 700 !important;
    }
    
    /* 额外的Gradio组件样式覆盖 - 使用明亮的金黄色文字 */
    .dark .gr-chatbot .message,
    .dark .gr-chatbot .message *,
    .dark .gr-chatbot .message p,
    .dark .gr-chatbot .message span,
    .dark .gr-chatbot .message div {
        color: #FFD700 !important;
        font-weight: 600 !important;
    }
    
    .dark .gr-chatbot .user,
    .dark .gr-chatbot .user *,
    .dark .gr-chatbot .user p,
    .dark .gr-chatbot .user span,
    .dark .gr-chatbot .user div {
        color: #000000 !important;
        font-weight: 700 !important;
    }
      /* 特别针对Gradio聊天机器人组件的样式强化 */
    .dark [data-testid="chatbot"] .message,
    .dark [data-testid="chatbot"] .message *,
    .dark .gradio-chatbot .message,
    .dark .gradio-chatbot .message * {
        color: #FFD700 !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .dark [data-testid="chatbot"] .user,
    .dark [data-testid="chatbot"] .user *,
    .dark .gradio-chatbot .user,
    .dark .gradio-chatbot .user * {
        color: #000000 !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }
    
    /* 最强制的CSS覆盖 - 针对所有可能的Gradio聊天组件 */
    .dark .gr-chatbot,
    .dark .gr-chatbot *,
    .dark .chatbot,
    .dark .chatbot *,
    .dark [class*="chatbot"],
    .dark [class*="chatbot"] *,
    .dark [id*="chatbot"],
    .dark [id*="chatbot"] * {
        color: #FFD700 !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFD700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    }
    
    /* 用户消息特殊处理 */
    .dark .gr-chatbot .user,
    .dark .gr-chatbot .user *,
    .dark .chatbot .user,
    .dark .chatbot .user *,
    .dark [class*="chatbot"] .user,
    .dark [class*="chatbot"] .user * {
        color: #000000 !important;
        background-color: #FFD700 !important;
        font-weight: 700 !important;
        -webkit-text-fill-color: #000000 !important;
        text-shadow: none !important;
    }
    
    /* 针对具体的聊天消息容器 */
    .dark .message,
    .dark .message *,
    .dark [class*="message"],
    .dark [class*="message"] * {
        color: #FFD700 !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFD700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    }
    
    /* 针对Gradio的具体聊天组件选择器 */
    .dark .svelte-1f354aw,
    .dark .svelte-1f354aw *,
    .dark .prose,
    .dark .prose * {
        color: #FFD700 !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFD700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    }
    
    /* 通用文本元素强制覆盖 */
    .dark p,
    .dark span,
    .dark div:not(.header):not(.footer) {
        color: #FFD700 !important;
        -webkit-text-fill-color: #FFD700 !important;
    }
    
    /* 输入框和按钮优化 */
    .input-container {
        background: linear-gradient(145deg, var(--bg-primary), var(--bg-secondary));
        border: 2px solid var(--loreal-gold);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 4px 16px rgba(212, 175, 55, 0.1);
    }
    
    /* 按钮样式 - 欧莱雅风格 */
    .btn-primary {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-dark-gold) 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: var(--loreal-black) !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(212, 175, 55, 0.3) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .btn-primary:hover {
        background: linear-gradient(135deg, var(--loreal-hover) 0%, var(--loreal-gold) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(212, 175, 55, 0.4) !important;
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--text-secondary) 100%) !important;
        border: 2px solid var(--loreal-gold) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .btn-secondary:hover {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-dark-gold) 100%) !important;
        color: var(--loreal-black) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* 示例查询区域优化 - 紧凑设计 */
    .example-section {
        background: linear-gradient(145deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--loreal-gold);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 0.5rem;
        box-shadow: 0 3px 10px rgba(212, 175, 55, 0.08);
    }
    
    .example-section h3, .example-section h4 {
        color: var(--text-primary) !important;
    }
    
    .example-section:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(212, 175, 55, 0.2);
    }
    
    .example-query {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border: 1px solid var(--loreal-gold);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .example-query:hover {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-hover) 100%);
        color: var(--loreal-black);
        transform: scale(1.02);
        box-shadow: 0 4px 16px rgba(212, 175, 55, 0.3);
    }
    
    /* Dark主题下的示例查询样式 */
    .dark .example-query {
        background: var(--bg-secondary) !important;
        border-color: var(--loreal-gold) !important;
        color: var(--text-primary) !important;
    }
    
    .dark .example-query:hover {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-dark-gold) 100%) !important;
        color: #000000 !important;
    }
    
    /* Dark主题下的按钮样式 */
    .dark .btn-primary {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-dark-gold) 100%) !important;
        color: #000000 !important;
    }
    
    .dark .btn-secondary {
        background: var(--bg-secondary) !important;
        border-color: var(--loreal-gold) !important;
        color: var(--text-primary) !important;
    }
    
    .dark .btn-secondary:hover {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-dark-gold) 100%) !important;
        color: #000000 !important;
    }
    
    .example-section h3 {
        color: var(--text-primary) !important;
        font-weight: 700;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
        text-align: center;
        position: relative;
    }
    
    .example-section h3::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, var(--loreal-gold) 0%, var(--loreal-hover) 100%);
        border-radius: 2px;
    }
    
    .example-section h4 {
        color: var(--loreal-dark-gray) !important;
        font-weight: 600;
        border-bottom: 2px solid var(--loreal-gold);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* 技术详情面板 */
    .accordion {
        background: linear-gradient(145deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        border: 2px solid var(--loreal-gold) !important;
        border-radius: 16px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.1) !important;
        overflow: hidden !important;
    }
    
    /* 确保手风琴默认收起 */
    .gradio-accordion:not(.open) .gradio-accordion-content {
        display: none !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    
    .gradio-accordion.open .gradio-accordion-content {
        display: block !important;
        height: auto !important;
    }
    
    /* Gradio手风琴组件样式修复 */
    .gradio-container .accordion {
        overflow: visible !important;
    }
    
    .gradio-container .accordion > div:last-child {
        transition: all 0.3s ease !important;
    }
    
    .accordion-header {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-dark-gold) 100%) !important;
        color: var(--loreal-black) !important;
        font-weight: 700 !important;
        padding: 1.5rem !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    .accordion-header:hover {
        background: linear-gradient(135deg, var(--loreal-hover) 0%, var(--loreal-gold) 100%) !important;
        transform: translateY(-2px) !important;
    }
    
    .accordion-content {
        background: var(--bg-primary) !important;
        padding: 2rem !important;
        border-top: 1px solid var(--loreal-gold) !important;
        color: var(--text-primary) !important;
    }
    
    /* 输入框样式 */
    .textbox {
        border: 2px solid var(--loreal-gold) !important;
        border-radius: 12px !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .textbox:focus {
        border-color: var(--loreal-hover) !important;
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.2) !important;
        outline: none !important;
    }
      /* 输入框占位符文本 */
    .textbox::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.7;
    }
    
    /* 修复Gradio暗色主题下输入框文字不可见的问题 */
    .dark .gr-textbox input,
    .dark .gr-textbox textarea,
    .dark input[type="text"],
    .dark textarea {
        background: #3A3A3A !important;
        color: #DAA520 !important;
        border: 2px solid var(--loreal-gold) !important;
        border-radius: 8px !important;
    }
    
    .dark .gr-textbox input:focus,
    .dark .gr-textbox textarea:focus,
    .dark input[type="text"]:focus,
    .dark textarea:focus {
        background: #3A3A3A !important;
        color: #DAA520 !important;
        border-color: var(--loreal-hover) !important;
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3) !important;
    }
    
    .dark .gr-textbox input::placeholder,
    .dark .gr-textbox textarea::placeholder,
    .dark input[type="text"]::placeholder,
    .dark textarea::placeholder {
        color: #B8860B !important;
        opacity: 0.8 !important;
    }
      /* 强制覆盖所有输入相关元素的文字颜色 */
    .dark [data-testid="textbox"] input,
    .dark [data-testid="textbox"] textarea,
    .dark .gr-form input,
    .dark .gr-form textarea {
        color: #DAA520 !important;
        background: #3A3A3A !important;
    }
    
    /* 额外的输入框样式强制覆盖 - 确保在所有情况下都可见 */
    .dark .gradio-container input[type="text"],
    .dark .gradio-container textarea,
    .dark .gradio-container .gr-textbox input,
    .dark .gradio-container .gr-textbox textarea,
    .dark .gradio-container .gr-box input,
    .dark .gradio-container .gr-box textarea,
    .dark input,
    .dark textarea {
        background-color: #3A3A3A !important;
        color: #FFD700 !important;
        border: 2px solid #DAA520 !important;
        border-radius: 8px !important;
        -webkit-text-fill-color: #FFD700 !important;
        text-shadow: none !important;
    }
    
    /* 输入框焦点状态 */
    .dark .gradio-container input[type="text"]:focus,
    .dark .gradio-container textarea:focus,
    .dark .gradio-container .gr-textbox input:focus,
    .dark .gradio-container .gr-textbox textarea:focus,
    .dark input:focus,
    .dark textarea:focus {
        background-color: #404040 !important;
        color: #FFD700 !important;
        border-color: #FFA500 !important;
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3) !important;
        outline: none !important;
        -webkit-text-fill-color: #FFD700 !important;
    }
    
    /* 输入框占位符文本在深色主题下 */
    .dark .gradio-container input::placeholder,
    .dark .gradio-container textarea::placeholder,
    .dark input::placeholder,
    .dark textarea::placeholder {
        color: #B8860B !important;
        opacity: 0.8 !important;
        -webkit-text-fill-color: #B8860B !important;
    }
    
    /* 针对Gradio特定的输入组件 */
    .dark .gr-chatbot-input input,
    .dark .gr-chatbot-input textarea {
        background-color: #3A3A3A !important;
        color: #FFD700 !important;
        border: 2px solid #DAA520 !important;
        -webkit-text-fill-color: #FFD700 !important;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem !important;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
        
        .example-section {
            padding: 1.5rem;
        }
        
        .btn-primary, .btn-secondary {
            padding: 0.6rem 1.5rem !important;
            font-size: 0.9rem !important;
        }
    }
    """
    
    # 获取界面文本
    texts = create_interface_components()
    
    with gr.Blocks(title=texts['app_title'], theme=gr.themes.Soft(), css=custom_css) as interface:
        # 语言设置状态
        language_state = gr.State(value=ui_translations.get_current_language())
        
        # 设置面板
        with gr.Row():
            with gr.Column(scale=4):
                pass  # 占位符
            with gr.Column(scale=1):
                with gr.Group():
                    language_dropdown = gr.Dropdown(
                        choices=[(ui_translations.get_language_name(lang), lang) 
                                for lang in ui_translations.get_available_languages().keys()],
                        value=ui_translations.get_current_language(),
                        label=texts['language_setting'],
                        interactive=True
                    )
        
        # 主界面内容
        
        # 主标题区域 - 紧凑设计
        main_header = gr.HTML(
            f"""
            <div class="main-header">
                <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">{texts['app_title']}</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">{texts['app_description']}</p>
            </div>
            """
        )
        
        # 功能介绍卡片 - 简洁设计
        feature_cards = gr.HTML(
            f"""
            <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                <div class="feature-card" style="flex: 1;">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">{texts['smart_query_title']}</h3>
                    <p style="margin: 0; font-size: 0.9rem;">{texts['smart_query_desc']}</p>
                </div>
                <div class="feature-card" style="flex: 1;">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">{texts['data_viz_title']}</h3>
                    <p style="margin: 0; font-size: 0.9rem;">{texts['data_viz_desc']}</p>
                </div>
                <div class="feature-card" style="flex: 1;">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">{texts['smart_insight_title']}</h3>
                    <p style="margin: 0; font-size: 0.9rem;">{texts['smart_insight_desc']}</p>
                </div>
            </div>
            """
        )
        
        # 主要交互区域 - 使用标签页
        with gr.Tabs() as main_tabs:
            # 主聊天页面
            with gr.TabItem("💬 智能对话", elem_id="chat_tab"):
                with gr.Row():
                    with gr.Column(scale=2):
                        # 聊天组件 - 增大尺寸设计
                        chatbot = gr.Chatbot(
                            height=600, 
                            label=texts['chat_history'],
                            type="messages",
                            show_copy_button=True,
                            layout="panel"
                        )
                        
                        # 输入区域 - 紧凑设计
                        with gr.Group():
                            msg = gr.Textbox(
                                placeholder=texts['input_placeholder'], 
                                label="",
                                lines=3,
                                max_lines=6,
                                show_label=False,
                                container=False,
                                scale=4
                            )
                            with gr.Row():
                                submit_btn = gr.Button(
                                    texts['send_button'], 
                                    variant="primary",
                                    scale=1
                                )
                                clear_btn = gr.Button(
                                    texts['clear_button'], 
                                    variant="secondary",
                                    scale=1
                                )
                    
                    with gr.Column(scale=1):
                        # 技术详情面板 - 默认展开
                        with gr.Accordion(texts['tech_details'], open=True):
                            sql_display = gr.Textbox(
                                label=texts['sql_query_label'], 
                                lines=6, 
                                interactive=False,
                                placeholder=texts['sql_placeholder']
                            )
                            result_display = gr.Textbox(
                                label=texts['result_label'], 
                                lines=10, 
                                interactive=False,
                                placeholder=texts['result_placeholder']
                            )
            
            # 历史记录页面
            with gr.TabItem("📊 查询历史", elem_id="history_tab") as history_tab:
                with gr.Row():
                    with gr.Column():
                        # 页面标题
                        history_page_title = gr.HTML(
                            f"""
                            <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
                                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 {texts['history_title']}</h1>
                                <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">实时同步 • 智能搜索 • 数据导出</p>
                            </div>
                            """
                        )
                        
                        # 控制面板
                        with gr.Row():
                            with gr.Column(scale=2):
                                search_input = gr.Textbox(
                                    placeholder=texts['search_placeholder'],
                                    label=f"🔍 {texts['search_button']}",
                                    lines=1
                                )
                            with gr.Column(scale=1):
                                with gr.Row():
                                    refresh_btn = gr.Button(f"🔄 刷新", size="sm")
                                    export_btn = gr.Button(f"📥 {texts['export_history']}", size="sm")
                                    clear_history_btn = gr.Button(f"🗑️ {texts['clear_history']}", size="sm", variant="stop")
                        
                        # 历史记录表格
                        history_table = gr.Dataframe(
                            headers=[texts['query_time'], "查询", texts['query_type'], "状态"],
                            datatype=["str", "str", "str", "str"],
                            interactive=False,
                            wrap=True,
                            column_widths=["20%", "50%", "15%", "15%"]
                        )
                        
                        # 统计信息
                        stats_display = gr.HTML(
                            f"""
                            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px; font-size: 1rem;">
                                <span style="margin-right: 30px;">📊 {texts['total_queries']}: 0</span>
                                <span style="margin-right: 30px;">✅ {texts['success']}: 0</span>
                                <span style="margin-right: 30px;">❌ {texts['failed']}: 0</span>
                                <span>⏱️ {texts['avg_time']}: 0.0s</span>
                            </div>
                            """
                        )
                        
                        # 操作结果显示
                        operation_result = gr.HTML(visible=False)
        
        # 示例查询区域 - 优化设计
        with gr.Row():
            with gr.Column():
                # 示例查询 - 保留必要示例
                with gr.Row():
                    with gr.Column(scale=1):
                        precise_title = gr.HTML(f"<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>{texts['precise_query']}</h4>")
                        precise_examples = gr.Examples(
                            examples=texts['examples_precise'],
                            inputs=msg,
                            elem_id="precise_examples"
                        )
                    
                    with gr.Column(scale=1):
                        visual_title = gr.HTML(f"<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>{texts['visual_display']}</h4>")
                        visual_examples = gr.Examples(
                            examples=texts['examples_visual'],
                            inputs=msg,
                            elem_id="visual_examples"
                        )
                    
                    with gr.Column(scale=1):
                        insights_title = gr.HTML(f"<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>{texts['smart_insights']}</h4>")
                        insights_examples = gr.Examples(
                            examples=texts['examples_insights'],
                            inputs=msg,
                            elem_id="insights_examples"
                        )
        

        
        # 添加隐藏的HTML组件用于执行JavaScript
        js_executor = gr.HTML(visible=False)
        
        # 定义回调函数
        def user_input(user_message, history):
            # 处理用户输入 - 使用messages格式
            return "", history + [{"role": "user", "content": user_message}]
        
        # 定义回调函数
        def bot_response(history):
            try:
                # 获取最后一条用户消息
                user_message = history[-1]["content"]
                
                # 使用LLM判断对话类型并获取回答
                conv_type, answer = text2sql.llm.classify_conversation(user_message)
                
                # 如果是普通对话，直接返回回答
                if conv_type == "general":
                    history.append({"role": "assistant", "content": answer})
                    return history, "", ""
                
                # 如果是数据查询，继续原有的处理逻辑
                if is_visualization_query(user_message):
                    # 处理可视化查询
                    df, viz_path, sql_query = text2viz.visualize(user_message)
                    
                    if viz_path and os.path.exists(viz_path):
                        summary = generate_data_summary(df)
                        db_result = df.head(10).to_string(index=False) if not df.empty else "无数据"
                        
                        # 添加文本摘要回复
                        history.append({"role": "assistant", "content": summary})
                        
                        # 追加图片消息
                        history.append({"role": "assistant", "content": {"path": viz_path}})
                        
                        return history, sql_query, db_result
                    else:
                        # 可视化失败，使用Text2SQL回退
                        response, sql_query, db_result = text2sql.query(user_message)
                        # 添加文本回复
                        history.append({"role": "assistant", "content": response})
                        return history, sql_query, db_result
                else:
                    # 处理普通文本查询
                    response, sql_query, db_result = text2sql.query(user_message)
                    # 添加回复
                    history.append({"role": "assistant", "content": response})
                    return history, sql_query, db_result
                    
            except Exception as e:
                # 错误处理 - 多语言支持
                current_lang = ui_translations.get_current_language()
                if current_lang == 'en':
                    error_msg = f"Sorry, an error occurred while processing your request: {str(e)}"
                else:
                    error_msg = f"抱歉，处理您的请求时发生错误：{str(e)}"
                
                history.append({"role": "assistant", "content": error_msg})
                logging.error(f"Bot response error: {str(e)}")
                return history, "", ""
        
        # 语言切换处理函数
        def update_interface_language(language):
            """更新界面语言"""
            ui_translations.set_language(language)
            new_texts = create_interface_components()
            
            # 返回更新后的界面组件
            return (
                # 主标题
                f"""
                <div class="main-header">
                    <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">{new_texts['app_title']}</h1>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">{new_texts['app_description']}</p>
                </div>
                """,
                # 功能卡片
                f"""
                <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                    <div class="feature-card" style="flex: 1;">
                        <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">{new_texts['smart_query_title']}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">{new_texts['smart_query_desc']}</p>
                    </div>
                    <div class="feature-card" style="flex: 1;">
                        <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">{new_texts['data_viz_title']}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">{new_texts['data_viz_desc']}</p>
                    </div>
                    <div class="feature-card" style="flex: 1;">
                        <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">{new_texts['smart_insight_title']}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">{new_texts['smart_insight_desc']}</p>
                    </div>
                </div>
                """,
                # 示例查询标题
                f"<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>{new_texts['precise_query']}</h4>",
                f"<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>{new_texts['visual_display']}</h4>",
                f"<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>{new_texts['smart_insights']}</h4>",
                # 历史记录页面标题
                f"""
                <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
                    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 {new_texts['history_title']}</h1>
                    <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">实时同步 • 智能搜索 • 数据导出</p>
                </div>
                """,
                # 历史记录统计信息
                f"""
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px; font-size: 1rem;">
                    <span style="margin-right: 30px;">📊 {new_texts['total_queries']}: 0</span>
                    <span style="margin-right: 30px;">✅ {new_texts['success']}: 0</span>
                    <span style="margin-right: 30px;">❌ {new_texts['failed']}: 0</span>
                    <span>⏱️ {new_texts['avg_time']}: 0.0s</span>
                </div>
                """,
                # 更新语言状态
                language
            )
        
        # 清空对话功能
        def clear_conversation():
            return [], "", "", ""
        
        # 历史记录相关功能函数
        def get_history_data(search_query=""):
            """获取历史记录数据"""
            try:
                current_lang = ui_translations.get_current_language()
                
                # 获取最近的历史记录
                history_records = history_service.get_recent_queries(days=30, limit=100)
                
                if not history_records:
                    no_history_text = ui_translations.get_text('no_history', current_lang)
                    return [], f"<div style='padding: 10px; background: #f8f9fa; border-radius: 5px; font-size: 0.9rem;'>📊 {no_history_text}</div>"
                
                # 转换为表格数据
                table_data = []
                for record in history_records:
                    # 搜索过滤
                    if search_query and search_query.lower() not in record.user_query.lower():
                        continue
                        
                    # 根据语言显示状态文本
                    status_text = ui_translations.get_text('success', current_lang) if record.success else ui_translations.get_text('failed', current_lang)
                    
                    table_data.append([
                        record.timestamp.strftime("%Y-%m-%d %H:%M"),
                        record.user_query[:100] + "..." if len(record.user_query) > 100 else record.user_query,
                        record.query_type,
                        status_text
                    ])
                
                # 生成统计信息
                total_count = len(history_records)
                success_count = sum(1 for r in history_records if r.success)
                fail_count = total_count - success_count
                avg_time = sum(r.execution_time for r in history_records if r.execution_time) / total_count if total_count > 0 else 0
                
                # 获取多语言文本
                total_queries_text = ui_translations.get_text('total_queries', current_lang)
                success_text = ui_translations.get_text('success', current_lang)
                failed_text = ui_translations.get_text('failed', current_lang)
                avg_time_text = ui_translations.get_text('avg_time', current_lang)
                
                stats_html = f"""
                <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; font-size: 0.9rem;">
                    <span style="margin-right: 20px;">📊 {total_queries_text}: {total_count}</span>
                    <span style="margin-right: 20px;">✅ {success_text}: {success_count}</span>
                    <span style="margin-right: 20px;">❌ {failed_text}: {fail_count}</span>
                    <span>⏱️ {avg_time_text}: {avg_time:.2f}s</span>
                </div>
                """
                
                return table_data, stats_html
                
            except Exception as e:
                current_lang = ui_translations.get_current_language()
                if current_lang == 'en':
                    error_msg = f"Error getting history: {str(e)}"
                else:
                    error_msg = f"获取历史记录时出错: {str(e)}"
                return [], f"<div style='padding: 10px; background: #ffe6e6; border-radius: 5px; color: #d63384;'>❌ {error_msg}</div>"
        
        def refresh_history():
            """刷新历史记录"""
            return get_history_data()
        
        def search_history(search_query):
            """搜索历史记录"""
            return get_history_data(search_query)
        
        def export_history():
            """导出历史记录"""
            try:
                current_lang = ui_translations.get_current_language()
                export_path = history_service.export_history()
                if export_path and os.path.exists(export_path):
                    if current_lang == 'en':
                        return f"✅ History exported to: {export_path}"
                    else:
                        return f"✅ 历史记录已导出到: {export_path}"
                else:
                    if current_lang == 'en':
                        return "❌ Export failed"
                    else:
                        return "❌ 导出失败"
            except Exception as e:
                current_lang = ui_translations.get_current_language()
                if current_lang == 'en':
                    return f"❌ Export error: {str(e)}"
                else:
                    return f"❌ 导出出错: {str(e)}"
        
        def clear_all_history():
            """清空所有历史记录"""
            try:
                current_lang = ui_translations.get_current_language()
                history_service.clear_history()
                if current_lang == 'en':
                    success_msg = "✅ History cleared"
                else:
                    success_msg = "✅ 历史记录已清空"
                return [], f"<div style='padding: 10px; background: #d1ecf1; border-radius: 5px; color: #0c5460;'>{success_msg}</div>"
            except Exception as e:
                current_lang = ui_translations.get_current_language()
                if current_lang == 'en':
                    error_msg = f"Error clearing history: {str(e)}"
                else:
                    error_msg = f"清空历史记录时出错: {str(e)}"
                return [], f"<div style='padding: 10px; background: #ffe6e6; border-radius: 5px; color: #d63384;'>❌ {error_msg}</div>"
        
        def toggle_history_panel():
            """切换历史记录面板显示状态"""
            # 当点击历史记录按钮时，自动刷新数据
            return get_history_data()
        
        # 设置事件处理
        # 语言切换事件
        def update_examples_and_interface(language):
            """更新界面语言和示例查询"""
            ui_translations.set_language(language)
            new_texts = create_interface_components()
            
            # 更新示例查询
            precise_examples.examples = new_texts['examples_precise']
            visual_examples.examples = new_texts['examples_visual']
            insights_examples.examples = new_texts['examples_insights']
            
            # 调用原有的界面更新函数
            return update_interface_language(language)
        
        language_dropdown.change(
            update_examples_and_interface,
            inputs=[language_dropdown],
            outputs=[main_header, feature_cards, precise_title, visual_title, insights_title, history_page_title, stats_display, language_state]
        )
        
        # 消息提交事件
        msg.submit(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, [chatbot, sql_display, result_display]
        )
        submit_btn.click(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, [chatbot, sql_display, result_display]
        )
        clear_btn.click(
            clear_conversation, 
            outputs=[chatbot, msg, sql_display, result_display]
        )
        
        # 标签页切换函数
        def switch_to_history_tab():
            """切换到历史记录标签页并刷新数据"""
            table_data, stats_html = get_history_data()
            return gr.Tabs(selected=1), table_data, stats_html
        
        # 初始化历史记录数据
        def load_initial_history():
            """页面加载时初始化历史记录数据"""
            table_data, stats_html = get_history_data()
            return table_data, stats_html
        
        # 页面加载时初始化历史记录
        interface.load(
            load_initial_history,
            outputs=[history_table, stats_display]
        )
        
        # 历史记录相关事件处理
        
        # 刷新按钮事件
        refresh_btn.click(
            refresh_history,
            outputs=[history_table, stats_display]
        )
        
        # 搜索事件
        search_input.submit(
            search_history,
            inputs=[search_input],
            outputs=[history_table, stats_display]
        )
        
        # 导出按钮事件
        def handle_export():
            result = export_history()
            return gr.HTML(value=f"<div style='padding: 10px; background: #d1ecf1; border-radius: 5px; color: #0c5460; margin-top: 10px;'>{result}</div>", visible=True)
        
        export_btn.click(
            handle_export,
            outputs=[operation_result]
        )
        
        # 清空历史记录按钮事件
        clear_history_btn.click(
            clear_all_history,
            outputs=[history_table, stats_display]
        )
    
    return interface

# 主函数
# 修改main函数中的日志配置
def main():
    # 设置基本日志级别 - 只在控制台显示INFO级别以上的日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logging.info("=== 应用启动 ===")
    
    # 创建界面
    interface = create_combined_interface()
    # 启动服务
    interface.launch(share=False)

if __name__ == "__main__":
    main()