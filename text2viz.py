import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns
import ast
import os
import logging # 保留 logging
import io
import contextlib
from datetime import datetime
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from llm_client import SiliconFlow  # 替换原来的导入
from sql_logger import (
    log_sql_request, log_sql_response, log_sql_cleaned, 
    log_sql_execution, log_sql_result, log_sql_error
)

# 配置基本的日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # 设置生产环境的日志级别为 INFO

class Text2Viz:
    def __init__(self, db_path="sqlite:///data/order_database.db"):
        """初始化Text2Viz类
        
        Args:
            db_path: 数据库连接URI
        """
        self.db = SQLDatabase.from_uri(db_path)
        self.llm = SiliconFlow()  # 使用独立的LLM实例
        self.chain = self._build_chain()
        self.viz_history = []
        
        # 设置图片保存目录
        self.img_dir = "viz_images"
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
    
    def _clean_sql_response(self, response: str) -> str:
        """清洗 SQL 前缀"""
        log_sql_response(response) # 保留此日志，因为它记录了原始响应
        
        if "SQLQuery:" in response:
            cleaned = response.split("SQLQuery:", 1)[1].strip()
            log_sql_cleaned(cleaned) # 保留此日志，记录清洗后的SQL
            return cleaned
        
        elif "SELECT" in response.upper():
            start_idx = response.upper().find("SELECT")
            cleaned = response[start_idx:]
            log_sql_cleaned(cleaned) # 保留此日志
            return cleaned
        
        log_sql_error(f"无法清洗SQL响应: {response}") # 关键错误日志，保留
        logger.warning(f"无法清洗SQL响应，返回原始响应: {response[:100]}...") # 添加 INFO/WARNING 级别日志
        return response
    
    def _convert_to_dataframe(self, result: str, sql_query: str = None) -> pd.DataFrame:
        """将SQL结果转换为DataFrame，支持不同的列名和数据格式
        
        Args:
            result: SQL查询结果字符串
            sql_query: SQL查询语句，用于提取列名
        """

        if result.startswith('[') and result.endswith(']'):
            try:
                parsed_data = ast.literal_eval(result)
                
                if parsed_data and isinstance(parsed_data[0], tuple):
                    column_names = []
                    if sql_query:
                        import re
                        matches = re.findall(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE)
                        if matches:
                            cols = matches[0].split(',')
                            column_names = []
                            for col in cols:
                                if ' AS ' in col.upper():
                                    alias = col.split(' AS ', 1)[1].strip().strip('"')
                                    column_names.append(alias)
                                else:
                                    name = col.strip().split('.')[-1].strip('"')
                                    column_names.append(name)
                    
                    if not column_names or len(column_names) != len(parsed_data[0]):
                        logger.info(f"无法从SQL提取准确列名或列名数量不匹配，将使用默认列名。SQL: {sql_query}")
                        column_names = [f"column_{i}" for i in range(len(parsed_data[0]))]
                    
                    df = pd.DataFrame(parsed_data, columns=column_names)
                else:
                    df = pd.DataFrame(parsed_data)
            except Exception as e:
                logger.error(f"DataFrame创建异常: {str(e)}. 原始结果: {result[:200]}")
                try:
                    # 备用解析方法
                    logger.info("尝试备用解析方法创建DataFrame")
                    df = pd.DataFrame([item.strip("()").split(",") for item in result.strip("[]").split("), (")])
                except Exception as e2:
                    logger.error(f"备用解析方法也失败: {str(e2)}. 原始结果: {result[:200]}")
                    df = pd.DataFrame()
        else:
            logger.warning(f"结果不是预期的列表格式，返回空DataFrame. 结果: {result[:200]}")
            df = pd.DataFrame()
    
        for col in df.columns:
            try:
                sample_values = df[col].dropna().head(5).astype(str)
                numeric_pattern = r'^-?\d+(\.\d+)?$'
                if sample_values.str.match(numeric_pattern).all():
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    continue
            except Exception as e:
                logger.warning(f"尝试将列 {col} 转换为数值类型时出错: {str(e)}")
                pass
            
            try:
                sample_values = df[col].dropna().head(5).astype(str)
                date_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}'
                if sample_values.str.match(date_pattern).any():
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception as e:
                logger.warning(f"尝试将列 {col} 转换为日期类型时出错: {str(e)}")
                pass

        return df
    
    def _create_visualization(self, df: pd.DataFrame) -> tuple:
        """创建可视化图表，支持不同的列名"""
        if len(df.columns) < 2 or df.empty:
            logger.warning("数据不足以创建可视化图表 (列数 < 2 或 DataFrame 为空)")
            return df, None

        font_prop = font_manager.FontProperties(family='SimHei')
        plt.rcParams['axes.unicode_minus'] = False

        x_col = df.columns[0]
        y_col = df.columns[1]

        if not pd.api.types.is_numeric_dtype(df[y_col]):
            logger.info(f"Y轴列 '{y_col}' 非数值类型，尝试转换...")
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            if df[y_col].isnull().all():
                logger.error(f"Y轴列 '{y_col}' 转换数值失败或全为NaN，无法绘图。")
                return df, None

        plt.figure(figsize=(12, 6))
        sns.set_style("whitegrid")

        try:
            if pd.api.types.is_datetime64_dtype(df[x_col]):
                plt.plot(df[x_col], df[y_col], marker='o')
                logger.info(f"创建时间序列图: X='{x_col}', Y='{y_col}'")
            else:
                plt.bar(df[x_col].astype(str), df[y_col]) # 确保x轴为字符串以避免类型问题
                logger.info(f"创建条形图: X='{x_col}', Y='{y_col}'")
            
            plt.xlabel(x_col, fontproperties=font_prop)
            plt.ylabel(y_col, fontproperties=font_prop)
            plt.title(f'{y_col} vs {x_col}', fontproperties=font_prop)
            plt.xticks(rotation=45, ha='right', fontproperties=font_prop)
            plt.yticks(fontproperties=font_prop)
            plt.tight_layout()

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()

            # 保存图片到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_filename = os.path.join(self.img_dir, f"viz_{timestamp}.png")
            with open(img_filename, 'wb') as f:
                f.write(img_buffer.getvalue())
            logger.info(f"可视化图表已保存到 {img_filename}")

            return df, img_filename
        except Exception as e:
            logger.error(f"创建可视化图表时发生错误: {str(e)}")
            plt.close() # 确保关闭图形，以防错误
            return df, None
    def _build_chain(self):
        """构建完整的处理链"""
        # SQL生成和执行组件
        write_query = create_sql_query_chain(self.llm, self.db)
        execute_query = QuerySQLDataBaseTool(db=self.db)
        
        # 在_build_chain方法中修改链的构建
        chain = (
        # 第一步：接收原始输入，保留问题字段
        RunnablePassthrough.assign(question=lambda x: x["question"])
        # 添加日志记录原始问题
        | RunnableLambda(lambda x: {**x, "_debug": log_sql_request(x['question']) or True})
        # 第二步：生成并清洗 SQL
        .assign(
            clean_query=write_query 
            | RunnableLambda(lambda x: log_sql_response(x) or x)
            | RunnableLambda(self._clean_sql_response)
        )
        # 添加SQL执行前的日志
        | RunnableLambda(lambda x: {**x, "_debug2": log_sql_execution(x['clean_query']) or True})
        # 第三步：执行SQL并转换为DataFrame，生成可视化
        .assign(
            result=RunnableLambda(lambda x: {
                "sql_query": x["clean_query"],
                "query_result": execute_query.invoke(x["clean_query"])
            })
            | RunnableLambda(lambda x: {
                "sql_query": x["sql_query"],
                "query_result": log_sql_result(x["query_result"]) or x["query_result"]
            })
            | RunnableLambda(lambda x: self._convert_to_dataframe(x["query_result"], x["sql_query"]))
            | RunnableLambda(self._create_visualization)
        )
        # 第四步：使用RunnableLambda包装返回值，确保正确返回
        | RunnableLambda(lambda x: {
            "result": x["result"],
            "clean_query": x["clean_query"]
        })
        )
        
        return chain
    def get_viz_history(self):
        """获取可视化历史"""
        return self.viz_history
    
    def visualize(self, question: str) -> tuple:
        """处理用户的可视化查询，返回数据框和可视化图像路径
        
        Args:
            question: 用户的查询问题
            
        Returns:
            tuple: (DataFrame, 图像文件路径)
                如果可视化失败，图像路径为None
        """
        try:
            logger.info(f"处理可视化查询: {question}")
            # 调用处理链，传入问题
            chain_result = self.chain.invoke({"question": question})
            # 正确处理返回值
            if isinstance(chain_result, dict):
                result = chain_result.get("result")
                clean_query = chain_result.get("clean_query", "")
            else:
                # 如果返回值不是字典，则假设它是直接的结果
                result = chain_result
                clean_query = ""
            
            # 记录可视化历史
            if isinstance(result, tuple) and len(result) == 2:
                df, img_path = result
                if img_path:
                    self.viz_history.append({
                        "question": question,
                        "timestamp": datetime.now().isoformat(),
                        "image_path": img_path,
                        "sql_query": clean_query
                    })
                    logger.info(f"可视化成功，图像保存至: {img_path}")
                else:
                    logger.warning(f"可视化失败，未生成图像")
                return df, img_path, clean_query
            else:
                logger.error(f"处理链返回格式异常: {result}")
                return pd.DataFrame(), None
        except Exception as e:
            logger.error(f"可视化处理异常: {str(e)}")
            return pd.DataFrame(), None

# 调用示例 (生产环境中通常不会直接在模块底部执行)
if __name__ == "__main__":
    pass