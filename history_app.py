#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的查询历史记录应用
支持实时同步、搜索、导出、清空等功能
"""

import gradio as gr
import pandas as pd
import os
import sys
from datetime import datetime
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from history_service import HistoryService
from ui_translations import ui_translations

def create_history_app():
    """创建独立的历史记录应用"""
    
    # 初始化服务
    history_service = HistoryService()
    
    # 设置语言并获取UI文本
    ui_translations.set_language('zh')
    current_lang = 'zh'
    
    # 创建文本字典
    texts = {
        'app_title': ui_translations.get_text('app_title', current_lang),
        'app_description': ui_translations.get_text('app_description', current_lang),
        'chat_history': ui_translations.get_text('chat_history', current_lang),
        'input_placeholder': ui_translations.get_text('input_placeholder', current_lang),
        'send_button': ui_translations.get_text('send_button', current_lang),
        'clear_button': ui_translations.get_text('clear_button', current_lang),
        'tech_details': ui_translations.get_text('tech_details', current_lang),
        'sql_query_label': ui_translations.get_text('sql_query_label', current_lang),
        'sql_placeholder': ui_translations.get_text('sql_placeholder', current_lang),
        'result_label': ui_translations.get_text('result_label', current_lang),
        'result_placeholder': ui_translations.get_text('result_placeholder', current_lang)
    }
    
    # 创建Gradio界面
    with gr.Blocks(
        title="📊 查询历史记录",
        theme=gr.themes.Soft(),
        css="""
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
        }
        .stats-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        .action-button {
            margin: 5px;
        }
        """
    ) as interface:
        
        # 状态变量
        language_state = gr.State("zh")
        
        # 页面标题
        gr.HTML(
            """
            <div class="header-section">
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 查询历史记录</h1>
                <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">实时同步 • 智能搜索 • 数据导出</p>
            </div>
            """
        )
        
        # 控制面板
        with gr.Row():
            with gr.Column(scale=1):
                # 语言选择
                language_dropdown = gr.Dropdown(
                    choices=[("中文", "zh"), ("English", "en")],
                    value="zh",
                    label="🌍 语言 / Language",
                    interactive=True
                )
                
                # 搜索功能
                search_input = gr.Textbox(
                    placeholder="🔍 搜索查询内容、SQL或结果...",
                    label="智能搜索",
                    lines=1
                )
                
                # 操作按钮
                with gr.Row():
                    refresh_btn = gr.Button(
                        "🔄 刷新", 
                        variant="primary",
                        scale=1
                    )
                    export_btn = gr.Button(
                        "📥 导出CSV", 
                        variant="secondary",
                        scale=1
                    )
                    clear_btn = gr.Button(
                        "🗑️ 清空历史", 
                        variant="stop",
                        scale=1
                    )
            
            with gr.Column(scale=2):
                # 统计信息
                stats_display = gr.HTML(
                    """
                    <div class="stats-card">
                        <h4 style="margin: 0 0 10px 0; color: #007bff;">📈 统计信息</h4>
                        <p style="margin: 0; font-size: 0.9rem;">正在加载统计数据...</p>
                    </div>
                    """
                )
        
        # 历史记录表格
        history_table = gr.Dataframe(
            headers=["时间", "查询", "类型", "状态"],
            datatype=["str", "str", "str", "str"],
            interactive=False,
            wrap=True,
            label="📋 查询历史记录"
        )
        
        # 导出文件下载
        export_file = gr.File(
            label="📁 导出文件",
            visible=False
        )
        
        # 自动刷新定时器
        auto_refresh_timer = gr.Timer(value=10)  # 每10秒自动刷新
        
        # 功能函数
        def get_history_data():
            """获取历史记录数据"""
            try:
                # 获取最近30天的历史记录
                records = history_service.get_recent_queries(days=30, limit=100)
                
                if records:
                    df = pd.DataFrame(records)
                    # 格式化时间列
                    if 'timestamp' in df.columns:
                        df['时间'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    # 重命名列
                    column_mapping = {
                        'query': '查询',
                        'type': '类型', 
                        'success': '状态'
                    }
                    for old_col, new_col in column_mapping.items():
                        if old_col in df.columns:
                            if old_col == 'success':
                                df[new_col] = df[old_col].apply(lambda x: "成功" if x else "失败")
                            else:
                                df[new_col] = df[old_col]
                    
                    # 选择需要显示的列
                    display_columns = ['时间', '查询', '类型', '状态']
                    available_columns = [col for col in display_columns if col in df.columns]
                    return df[available_columns].fillna('')
                else:
                    return pd.DataFrame(columns=['时间', '查询', '类型', '状态'])
            except Exception as e:
                print(f"获取历史记录时出错: {e}")
                return pd.DataFrame(columns=['时间', '查询', '类型', '状态'])
        
        def refresh_history():
            """刷新历史记录"""
            df = get_history_data()
            stats_html = generate_stats_html(df)
            return df, stats_html
        
        def generate_stats_html(df):
            """生成统计信息HTML"""
            total_queries = len(df)
            if total_queries > 0:
                latest_query = df.iloc[0]['时间'] if '时间' in df.columns and not df.empty else "无"
                unique_queries = df['查询'].nunique() if '查询' in df.columns else 0
            else:
                latest_query = "无"
                unique_queries = 0
            
            return f"""
            <div class="stats-card">
                <h4 style="margin: 0 0 10px 0; color: #007bff;">📈 统计信息</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                    <div><strong>总查询数:</strong> {total_queries}</div>
                    <div><strong>唯一查询:</strong> {unique_queries}</div>
                    <div style="grid-column: 1 / -1;"><strong>最新查询:</strong> {latest_query}</div>
                </div>
                <p style="margin: 10px 0 0 0; font-size: 0.8rem; color: #666;">
                    💡 数据每10秒自动刷新，确保与主应用同步
                </p>
            </div>
            """
        
        def search_history(search_term):
            """搜索历史记录"""
            df = get_history_data()
            if search_term and not df.empty:
                # 在所有列中搜索
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                filtered_df = df[mask]
                stats_html = generate_stats_html(filtered_df)
                return filtered_df, stats_html
            else:
                stats_html = generate_stats_html(df)
                return df, stats_html
        
        def export_history():
            """导出历史记录为CSV"""
            try:
                df = get_history_data()
                if df.empty:
                    return None, "⚠️ 没有数据可导出"
                
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"history_export_{timestamp}.csv"
                filepath = os.path.join(os.getcwd(), filename)
                
                # 导出CSV
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                return filepath, f"✅ 成功导出 {len(df)} 条记录到 {filename}"
            except Exception as e:
                return None, f"❌ 导出失败: {str(e)}"
        
        def clear_history():
            """清空历史记录"""
            try:
                history_service.clear_all_history()
                empty_df = pd.DataFrame(columns=['时间', '查询', 'SQL', '结果'])
                stats_html = generate_stats_html(empty_df)
                return empty_df, stats_html, "✅ 历史记录已清空"
            except Exception as e:
                df = get_history_data()
                stats_html = generate_stats_html(df)
                return df, stats_html, f"❌ 清空失败: {str(e)}"
        
        def update_language(language):
            """更新界面语言"""
            # 这里可以根据需要更新界面文本
            return language
        
        # 事件绑定
        
        # 页面加载时初始化数据
        interface.load(
            refresh_history,
            outputs=[history_table, stats_display]
        )
        
        # 刷新按钮
        refresh_btn.click(
            refresh_history,
            outputs=[history_table, stats_display]
        )
        
        # 搜索功能
        search_input.change(
            search_history,
            inputs=[search_input],
            outputs=[history_table, stats_display]
        )
        
        # 导出功能
        export_btn.click(
            export_history,
            outputs=[export_file, stats_display]
        ).then(
            lambda file, msg: gr.update(visible=file is not None),
            inputs=[export_file, stats_display],
            outputs=[export_file]
        )
        
        # 清空历史
        clear_btn.click(
            clear_history,
            outputs=[history_table, stats_display, stats_display]
        )
        
        # 语言切换
        language_dropdown.change(
            update_language,
            inputs=[language_dropdown],
            outputs=[language_state]
        )
        
        # 自动刷新
        auto_refresh_timer.tick(
            refresh_history,
            outputs=[history_table, stats_display]
        )
    
    return interface

def main():
    """主函数"""
    print("🚀 启动独立历史记录应用...")
    
    # 创建应用
    app = create_history_app()
    
    # 启动应用
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()