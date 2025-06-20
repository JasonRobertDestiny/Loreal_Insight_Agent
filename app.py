import os
import sys
import pandas as pd
from text2sql import Text2SQL
from text2viz import Text2Viz
import re
import logging
import gradio as gr

# 初始化实例
text2sql = Text2SQL()
text2viz = Text2Viz()

# 检测是否是可视化请求的函数
def is_visualization_query(query):
    """检测查询是否是可视化请求"""
    viz_keywords = [
        "可视化", "图表", "图形", "绘制", "画图", "展示", "趋势", "变化", 
        "统计图", "柱状图", "折线图", "饼图", "直方图", "散点图", "分布图",
        "visualize", "visualization", "chart", "plot", "graph", "trend", "变化情况"
    ]
    
    # 检查查询中是否包含可视化关键词
    for keyword in viz_keywords:
        if keyword in query.lower():
            return True
    return False

# 定义回调函数
def process_query(message, history):
    """处理用户查询并返回回答"""
    if is_visualization_query(message):
        # 使用Text2Viz处理可视化查询
        df, viz_path = text2viz.visualize(message)
        
        if viz_path and os.path.exists(viz_path):
            # 生成数据摘要
            summary = generate_data_summary(df)
            # 返回带图片的回答 - 确保这里返回的是正确的格式
            return [(message, (summary, viz_path))]
        else:
            # 可视化失败，使用Text2SQL回退
            response = text2sql.query(message)
            return [(message, response)]
    else:
        # 使用Text2SQL处理普通查询
        response = text2sql.query(message)
        return [(message, response)]

# 生成数据摘要
def generate_data_summary(df):
    """生成数据摘要信息"""
    if df.empty:
        return "无法生成数据可视化，请尝试其他查询。"
    
    summary = "以下是查询结果的可视化：\n\n"
    
    # 添加基本统计信息
    summary += f"数据包含 {len(df)} 行记录。\n"
    
    # 根据数据类型添加更多统计信息
    for col in df.columns:
        if pd.api.types.is_datetime64_dtype(df[col]):
            summary += f"• {col} 范围: {df[col].min().date()} 到 {df[col].max().date()}\n"
        elif pd.api.types.is_numeric_dtype(df[col]):
            summary += f"• {col} 统计: 总和={df[col].sum():.2f}, 平均值={df[col].mean():.2f}\n"
    
    return summary

