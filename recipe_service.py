from typing import Dict, Any, List
from adapters.base import Ingredient, UserPref, WeekPlan, BaseAdapter
from db.database import db


class RecipeService:
    """菜谱服务类"""
    
    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
    
    async def generate_recipes(self, ingredients: List[Ingredient], preferences: UserPref) -> Dict[str, Any]:
        """生成一周菜谱"""
        recipes = await self.adapter.generate_recipes(ingredients, preferences)
        # 保存到历史记录
        ingredients_snapshot = [ing.to_dict() for ing in ingredients]
        db.add_recipe_history(
            title=f"一周菜谱 ({preferences.days}天)",
            model_used=self.adapter.__class__.__name__,
            ingredients_snapshot=ingredients_snapshot,
            week_plan=recipes.get("week_plan", []),
            nutrition_report={}
        )
        return recipes
    
    def get_recipe_history(self) -> List[Dict[str, Any]]:
        """获取菜谱历史"""
        return db.get_recipe_history()
    
    async def generate_shopping_list(self, recipes: Dict[str, Any], have: List[Ingredient]) -> Dict[str, List[Dict[str, str]]]:
        """生成购物清单"""
        shopping_list = await self.adapter.generate_shopping_list(recipes, have)
        return shopping_list.to_dict()
    
    def add_favorite(self, recipe_name: str, ingredients: List[str], steps: List[str]) -> int:
        """添加收藏"""
        return db.add_favorite(
            recipe_name=recipe_name,
            ingredients=ingredients,
            steps=steps
        )
    
    def get_favorites(self) -> List[Dict[str, Any]]:
        """获取收藏夹"""
        return db.get_favorites()
    
    def delete_favorite(self, favorite_id: int) -> None:
        """删除收藏"""
        db.delete_favorite(favorite_id)