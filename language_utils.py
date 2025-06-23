# -*- coding: utf-8 -*-
"""
语言检测和多语言支持工具模块
提供语言检测、关键词匹配和提示模板选择功能
"""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class LanguageDetector:
    """语言检测器"""
    
    def __init__(self):
        # 中文字符正则表达式
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        # 英文字符正则表达式
        self.english_pattern = re.compile(r'[a-zA-Z]+')
        # 移除法语支持
    
    def detect_language(self, text: str) -> str:
        """检测文本语言
        
        Args:
            text: 输入文本
            
        Returns:
            'zh' for Chinese, 'en' for English, 'mixed' for mixed languages
        """
        chinese_chars = len(self.chinese_pattern.findall(text))
        english_words = len(self.english_pattern.findall(text))
        
        # 语言检测逻辑
        languages_detected = []
        if chinese_chars > 0:
            languages_detected.append('zh')
        if english_words > 0:
            languages_detected.append('en')
        
        if len(languages_detected) == 0:
            return 'zh'  # 默认返回中文
        elif len(languages_detected) == 1:
            return languages_detected[0]
        else:
            return 'mixed'

class MultilingualKeywords:
    """多语言关键词管理"""
    
    def __init__(self):
        # 可视化关键词
        self.viz_keywords = {
            'zh': [
                "可视化", "图表", "图形", "绘制", "画图", "展示", "趋势", "变化", 
                "统计图", "柱状图", "折线图", "饼图", "直方图", "散点图", "分布图",
                "变化情况", "走势", "对比", "分析图"
            ],
            'en': [
                "visualize", "visualization", "chart", "plot", "graph", "trend", 
                "show", "display", "draw", "create chart", "bar chart", "line chart", 
                "pie chart", "histogram", "scatter plot", "distribution", "trend analysis",
                "comparison", "analytics", "dashboard", "visual", "plotting"
            ],

        }
        
        # 普通对话关键词
        self.general_keywords = {
            'zh': [
                "你好", "您好", "谢谢", "感谢", "再见", "介绍", "功能", "帮助",
                "什么", "怎么", "如何", "能否", "可以", "身份", "名字"
            ],
            'en': [
                "hello", "hi", "thank", "thanks", "goodbye", "bye", "introduce", 
                "function", "help", "what", "how", "can", "could", "would", 
                "identity", "name", "who are you", "what can you do"
            ]
        }
    
    def is_visualization_query(self, query: str, language: str = None) -> bool:
        """检测是否为可视化查询
        
        Args:
            query: 查询文本
            language: 语言代码，如果为None则自动检测
            
        Returns:
            是否为可视化查询
        """
        if language is None:
            detector = LanguageDetector()
            language = detector.detect_language(query)
        
        query_lower = query.lower()
        
        # 检查中文关键词
        if language in ['zh', 'mixed']:
            for keyword in self.viz_keywords['zh']:
                if keyword in query_lower:
                    return True
        
        # 检查英文关键词
        if language in ['en', 'mixed']:
            for keyword in self.viz_keywords['en']:
                if keyword in query_lower:
                    return True
        
        return False
    
    def is_general_conversation(self, query: str, language: str = None) -> bool:
        """检测是否为普通对话
        
        Args:
            query: 查询文本
            language: 语言代码，如果为None则自动检测
            
        Returns:
            是否为普通对话
        """
        if language is None:
            detector = LanguageDetector()
            language = detector.detect_language(query)
        
        query_lower = query.lower()
        
        # 检查中文关键词
        if language in ['zh', 'mixed']:
            for keyword in self.general_keywords['zh']:
                if keyword in query_lower:
                    return True
        
        # 检查英文关键词
        if language in ['en', 'mixed']:
            for keyword in self.general_keywords['en']:
                if keyword in query_lower:
                    return True
        
        return False

