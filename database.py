import sqlite3
import json
from datetime import datetime


class Database:
    """SQLite 数据库管理类"""
    
    def __init__(self, db_path="recipe_manager.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """创建数据表"""
        # 用户偏好表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY,
            people_count INTEGER DEFAULT 2,
            taste_preference TEXT DEFAULT '家常',
            allergies TEXT DEFAULT '',
            cuisine_style TEXT DEFAULT '中餐',
            days INTEGER DEFAULT 7
        )
        ''')
        
        # 食材记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity TEXT,
            category TEXT,
            source TEXT DEFAULT 'manual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 菜谱历史表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            model_used TEXT,
            ingredients_snapshot TEXT,
            week_plan TEXT,
            nutrition_report TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 收藏夹表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT NOT NULL,
            ingredients TEXT,
            steps TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 初始化默认偏好
        self.cursor.execute('''
        INSERT OR IGNORE INTO preferences (id, people_count, taste_preference, allergies, cuisine_style, days)
        VALUES (1, 2, '家常', '', '中餐', 7)
        ''')
        
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def get_preferences(self):
        """获取用户偏好"""
        self.cursor.execute('SELECT * FROM preferences WHERE id = 1')
        row = self.cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'people_count': row[1],
                'taste_preference': row[2],
                'allergies': row[3],
                'cuisine_style': row[4],
                'days': row[5]
            }
        return None
    
    def update_preferences(self, **kwargs):
        """更新用户偏好"""
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(1)
        
        sql = f"UPDATE preferences SET {', '.join(fields)} WHERE id = ?"
        self.cursor.execute(sql, values)
        self.conn.commit()
    
    def add_ingredient(self, name, quantity, category, source="manual"):
        """添加食材"""
        self.cursor.execute(
            "INSERT INTO ingredients (name, quantity, category, source) VALUES (?, ?, ?, ?)",
            (name, quantity, category, source)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_ingredients(self):
        """获取所有食材"""
        self.cursor.execute('SELECT * FROM ingredients ORDER BY created_at DESC')
        rows = self.cursor.fetchall()
        return [
            {
                'id': row[0],
                'name': row[1],
                'quantity': row[2],
                'category': row[3],
                'source': row[4],
                'created_at': row[5]
            }
            for row in rows
        ]
    
    def delete_ingredient(self, ingredient_id):
        """删除食材"""
        self.cursor.execute('DELETE FROM ingredients WHERE id = ?', (ingredient_id,))
        self.conn.commit()
    
    def add_recipe_history(self, title, model_used, ingredients_snapshot, week_plan, nutrition_report):
        """添加菜谱历史"""
        self.cursor.execute(
            "INSERT INTO recipe_history (title, model_used, ingredients_snapshot, week_plan, nutrition_report) VALUES (?, ?, ?, ?, ?)",
            (title, model_used, json.dumps(ingredients_snapshot), json.dumps(week_plan), json.dumps(nutrition_report))
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_recipe_history(self):
        """获取菜谱历史"""
        self.cursor.execute('SELECT * FROM recipe_history ORDER BY created_at DESC')
        rows = self.cursor.fetchall()
        return [
            {
                'id': row[0],
                'title': row[1],
                'model_used': row[2],
                'ingredients_snapshot': json.loads(row[3]) if row[3] else None,
                'week_plan': json.loads(row[4]) if row[4] else None,
                'nutrition_report': json.loads(row[5]) if row[5] else None,
                'created_at': row[6]
            }
            for row in rows
        ]
    
    def add_favorite(self, recipe_name, ingredients, steps):
        """添加收藏"""
        self.cursor.execute(
            "INSERT INTO favorites (recipe_name, ingredients, steps) VALUES (?, ?, ?)",
            (recipe_name, json.dumps(ingredients), json.dumps(steps))
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_favorites(self):
        """获取收藏夹"""
        self.cursor.execute('SELECT * FROM favorites ORDER BY created_at DESC')
        rows = self.cursor.fetchall()
        return [
            {
                'id': row[0],
                'recipe_name': row[1],
                'ingredients': json.loads(row[2]) if row[2] else None,
                'steps': json.loads(row[3]) if row[3] else None,
                'created_at': row[4]
            }
            for row in rows
        ]
    
    def delete_favorite(self, favorite_id):
        """删除收藏"""
        self.cursor.execute('DELETE FROM favorites WHERE id = ?', (favorite_id,))
        self.conn.commit()


# 全局数据库实例
db = Database()