import os
import logging
from typing import Optional, List, Any
from langchain_community.utilities import SQLDatabase
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
from llm_client import SiliconFlow  # 使用独立的LLM模块
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Text2SQL:
    def __init__(self, db_path="sqlite:///data/order_database.db"):
        """初始化Text2SQL类
        
        Args:
            db_path: 数据库连接URI
        """
        self.db = SQLDatabase.from_uri(db_path)
        self.llm = SiliconFlow()  # 使用独立的LLM实例
        self.chain = self._build_chain()
        self.chat_history = []
        logger.info(f"Text2SQL initialized with db_path: {db_path}")
    
    def _clean_sql_response(self, response: str) -> str:
        """清洗 SQL 前缀"""
        if response.startswith("SQLQuery:"):
            cleaned_response = response.split("SQLQuery:", 1)[1].strip()
            logger.debug(f"Cleaned SQL: {cleaned_response}")
            return cleaned_response
        logger.warning(f"SQL response did not start with 'SQLQuery:': {response[:100]}...")
        return response
    
    def _format_result_wrapper(self, result: Any) -> dict:
        """将执行结果包装为字典，保留原始 SQL 和结果"""
        # 确保result是字符串或可以安全转换为字符串
        if not isinstance(result, str):
            try:
                result_str = str(result)
            except Exception as e:
                logger.error(f"Could not convert SQL result to string: {e}")
                result_str = "Error: Could not format SQL result."
        else:
            result_str = result
        logger.debug(f"Formatted SQL result: {result_str[:200]}...")
        return {"raw_result": result_str}
    
    def _build_chain(self):
        """构建完整的处理链"""
        # SQL 生成链（原始输出含 "SQLQuery: " 前缀）
        write_query = create_sql_query_chain(self.llm, self.db)
        execute_query = QuerySQLDataBaseTool(db=self.db)
        
        # 回答生成提示模板
        answer_prompt = PromptTemplate.from_template(
            """基于以下信息回答问题：
问题：{question}
生成的 SQL 查询：{clean_query}
数据库返回结果：{result}

请用自然语言给出简洁答案。如果结果中的数值为 0，明确说明"没有记录"""
        )
        
        # 构建完整链
        chain = (
            # 第一步：接收原始输入，保留问题字段
            RunnablePassthrough.assign(question=lambda x: x["question"])
            # 第二步：生成并清洗 SQL
            .assign(
                clean_query=write_query | RunnableLambda(self._clean_sql_response)
            )
            # 第三步：执行 SQL 并包装结果
            .assign(
                result=itemgetter("clean_query") | execute_query | RunnableLambda(self._format_result_wrapper)
            )
            # 第四步：组合所有数据到提示模板并生成回答
            .assign(
                response={
                    "question": itemgetter("question"),
                    "clean_query": itemgetter("clean_query"),
                    "result": itemgetter("result")
                }
                | answer_prompt  # 填充模板
                | self.llm  # 生成自然语言回答
                | StrOutputParser()  # 解析输出
            )
            # 第五步：返回包含回答、SQL查询和执行结果的字典
            | {
                "response": itemgetter("response"),
                "clean_query": itemgetter("clean_query"),
                "sql_result": itemgetter("result")
            }
        )
        logger.info("Text2SQL chain built successfully.")
        return chain
    
    def query(self, question: str) -> tuple[str, str, str]:
        """处理自然语言问题并返回回答、SQL查询和SQL执行结果
        
        Args:
            question: 用户的自然语言问题
            
        Returns:
            tuple[str, str, str]: 返回一个元组，包含(自然语言回答, SQL查询, SQL执行结果)
        """
        logger.info(f"Processing query: {question}")
        try:
            # 执行chain并获取结果
            result = self.chain.invoke({"question": question})
            # 从result中获取response、clean_query和sql_result
            answer = result["response"]
            clean_query = result["clean_query"]
            sql_result = result["sql_result"]
            # 更新对话历史
            self.chat_history.append({"question": question, "answer": answer})
            return answer, clean_query, sql_result
        except Exception as e:
            logger.error(f"Error during query processing for '{question}': {str(e)}", exc_info=True)
            return "抱歉，处理您的请求时发生错误。", "", ""
    
    def get_chat_history(self):
        """获取对话历史"""
        return self.chat_history

# 调用示例 (生产环境中通常不会直接在模块底部执行)
if __name__ == "__main__":
    pass