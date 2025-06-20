"""配置管理模块

统一管理应用配置，提高代码的可维护性和安全性。
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # API配置
    API_KEY: str = os.getenv("API_KEY", "")
    BASE_URL: str = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen/QwQ-32B")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/order_database.db")
    
    # 应用配置
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 可视化配置
    VIZ_IMAGE_DIR: str = os.getenv("VIZ_IMAGE_DIR", "viz_images")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "512"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Gradio配置
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "False").lower() == "true"
    GRADIO_PORT: Optional[int] = int(os.getenv("GRADIO_PORT", "7860")) if os.getenv("GRADIO_PORT") else None
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.API_KEY:
            raise ValueError("API_KEY is required. Please set it in .env file.")
        return True
    
    @classmethod
    def get_llm_params(cls) -> dict:
        """获取LLM参数配置"""
        return {
            "model": cls.MODEL_NAME,
            "stream": False,
            "max_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE,
            "top_p": 0.7,
            "frequency_penalty": 0.5
        }

# 全局配置实例
config = Config()