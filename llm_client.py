import os
import logging
from typing import Optional, List, Any, Tuple
from langchain.llms.base import LLM
from openai import OpenAI
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_community.llms.utils import enforce_stop_tokens
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
            client = OpenAI(
                api_key=os.environ.get("API_KEY"),
                base_url=os.environ.get("BASE_URL")  # 修改API路径
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
            # 判断对话类型
            classify_prompt = f"""请判断以下用户输入是普通对话还是数据查询问题。

            用户输入: "{question}"

            判断标准：
            - 普通对话：问候语、闲聊、询问身份、功能介绍、感谢等与数据无关的对话
            - 数据查询：询问销售数据、统计信息、数据分析、可视化等与数据相关的问题

            请只回答'普通对话'或'数据查询'，不要有其他内容。"""
            
            response = self.simple_call(classify_prompt)
            is_general = '普通对话' in response
            
            # 如果是普通对话，生成回答
            if is_general:
                chat_prompt = f"""你是欧莱雅集团的智能数据分析助手 BeautyInsight，专注于美妆行业数据分析。

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

                请回答："""

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