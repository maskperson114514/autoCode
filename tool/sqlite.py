import sqlite3
import os

class AbstractDatabase:
    def __init__(self, db_path="abstracts.db"):
        """
        初始化数据库连接，如果数据库不存在则创建，并确保摘要表存在
        
        参数:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.connection = None
        self.create_connection()
        self.create_tables()
    
    def create_connection(self):
        """创建与数据库的连接"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        except sqlite3.Error as e:
            print(f"数据库连接错误: {e}")
    
    def create_tables(self):
        """创建摘要表（如果不存在）"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS abstracts (
                    id TEXT PRIMARY KEY,
                    summary TEXT,
                    role TEXT
                )
            ''')
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"创建表错误: {e}")
    
    def get_all_abstracts(self):
        """
        获取摘要表中的所有记录
        
        返回:
            包含所有摘要记录的列表，每条记录为字典格式
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM abstracts")
            rows = cursor.fetchall()
            
            # 将查询结果转换为字典列表
            result = []
            for row in rows:
                result.append({
                    'id': row['id'],
                    'summary': row['summary'],
                    'role': row['role']
                })
            return result
        except sqlite3.Error as e:
            print(f"获取摘要表错误: {e}")
            return []
    
    def get_abstract_by_id(self, file_path):
        """
        根据文件路径(id)获取特定摘要记录
        
        参数:
            file_path: 作为id的文件路径
            
        返回:
            找到的记录字典，如果未找到则返回None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM abstracts WHERE id = ?", (file_path,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'summary': row['summary'],
                    'role': row['role']
                }
            return None
        except sqlite3.Error as e:
            print(f"获取摘要记录错误: {e}")
            return None
    
    def add_abstract(self, file_path, summary, role):
        """
        添加新的摘要记录
        
        参数:
            file_path: 文件路径，作为id
            summary: 文件摘要
            role: 文件作用
            
        返回:
            操作是否成功
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO abstracts (id, summary, role) VALUES (?, ?, ?)",
                (file_path, summary, role)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"添加摘要记录错误: {e}")
            return False
    
    def update_abstract(self, file_path, summary=None, role=None):
        """
        更新现有摘要记录
        
        参数:
            file_path: 文件路径，作为id
            summary: 新的文件摘要，如果为None则不更新
            role: 新的文件作用，如果为None则不更新
            
        返回:
            操作是否成功
        """
        try:
            cursor = self.connection.cursor()
            update_fields = []
            params = []
            
            if summary is not None:
                update_fields.append("summary = ?")
                params.append(summary)
            
            if role is not None:
                update_fields.append("role = ?")
                params.append(role)
            
            if not update_fields:
                return True  # 没有需要更新的字段
            
            params.append(file_path)  # WHERE条件的参数
            
            query = f"UPDATE abstracts SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新摘要记录错误: {e}")
            return False
    
    def delete_abstract(self, file_path):
        """
        删除指定文件路径的摘要记录
        
        参数:
            file_path: 文件路径，作为id
            
        返回:
            操作是否成功
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM abstracts WHERE id = ?", (file_path,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"删除摘要记录错误: {e}")
            return False
    
    def __del__(self):
        """析构函数，确保连接关闭"""
        if self.connection:
            self.connection.close()