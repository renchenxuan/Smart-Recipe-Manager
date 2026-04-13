from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Ingredient:
    """食材类"""
    def __init__(self, name: str, quantity: str, category: str):
        self.name = name
        self.quantity = quantity
        self.category = category
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "category": self.category
        }


class Meal:
    """餐食类"""
    def __init__(self, name: str, ingredients: List[str], steps: List[str]):
        self.name = name
        self.ingredients = ingredients
        self.steps = steps
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "ingredients": self.ingredients,
            "steps": self.steps
        }


class DayPlan:
    """每日计划类"""
    def __init__(self, day: str, breakfast: Meal, lunch: Meal, dinner: Meal):
        self.day = day
        self.breakfast = breakfast
        self.lunch = lunch
        self.dinner = dinner
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "meals": {
                "breakfast": self.breakfast.to_dict(),
                "lunch": self.lunch.to_dict(),
                "dinner": self.dinner.to_dict()
            }
        }


class WeekPlan:
    """一周计划类"""
    def __init__(self, day_plans: List[DayPlan]):
        self.day_plans = day_plans
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "week_plan": [plan.to_dict() for plan in self.day_plans]
        }


class NutritionReport:
    """营养报告类"""
    def __init__(self, daily: Dict[str, float], weekly: Dict[str, float], suggestions: str):
        self.daily = daily
        self.weekly = weekly
        self.suggestions = suggestions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "daily": self.daily,
            "weekly": self.weekly,
            "suggestions": self.suggestions
        }


class ShoppingList:
    """购物清单类"""
    def __init__(self, items: List[Dict[str, str]]):
        self.items = items
    
    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "shopping_list": self.items
        }


class UserPref:
    """用户偏好类"""
    def __init__(self, people_count: int, taste_preference: str, allergies: str, cuisine_style: str, days: int):
        self.people_count = people_count
        self.taste_preference = taste_preference
        self.allergies = allergies
        self.cuisine_style = cuisine_style
        self.days = days
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "people_count": self.people_count,
            "taste_preference": self.taste_preference,
            "allergies": self.allergies,
            "cuisine_style": self.cuisine_style,
            "days": self.days
        }


class BaseAdapter(ABC):
    """所有模型适配器的抽象基类"""
    
    @abstractmethod
    async def identify_ingredients(self, image_bytes: bytes) -> List[Ingredient]:
        """识别图片中的食材"""
        pass
    
    @abstractmethod
    async def generate_recipes(self, ingredients: List[Ingredient], preferences: UserPref) -> Dict[str, Any]:
        """基于食材生成一周菜谱"""
        pass
    
    @abstractmethod
    async def analyze_nutrition(self, week_plan: WeekPlan) -> NutritionReport:
        """分析菜谱的营养成分"""
        pass
    
    @abstractmethod
    async def generate_shopping_list(self, recipes: Dict[str, Any], have: List[Ingredient]) -> ShoppingList:
        """生成购物清单"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试模型连接"""
        pass