# 创建Gradio界面
def create_combined_interface():
    """创建集成Text2SQL和Text2Viz的Gradio界面"""
    # 欧莱雅品牌风格的自定义CSS样式
    custom_css = """
    /* L'Oréal 品牌色彩定义 - 支持主题切换 */
    :root {
        --loreal-gold: #D4AF37;
        --loreal-dark-gold: #B8941F;
        --loreal-hover: #E6C55A;
        --loreal-black: #1A1A1A;
        --loreal-dark-gray: #2D2D2D;
        --loreal-light-gray: #F5F5F5;
        --loreal-white: #FFFFFF;
        --loreal-accent: #8B4513;
        
        /* Light主题默认颜色 - 优化对比度 */
        --text-primary: #1A1A1A;
        --text-secondary: #2D2D2D;
        --text-muted: #666666;
        --bg-primary: #FFFFFF;
        --bg-secondary: #FAFAFA;
        --border-color: #E0E0E0;
    }
    
    /* Dark模式适配 - 优化颜色对比度 */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #F5F5F5;
            --text-secondary: #CCCCCC;
            --text-muted: #B0B0B0;
            --bg-primary: #1E1E1E;
            --bg-secondary: #2A2A2A;
            --border-color: #404040;
        }
    }
    
    /* Gradio dark主题检测 */
    .dark :root {
        --text-primary: #F5F5F5;
        --text-secondary: #CCCCCC;
        --text-muted: #B0B0B0;
        --bg-primary: #1E1E1E;
        --bg-secondary: #2A2A2A;
        --border-color: #404040;
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
    }
    
    .main-header h1 {
        position: relative;
        z-index: 2;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        background: linear-gradient(45deg, var(--loreal-white), var(--loreal-gold));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        position: relative;
        z-index: 2;
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
    }
    
    .feature-card p {
        color: var(--text-secondary) !important;
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
    
    /* 聊天界面优化 */
    .chatbot {
        border: 2px solid var(--loreal-gold) !important;
        border-radius: 16px !important;
        background: var(--bg-primary) !important;
        box-shadow: 0 8px 32px rgba(212, 175, 55, 0.2) !important;
        color: var(--text-primary) !important;
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
    
    with gr.Blocks(title="🔍 L'Oréal 数据洞察助手", theme=gr.themes.Soft(), css=custom_css) as interface:
        # 主标题区域 - 紧凑设计
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="main-header">
                    <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">🔍 L'Oréal 数据洞察助手</h1>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">让数据洞察如钻石般闪耀，每次查询都是发现价值的旅程</p>
                </div>
                """)
        
        # 功能介绍卡片 - 简洁设计
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">💎 智能查询</h3>
                    <p style="margin: 0; font-size: 0.9rem;">自然语言转SQL，智能数据查询</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">📊 数据可视化</h3>
                    <p style="margin: 0; font-size: 0.9rem;">多样图表类型，直观数据展示</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">🎯 智能洞察</h3>
                    <p style="margin: 0; font-size: 0.9rem;">深度分析，专业商业洞察</p>
                </div>
                """)
        
        # 主要交互区域
        with gr.Row():
            with gr.Column(scale=2):
                # 聊天组件 - 紧凑设计
                chatbot = gr.Chatbot(
                    height=400, 
                    label="💬 对话历史",
                    type="messages"
                )
                
                # 输入区域 - 紧凑设计
                with gr.Group():
                    msg = gr.Textbox(
                        placeholder="💭 请输入您的数据查询问题...", 
                        label="",
                        lines=2,
                        max_lines=4,
                        show_label=False,
                        container=False
                    )
                    with gr.Row():
                        submit_btn = gr.Button(
                            "🚀 发送查询", 
                            variant="primary",
                            scale=1
                        )
                        clear_btn = gr.Button(
                            "🗑️ 清空对话", 
                            variant="secondary",
                            scale=1
                        )
            
            with gr.Column(scale=1):
                # 技术详情面板
                with gr.Accordion("🔧 技术详情", open=False):
                    sql_display = gr.Textbox(
                        label="📝 生成的SQL查询", 
                        lines=6, 
                        interactive=False,
                        placeholder="SQL查询将在这里显示..."
                    )
                    result_display = gr.Textbox(
                        label="📋 数据库返回结果", 
                        lines=10, 
                        interactive=False,
                        placeholder="查询结果将在这里显示..."
                    )
        
        # 示例查询区域 - 优化设计
        with gr.Row():
            with gr.Column():
                pass
                
                # 示例查询 - 保留必要示例
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>💎 精准查询</h4>")
                        gr.Examples(
                            examples=[
                                "查询最近7天的总销售额",
                                "显示销售额最高的前5个订单",
                                "统计每个渠道的订单数量",
                                "查看所有品牌的销售情况"
                            ],
                            inputs=msg
                        )
                    
                    with gr.Column(scale=1):
                        gr.HTML("<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>🎨 视觉呈现</h4>")
                        gr.Examples(
                            examples=[
                                "绘制每日销售额的趋势图",
                                "可视化各个渠道的销售对比",
                                "展示不同品牌的销售分布",
                                "画出各省份销售额排行图"
                            ],
                            inputs=msg
                        )
                    
                    with gr.Column(scale=1):
                        gr.HTML("<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>🔮 智慧洞察</h4>")
                        gr.Examples(
                            examples=[
                                "最近5天的销售趋势如何？",
                                "哪个省份的销售表现最好？",
                                "销售额最高的前3个品牌是什么？",
                                "10月份的总销售额是多少？"
                            ],
                            inputs=msg
                        )
        
        # 定义回调函数
        def user_input(user_message, history):
            # 处理用户输入 - 使用messages格式
            return "", history + [{"role": "user", "content": user_message}]
        
        # 定义回调函数
        def bot_response(history):
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
        
        # 清空对话功能
        def clear_conversation():
            return [], "", "", ""
        
        # 设置事件处理
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