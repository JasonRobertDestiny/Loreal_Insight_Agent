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

# 初始化实例
text2sql = Text2SQL()
text2viz = Text2Viz()

# 检测是否是可视化请求的函数（支持多语言）
def is_visualization_query(query):
    """检测查询是否是可视化请求（支持中英文）"""
    # 使用新的多语言关键词检测
    return multilingual_keywords.is_visualization_query(query)

# 定义回调函数
def process_query(message, history):
    """处理用户查询并返回回答"""
    if is_visualization_query(message):
        # 使用Text2Viz处理可视化查询
        df, viz_path = text2viz.visualize(message)
        
        if viz_path and os.path.exists(viz_path):
            # 生成数据摘要，但不显示图片
            summary = generate_data_summary(df)
            return [(message, summary)]
        else:
            # 可视化失败，使用Text2SQL回退
            response = text2sql.query(message)
            return [(message, response)]
    else:
        # 使用Text2SQL处理普通查询
        response = text2sql.query(message)
        return [(message, response)]

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
        'system_theme': ui_translations.get_text('system_theme', current_lang)
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
    
    /* Dark模式适配 - 优化颜色对比度和配色 */
    @media (prefers-color-scheme: dark) {
        :root {
            --loreal-gold: #FFD700;
            --loreal-dark-gold: #FFA500;
            --loreal-hover: #FFFF99;
            --text-primary: #FFFFFF;
            --text-secondary: #E0E0E0;
            --text-muted: #CCCCCC;
            --bg-primary: #1A1A1A;
            --bg-secondary: #2D2D2D;
            --bg-tertiary: #404040;
            --border-color: #555555;
            --shadow-light: rgba(255, 255, 255, 0.1);
            --shadow-medium: rgba(255, 255, 255, 0.15);
        }
    }
    
    /* Gradio dark主题检测 */
    .dark :root {
        --loreal-gold: #FFD700;
        --loreal-dark-gold: #FFA500;
        --loreal-hover: #FFFF99;
        --text-primary: #FFFFFF;
        --text-secondary: #E0E0E0;
        --text-muted: #CCCCCC;
        --bg-primary: #1A1A1A;
        --bg-secondary: #2D2D2D;
        --bg-tertiary: #404040;
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
    
    /* Dark主题下的消息样式优化 - 使用浅灰背景 */
    .dark .chatbot .message.user {
        background: linear-gradient(135deg, var(--loreal-gold) 0%, var(--loreal-dark-gold) 100%) !important;
        color: #000000 !important;
        font-weight: 600 !important;
        text-shadow: none !important;
        margin-left: 4rem !important;
        margin-right: 0.5rem !important;
        text-align: right !important;
    }
    
    .dark .chatbot .message.bot {
        background: #505050 !important;
        border: none !important;
        color: #FFFFFF !important;
        text-shadow: none !important;
        margin-left: 0.5rem !important;
        margin-right: 4rem !important;
        text-align: left !important;
    }
    
    /* 确保聊天界面在dark主题下的可见性 - 使用浅灰背景 */
    .dark .chatbot {
        background: #3A3A3A !important;
        border-color: var(--loreal-gold) !important;
        color: #FFFFFF !important;
    }
    
    /* 强制覆盖Gradio默认样式 */
    .dark .chatbot .message.bot,
    .dark .chatbot .message.bot *,
    .dark .chatbot .message.bot p,
    .dark .chatbot .message.bot span,
    .dark .chatbot .message.bot div,
    .dark .chatbot .message.bot pre,
    .dark .chatbot .message.bot code {
        color: #FFFFFF !important;
        background: transparent !important;
    }
    
    .dark .chatbot .message.user,
    .dark .chatbot .message.user *,
    .dark .chatbot .message.user p,
    .dark .chatbot .message.user span,
    .dark .chatbot .message.user div,
    .dark .chatbot .message.user pre,
    .dark .chatbot .message.user code {
        color: #000000 !important;
        background: transparent !important;
    }
    
    /* 额外的Gradio组件样式覆盖 */
    .dark .gr-chatbot .message,
    .dark .gr-chatbot .message * {
        color: #FFFFFF !important;
    }
    
    .dark .gr-chatbot .user,
    .dark .gr-chatbot .user * {
        color: #000000 !important;
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
        
        # 主要交互区域
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

                # 更新语言状态
                language
            )
        
        # 清空对话功能
        def clear_conversation():
            return [], "", "", ""
        
        # 设置事件处理
        # 语言切换事件
        language_dropdown.change(
            update_interface_language,
            inputs=[language_dropdown],
            outputs=[main_header, feature_cards, precise_title, visual_title, insights_title, language_state]
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