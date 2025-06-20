import logging
import os
from logging.handlers import RotatingFileHandler

# 创建专门的SQL查询日志器
sql_logger = logging.getLogger('sql_query')
sql_logger.setLevel(logging.DEBUG)

# 确保日志目录存在
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建文件处理器，使用循环日志文件
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'sql_queries.log'),
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3
)

# 设置格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加处理器到日志器
sql_logger.addHandler(file_handler)

# 设置为不向父日志器传播日志
sql_logger.propagate = False

# 便捷日志函数
def log_sql_request(question):
    sql_logger.info(f"SQL请求: {question}")

def log_sql_response(response):
    sql_logger.info(f"SQL响应: {response}")
    
def log_sql_cleaned(cleaned_sql):
    sql_logger.info(f"清洗后的SQL: {cleaned_sql}")
    
def log_sql_execution(sql):
    sql_logger.info(f"执行SQL: {sql}")
    
def log_sql_result(result):
    sql_logger.info(f"SQL结果: {result[:500]}" + ("..." if len(str(result)) > 500 else ""))
    
def log_sql_error(error):
    sql_logger.error(f"SQL错误: {error}")