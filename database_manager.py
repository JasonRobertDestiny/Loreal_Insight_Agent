"""
数据库管理器 - 统一管理所有数据库操作
修复数据结构问题，提供完整的数据库管理功能
"""

import sqlite3
import pandas as pd
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器 - 统一管理所有数据库操作"""
    
    def __init__(self, db_path: str = "data/loreal_insight.db"):
        self.db_path = db_path
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else "data", exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        
        schema_sql = """
        -- 1. 用户管理表
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL DEFAULT 'default_user',
            email VARCHAR(100),
            role VARCHAR(20) DEFAULT 'user',
            department VARCHAR(50) DEFAULT 'L''Oréal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );

        -- 2. 数据源配置表
        CREATE TABLE IF NOT EXISTS data_sources (
            source_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name VARCHAR(100) NOT NULL,
            source_type VARCHAR(20) NOT NULL DEFAULT 'sqlite',
            connection_string TEXT,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 3. 优化的查询历史表
        CREATE TABLE IF NOT EXISTS query_history (
            query_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            session_id VARCHAR(50),
            query_type VARCHAR(20) DEFAULT 'natural_language',
            original_query TEXT NOT NULL,
            generated_sql TEXT,
            query_intent VARCHAR(100),
            execution_time_ms INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            result_rows INTEGER DEFAULT 0,
            result_size_kb REAL DEFAULT 0,
            data_source_id INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (data_source_id) REFERENCES data_sources(source_id)
        );

        -- 4. 业务数据表 - 销售数据 (修复版)
        CREATE TABLE IF NOT EXISTS sales_data (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date DATE NOT NULL,
            product_id VARCHAR(20),
            product_name VARCHAR(100),
            category VARCHAR(50),
            brand VARCHAR(50),
            customer_id VARCHAR(20),
            customer_name VARCHAR(100),
            city VARCHAR(50),
            province VARCHAR(50),
            sales_amount DECIMAL(10,2),
            quantity INTEGER,
            discount_amount DECIMAL(10,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 5. 产品主数据表
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(20) PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            sub_category VARCHAR(50),
            brand VARCHAR(50),
            unit_price DECIMAL(10,2),
            cost_price DECIMAL(10,2),
            launch_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 6. 客户主数据表
        CREATE TABLE IF NOT EXISTS customers (
            customer_id VARCHAR(20) PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            customer_type VARCHAR(20) DEFAULT 'B2C',
            city VARCHAR(50),
            province VARCHAR(50),
            registration_date DATE,
            total_orders INTEGER DEFAULT 0,
            total_amount DECIMAL(12,2) DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        );

        -- 7. AI对话上下文表
        CREATE TABLE IF NOT EXISTS conversation_context (
            context_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(50),
            user_id INTEGER DEFAULT 1,
            context_data TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- 8. 插入默认用户
        INSERT OR IGNORE INTO users (user_id, username, department) VALUES (1, 'loreal_user', 'L''Oréal Analytics');
        
        -- 9. 插入默认数据源
        INSERT OR IGNORE INTO data_sources (source_id, source_name, source_type, description) 
        VALUES (1, 'L''Oréal Business Database', 'sqlite', 'Main business data source');
        """
        
        try:
            conn.executescript(schema_sql)
            conn.commit()
            logger.info("数据库初始化成功")
            self.insert_sample_data()
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
        finally:
            conn.close()
    
    def insert_sample_data(self):
        """插入有意义的示例数据"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # 检查是否已有数据
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sales_data")
            if cursor.fetchone()[0] > 0:
                logger.info("数据已存在，跳过示例数据插入")
                return
            
            # 插入产品数据
            products_data = [
                ('PRD001', '欧莱雅复颜精华液', '护肤品', '精华类', '欧莱雅', 299.00, 150.00, '2023-01-01', 1),
                ('PRD002', '兰蔻气垫BB霜', '彩妆', '底妆类', '兰蔻', 450.00, 200.00, '2023-02-01', 1),
                ('PRD003', '薇姿温泉洁面乳', '护肤品', '洁面类', '薇姿', 180.00, 80.00, '2023-01-15', 1),
                ('PRD004', '美宝莲睫毛膏', '彩妆', '眼妆类', '美宝莲', 120.00, 50.00, '2023-03-01', 1),
                ('PRD005', '植村秀洁颜油', '护肤品', '洁面类', '植村秀', 380.00, 180.00, '2023-02-15', 1),
                ('PRD006', '科颜氏牛油果眼霜', '护肤品', '眼部护理', '科颜氏', 520.00, 250.00, '2023-01-20', 1),
                ('PRD007', '兰蔻粉水', '护肤品', '爽肤水', '兰蔻', 350.00, 150.00, '2023-02-10', 1),
                ('PRD008', '欧莱雅口红', '彩妆', '唇妆类', '欧莱雅', 89.00, 30.00, '2023-03-15', 1),
            ]
            
            conn.executemany("""
                INSERT OR REPLACE INTO products 
                (product_id, product_name, category, sub_category, brand, unit_price, cost_price, launch_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, products_data)
            
            # 插入客户数据
            customers_data = [
                ('CUST001', '张丽华', 'B2C', '上海', '上海市', '2023-01-10', 0, 0, 1),
                ('CUST002', '李明', 'B2C', '北京', '北京市', '2023-01-15', 0, 0, 1),
                ('CUST003', '王小美', 'B2C', '广州', '广东省', '2023-02-01', 0, 0, 1),
                ('CUST004', '赵雅琪', 'B2C', '深圳', '广东省', '2023-02-10', 0, 0, 1),
                ('CUST005', '钱芳', 'B2C', '杭州', '浙江省', '2023-02-15', 0, 0, 1),
                ('CUST006', '孙佳佳', 'B2C', '南京', '江苏省', '2023-03-01', 0, 0, 1),
                ('CUST007', '周婷婷', 'B2C', '成都', '四川省', '2023-03-05', 0, 0, 1),
                ('CUST008', '吴雨薇', 'B2C', '重庆', '重庆市', '2023-03-10', 0, 0, 1),
            ]
            
            conn.executemany("""
                INSERT OR REPLACE INTO customers 
                (customer_id, customer_name, customer_type, city, province, registration_date, total_orders, total_amount, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, customers_data)
            
            # 插入最近几个月的销售数据
            import random
            from datetime import datetime, timedelta
            
            sales_data = []
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2024, 6, 23)  # 到今天
            
            # 生成更真实的销售数据
            for i in range(500):  # 生成500条记录
                random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
                product = random.choice(products_data)
                customer = random.choice(customers_data)
                
                # 根据产品价格生成合理的销量和折扣
                base_price = product[5]  # unit_price
                quantity = random.randint(1, 3)
                discount = random.choice([0, 0, 0, base_price * 0.1, base_price * 0.15, base_price * 0.2])
                sales_amount = (base_price * quantity) - discount
                
                sales_data.append((
                    random_date.date().isoformat(),
                    product[0],  # product_id
                    product[1],  # product_name
                    product[2],  # category
                    product[4],  # brand
                    customer[0], # customer_id
                    customer[1], # customer_name
                    customer[2], # city
                    customer[3], # province
                    round(sales_amount, 2),
                    quantity,
                    round(discount, 2)
                ))
            
            conn.executemany("""
                INSERT INTO sales_data 
                (order_date, product_id, product_name, category, brand, customer_id, 
                 customer_name, city, province, sales_amount, quantity, discount_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sales_data)
            
            conn.commit()
            logger.info(f"成功插入 {len(sales_data)} 条销售记录")
            
        except Exception as e:
            logger.error(f"插入示例数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """执行查询并返回DataFrame"""
        conn = sqlite3.connect(self.db_path)
        try:
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作并返回影响行数"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"更新操作失败: {e}")
            return 0
        finally:
            conn.close()
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表信息"""
        conn = sqlite3.connect(self.db_path)
        try:
            # 获取表结构
            schema_df = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
            
            # 获取记录数
            count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table_name}", conn)
            
            return {
                'schema': schema_df.to_dict('records'),
                'row_count': count_df['count'].iloc[0] if not count_df.empty else 0
            }
        except Exception as e:
            return {'error': str(e)}
        finally:
            conn.close()
    
    def get_database_summary(self) -> Dict[str, Any]:
        """获取数据库概要信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 获取所有表
            tables_df = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'", 
                conn
            )
            
            summary = {
                'tables': [],
                'total_records': 0,
                'last_updated': datetime.now().isoformat()
            }
            
            for table_name in tables_df['name']:
                table_info = self.get_table_info(table_name)
                if 'error' not in table_info:
                    summary['tables'].append({
                        'name': table_name,
                        'row_count': table_info['row_count']
                    })
                    summary['total_records'] += table_info['row_count']
            
            conn.close()
            return summary
            
        except Exception as e:
            logger.error(f"获取数据库概要失败: {e}")
            return {'error': str(e)}

# 全局数据库管理器实例
db_manager = DatabaseManager()

if __name__ == "__main__":
    # 测试数据库管理器
    db_manager = DatabaseManager()
    summary = db_manager.get_database_summary()
    print("数据库概要:", summary)
