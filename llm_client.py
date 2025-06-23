import os
import logging
from typing import Optional, List, Any, Tuple
from langchain.llms.base import LLM
from openai import OpenAI
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_community.llms.utils import enforce_stop_tokens
from language_utils import language_detector, multilingual_prompts
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 设置日志
logger = logging.getLogger(__name__)

class SiliconFlow(LLM):
    """独立的SiliconFlow LLM客户端"""
    
    def __init__(self):
        super().__init__()
        
    @property
    def _llm_type(self) -> str:
        return "silicon_flow"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            # 检查API_KEY是否存在
            api_key = os.environ.get("API_KEY")
            if not api_key or api_key == "your_api_key_here":
                return "⚠️ 请先配置API_KEY环境变量。\n\n在本地开发时：\n1. 复制.env.example为.env\n2. 在.env文件中填入您的真实API_KEY\n\n在魔塔部署时：\n1. 在平台的环境变量设置中配置API_KEY"
            
            client = OpenAI(
                api_key=api_key,
                base_url=os.environ.get("BASE_URL", "https://api.siliconflow.cn/v1")
            )
            
            response = client.chat.completions.create(
                model='Qwen/Qwen2.5-Coder-32B-Instruct',
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                stream=False,
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                frequency_penalty=0.5
            )
            
            content = ""
            if hasattr(response, 'choices') and response.choices:
                for choice in response.choices:
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        content += choice.message.content
            else:
                logger.error("Unexpected response structure from LLM API")
                return "Error: LLM did not return a valid response."
            
            if stop is not None:
                content = enforce_stop_tokens(content, stop)
            
            return content
        except Exception as e:
            logger.error(f"API call error: {str(e)}", exc_info=True)
            raise
    
    def simple_call(self, prompt: str) -> str:
        """简化的调用方法，直接返回文本响应"""
        return self._call(prompt)
    
    def classify_conversation(self, question: str) -> Tuple[str, str]:
        """判断对话类型并返回相应的回答
        
        Args:
            question: 用户的问题
            
        Returns:
            Tuple[str, str]: (对话类型, 回答)
                对话类型: "general" 或 "data"
                回答: 如果是普通对话，返回回答；如果是数据查询，返回空字符串
        """
        logger.info(f"判断对话类型: {question}")
        try:
            # 检测语言并获取相应的分类提示模板
            detected_language = language_detector.detect_language(question)
            classify_template = multilingual_prompts.get_classify_prompt(detected_language)
            classify_prompt = classify_template.format(question=question)
            
            response = self.simple_call(classify_prompt)
            # 判断回答类型（统一使用英文关键词）
            is_general = 'general_conversation' in response.lower()
            
            # 如果是普通对话，生成回答
            if is_general:
                chat_template = multilingual_prompts.get_chat_prompt(detected_language)
                chat_prompt = chat_template.format(question=question)
                
                answer = self.simple_call(chat_prompt)
                logger.info(f"普通对话回答: {answer}")
                return "general", answer
            else:
                logger.info("判断为数据查询")
                return "data", ""
                
        except Exception as e:
            logger.error(f"对话分类过程出错: {str(e)}", exc_info=True)
            # 出错时默认返回数据查询类型
            return "data", ""