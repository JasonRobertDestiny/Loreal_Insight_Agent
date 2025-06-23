"""
快速数据服务层 - 优化查询性能
"""

import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FastDataService:
    """快速数据服务 - 减少API调用，提高响应速度"""
    
    def __init__(self):
        # 缓存常用查询结果
        self.query_cache = {}
    
    def is_visualization_query(self, query: str) -> bool:
        """快速判断是否为可视化查询"""
        viz_keywords = [
            '图表', '图形', '可视化', '趋势', '对比', '排名', '分布', 
            '柱状图', '折线图', '饼图', '绘制', '画图',
            'chart', 'graph', 'plot', 'trend', 'comparison', 'visualize'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in viz_keywords)
    
    def get_optimized_examples(self) -> Dict[str, list]:
        """获取基于实际数据的优化示例"""
        return {
            'precise': [
                "查询2024年总销售额和订单数量",
                "各省份销售额排名统计", 
                "Show total sales amount by brand",
                "Count orders by province"
            ],
            'visual': [
                "绘制各省份销售额对比图",
                "可视化兰蔻和欧莱雅品牌销售对比",
                "Visualize sales distribution by province",
                "Plot monthly sales trend chart"
            ],
            'insights': [
                "哪个省份的销售表现最好？",
                "兰蔻和欧莱雅哪个品牌更受欢迎？", 
                "Which brand has the highest sales?",
                "What are the top 5 selling products?"
            ]
        }

# 全局实例
fast_service = FastDataService()
