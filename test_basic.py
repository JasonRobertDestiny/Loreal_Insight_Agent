"""基础功能测试模块

提供基本的功能测试，确保核心组件正常工作。
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    is_visualization_query,
    clean_sql_query,
    format_data_summary,
    extract_column_names_from_sql,
    validate_dataframe_for_visualization
)
from config import Config
from exceptions import APIError, DatabaseError

class TestUtils(unittest.TestCase):
    """工具函数测试类"""
    
    def test_is_visualization_query(self):
        """测试可视化查询检测"""
        # 正面测试
        self.assertTrue(is_visualization_query("请可视化销售数据"))
        self.assertTrue(is_visualization_query("绘制图表"))
        self.assertTrue(is_visualization_query("show me a chart"))
        self.assertTrue(is_visualization_query("visualize the trend"))
        
        # 负面测试
        self.assertFalse(is_visualization_query("查询销售总额"))
        self.assertFalse(is_visualization_query("what is the total sales"))
    
    def test_clean_sql_query(self):
        """测试SQL清洗功能"""
        # 测试带前缀的SQL
        sql_with_prefix = "SQLQuery: SELECT * FROM orders"
        cleaned = clean_sql_query(sql_with_prefix)
        self.assertEqual(cleaned, "SELECT * FROM orders")
        
        # 测试不带前缀的SQL
        sql_without_prefix = "SELECT * FROM orders"
        cleaned = clean_sql_query(sql_without_prefix)
        self.assertEqual(cleaned, "SELECT * FROM orders")
    
    def test_format_data_summary(self):
        """测试数据摘要格式化"""
        # 测试空数据框
        empty_df = pd.DataFrame()
        summary = format_data_summary(empty_df)
        self.assertIn("无法生成", summary)
        
        # 测试有数据的数据框
        df = pd.DataFrame({
            'sales': [100, 200, 300],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
        summary = format_data_summary(df)
        self.assertIn("3 行记录", summary)
        self.assertIn("sales", summary)
    
    def test_extract_column_names_from_sql(self):
        """测试从SQL中提取列名"""
        sql = "SELECT name, sales AS total_sales FROM orders"
        columns = extract_column_names_from_sql(sql)
        self.assertIn("name", columns)
        self.assertIn("total_sales", columns)
    
    def test_validate_dataframe_for_visualization(self):
        """测试数据框可视化验证"""
        # 测试空数据框
        empty_df = pd.DataFrame()
        valid, msg = validate_dataframe_for_visualization(empty_df)
        self.assertFalse(valid)
        self.assertIn("空", msg)
        
        # 测试有效数据框
        valid_df = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'sales': [100, 200, 300]
        })
        valid, msg = validate_dataframe_for_visualization(valid_df)
        self.assertTrue(valid)

class TestConfig(unittest.TestCase):
    """配置测试类"""
    
    def test_config_loading(self):
        """测试配置加载"""
        # 测试默认值
        self.assertEqual(Config.MODEL_NAME, "Qwen/QwQ-32B")
        self.assertEqual(Config.BASE_URL, "https://api.siliconflow.cn/v1")
        self.assertEqual(Config.MAX_TOKENS, 512)
    
    def test_llm_params(self):
        """测试LLM参数获取"""
        params = Config.get_llm_params()
        self.assertIn("model", params)
        self.assertIn("max_tokens", params)
        self.assertEqual(params["model"], "Qwen/QwQ-32B")

class TestExceptions(unittest.TestCase):
    """异常测试类"""
    
    def test_api_error(self):
        """测试API错误"""
        error = APIError("API调用失败", status_code=500, response_text="Internal Server Error")
        self.assertEqual(str(error), "API调用失败")
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.response_text, "Internal Server Error")
    
    def test_database_error(self):
        """测试数据库错误"""
        error = DatabaseError("数据库连接失败")
        self.assertEqual(str(error), "数据库连接失败")

class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
    @patch('requests.post')
    def test_api_connection(self, mock_post):
        """测试API连接（模拟）"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '测试响应'
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 这里可以添加实际的API调用测试
        # 由于需要真实的API密钥，这里只做模拟测试
        self.assertTrue(True)  # 占位符测试

def run_basic_tests():
    """运行基础测试"""
    print("开始运行基础功能测试...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestUtils))
    test_suite.addTest(unittest.makeSuite(TestConfig))
    test_suite.addTest(unittest.makeSuite(TestExceptions))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    
    # 运行测试
    success = run_basic_tests()
    
    if success:
        print("\n✅ 所有基础测试通过！")
    else:
        print("\n❌ 部分测试失败，请检查代码。")
        sys.exit(1)