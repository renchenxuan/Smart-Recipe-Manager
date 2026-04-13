from typing import List, Dict, Any
from db.database import db


class HistoryService:
    """历史记录服务类"""
    
    def get_recipe_history(self) -> List[Dict[str, Any]]:
        """获取菜谱历史"""
        return db.get_recipe_history()
    
    def clear_history(self) -> None:
        """清空历史记录"""
        # 这里可以实现清空历史记录的逻辑
        pass