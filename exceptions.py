"""自定义异常类模块

定义应用特定的异常类，提高错误处理的精确性和可读性。
"""

class LorealInsightError(Exception):
    """L'Oreal洞察代理基础异常类"""
    pass

class APIError(LorealInsightError):
    """API调用相关错误"""
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class DatabaseError(LorealInsightError):
    """数据库操作相关错误"""
    pass

class SQLGenerationError(LorealInsightError):
    """SQL生成相关错误"""
    pass

class VisualizationError(LorealInsightError):
    """数据可视化相关错误"""
    pass

class ConfigurationError(LorealInsightError):
    """配置相关错误"""
    pass

class DataProcessingError(LorealInsightError):
    """数据处理相关错误"""
    pass