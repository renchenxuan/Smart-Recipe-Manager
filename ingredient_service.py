from typing import List, Dict, Any
from adapters.base import Ingredient, BaseAdapter
from db.database import db


class IngredientService:
    """食材服务类"""
    
    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
    
    async def identify_ingredients(self, image_bytes: bytes) -> List[Ingredient]:
        """识别图片中的食材"""
        ingredients = await self.adapter.identify_ingredients(image_bytes)
        # 保存识别结果到数据库
        for ing in ingredients:
            db.add_ingredient(
                name=ing.name,
                quantity=ing.quantity,
                category=ing.category,
                source="photo"
            )
        return ingredients
    
    def get_ingredients(self) -> List[Dict[str, Any]]:
        """获取所有食材"""
        return db.get_ingredients()
    
    def add_ingredient(self, name: str, quantity: str, category: str) -> int:
        """手动添加食材"""
        return db.add_ingredient(
            name=name,
            quantity=quantity,
            category=category,
            source="manual"
        )
    
    def delete_ingredient(self, ingredient_id: int) -> None:
        """删除食材"""
        db.delete_ingredient(ingredient_id)
    
    def clear_ingredients(self) -> None:
        """清空食材列表"""
        # 这里可以实现清空食材的逻辑
        pass