class MultilingualPrompts:
    """多语言提示模板管理"""
    
    def __init__(self):
        # SQL回答生成提示模板
        self.sql_answer_prompts = {
            'zh': """
你是一个专业的数据分析师。基于以下SQL查询结果，请用中文提供清晰、准确的回答。

SQL查询: {clean_query}
查询结果: {result}
用户问题: {question}

请根据查询结果回答用户问题，要求：
1. 回答要准确、简洁
2. 如果有数字，请突出显示重要数据
3. 如果结果为空，请说明可能的原因
4. 用专业但易懂的语言
""",
            'en': """
You are a professional data analyst. Based on the following SQL query results, please provide a clear and accurate answer in English.

SQL Query: {clean_query}
Query Results: {result}
User Question: {question}

Please answer the user's question based on the query results with the following requirements:
1. Answer should be accurate and concise
2. Highlight important data if there are numbers
3. If results are empty, explain possible reasons
4. Use professional but understandable language
""",

        }
        
        # 对话分类提示模板
        self.conversation_classification_prompts = {
            'zh': """
请判断以下用户输入是否为数据查询相关的问题。

用户输入: "{question}"

如果是数据查询相关（包括但不限于：销售数据、产品信息、统计分析、趋势查询、可视化需求等），请回答"data_query"。
如果是一般性对话（如问候、闲聊、非数据相关问题等），请回答"general_conversation"。

只需回答分类结果，不需要其他解释。
""",
            'en': """
Please determine whether the following user input is related to data query.

User Input: "{question}"

If it's data query related (including but not limited to: sales data, product information, statistical analysis, trend queries, visualization needs, etc.), please answer "data_query".
If it's general conversation (such as greetings, small talk, non-data related questions, etc.), please answer "general_conversation".

Only provide the classification result, no other explanation needed.
""",

        }
        
        # 普通对话回答提示模板
        self.chat_prompts = {
            'zh': """你是欧莱雅集团的智能数据分析助手 BeautyInsight，专注于美妆行业数据分析。

作为你的专业领域：
- 我精通欧莱雅集团的销售数据分析
- 可以帮助进行销量趋势、市场表现、品类分析等
- 擅长通过图表直观展示数据洞察

沟通风格：
- 专业且平易近人
- 善于用通俗易懂的语言解释专业数据
- 注重实用性的数据洞察

用户问题: "{question}"

回答要求：
- 用专业、友好的语言回答
- 如果用户询问功能，介绍数据分析和可视化能力，并举例说明（如"我可以帮您分析某个品类的月度销售趋势"）
- 确保回答既专业又容易理解
- 适时建议可以进行的深入分析

请回答：""",
            
            'en': """You are BeautyInsight, L'Oréal Group's intelligent data analysis assistant, specializing in beauty industry data analysis.

As your professional expertise:
- I excel in L'Oréal Group's sales data analysis
- I can help with sales trend analysis, market performance, category analysis, etc.
- I'm skilled at presenting data insights through intuitive charts

Communication style:
- Professional yet approachable
- Good at explaining professional data in easy-to-understand language
- Focus on practical data insights

User question: "{question}"

Response requirements:
- Answer in professional, friendly language
- If users ask about features, introduce data analysis and visualization capabilities with examples (e.g., "I can help you analyze monthly sales trends for a specific category")
- Ensure answers are both professional and easy to understand
- Suggest in-depth analysis when appropriate

Please respond:"""
        }
    
    def get_prompts(self, language: str) -> Dict[str, str]:
        """获取指定语言的所有提示模板
        
        Args:
            language: 语言代码 ('zh', 'en', 'mixed')
            
        Returns:
            包含所有提示模板的字典
        """
        # 如果是混合语言，默认使用中文
        if language == 'mixed':
            language = 'zh'
            
        return {
            'sql_answer': self.get_sql_answer_prompt(language),
            'classify_conversation': self.get_classify_prompt(language),
            'chat': self.get_chat_prompt(language)
        }
    
    def get_sql_answer_prompt(self, language: str) -> str:
        """获取SQL回答提示模板"""
        return self.sql_answer_prompts.get(language, self.sql_answer_prompts['zh'])
    
    def get_classify_prompt(self, language: str) -> str:
        """获取对话分类提示模板"""
        return self.conversation_classification_prompts.get(language, self.conversation_classification_prompts['zh'])
    
    def get_chat_prompt(self, language: str) -> str:
        """获取普通对话提示模板"""
        return self.chat_prompts.get(language, self.chat_prompts['zh'])

# 全局实例
language_detector = LanguageDetector()
multilingual_keywords = MultilingualKeywords()
multilingual_prompts = MultilingualPrompts()