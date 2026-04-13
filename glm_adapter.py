import base64
import json
import httpx
from typing import List, Dict, Any
from .base import BaseAdapter, Ingredient, UserPref, WeekPlan, NutritionReport, ShoppingList


class GLMAdapter(BaseAdapter):
    """智谱 GLM-4V 模型适配器"""
    
    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn/api/mock/v1/chat/completions"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def identify_ingredients(self, image_bytes: bytes) -> List[Ingredient]:
        """识别图片中的食材"""
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "model": "glm-4v-plus",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的厨房食材识别专家。请识别图片中的所有食材，并预估数量。输出格式为 JSON 数组，每个元素包含 name（食材名）、quantity（数量）、category（分类）字段。category 取值范围：蔬菜/水果/肉类/蛋奶/调味品/主食/其他。只识别食材，忽略非食物物品。数量尽量准确，无法判断时写'若干'。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": base64_image
                        }
                    ]
                }
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = await self.client.post("", json=payload)
            response.raise_for_status()
            data = response.json()
            ingredients_data = json.loads(data['choices'][0]['message']['content'])
            
            ingredients = []
            for item in ingredients_data:
                ingredients.append(
                    Ingredient(
                        name=item.get('name', ''),
                        quantity=item.get('quantity', '若干'),
                        category=item.get('category', '其他')
                    )
                )
            return ingredients
        except Exception as e:
            print(f"GLM-4V 食材识别错误: {e}")
            return []
    
    async def generate_recipes(self, ingredients: List[Ingredient], preferences: UserPref) -> Dict[str, Any]:
        """基于食材生成一周菜谱"""
        ingredients_str = "\n".join([f"{ing.name} {ing.quantity}" for ing in ingredients])
        
        payload = {
            "model": "glm-4v-plus",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位营养均衡、创意十足的家庭厨师。请根据用户提供的现有食材和偏好，生成一周的菜谱计划（早、午、晚三餐）。输出格式为 JSON，包含 week_plan（一周计划）和 shopping_list（购物清单）字段。优先使用现有食材，确保营养均衡，考虑食材保鲜期，尊重用户忌口。"
                },
                {
                    "role": "user",
                    "content": f"现有食材：\n{ingredients_str}\n\n用户偏好：\n用餐人数：{preferences.people_count}\n口味：{preferences.taste_preference}\n忌口：{preferences.allergies}\n菜系：{preferences.cuisine_style}\n生成天数：{preferences.days}"
                }
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = await self.client.post("", json=payload)
            response.raise_for_status()
            data = response.json()
            return json.loads(data['choices'][0]['message']['content'])
        except Exception as e:
            print(f"GLM-4V 菜谱生成错误: {e}")
            return {"week_plan": [], "shopping_list": []}
    
    async def analyze_nutrition(self, week_plan: WeekPlan) -> NutritionReport:
        """分析菜谱的营养成分"""
        week_plan_str = json.dumps(week_plan.to_dict(), ensure_ascii=False)
        
        payload = {
            "model": "glm-4v-plus",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的营养师。请分析提供的一周菜谱，计算每日和每周的营养摄入（卡路里、蛋白质、碳水化合物、脂肪），并给出营养建议。输出格式为 JSON，包含 daily（每日营养）、weekly（每周营养）和 suggestions（营养建议）字段。"
                },
                {
                    "role": "user",
                    "content": f"一周菜谱：\n{week_plan_str}"
                }
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = await self.client.post("", json=payload)
            response.raise_for_status()
            data = response.json()
            nutrition_data = json.loads(data['choices'][0]['message']['content'])
            
            return NutritionReport(
                daily=nutrition_data.get('daily', {}),
                weekly=nutrition_data.get('weekly', {}),
                suggestions=nutrition_data.get('suggestions', '')
            )
        except Exception as e:
            print(f"GLM-4V 营养分析错误: {e}")
            return NutritionReport(
                daily={"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
                weekly={"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
                suggestions="营养分析失败"
            )
    
    async def generate_shopping_list(self, recipes: Dict[str, Any], have: List[Ingredient]) -> ShoppingList:
        """生成购物清单"""
        have_ingredients = [ing.name for ing in have]
        recipes_str = json.dumps(recipes, ensure_ascii=False)
        
        payload = {
            "model": "glm-4v-plus",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位细心的家庭采购助手。请根据菜谱和现有食材，生成需要购买的食材清单。输出格式为 JSON 数组，每个元素包含 name（食材名）、quantity（数量）、category（分类）字段。"
                },
                {
                    "role": "user",
                    "content": f"菜谱：\n{recipes_str}\n\n现有食材：\n{', '.join(have_ingredients)}"
                }
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = await self.client.post("", json=payload)
            response.raise_for_status()
            data = response.json()
            shopping_list_data = json.loads(data['choices'][0]['message']['content'])
            return ShoppingList(items=shopping_list_data)
        except Exception as e:
            print(f"GLM-4V 购物清单生成错误: {e}")
            return ShoppingList(items=[])
    
    async def test_connection(self) -> bool:
        """测试模型连接"""
        try:
            payload = {
                "model": "glm-4v-plus",
                "messages": [
                    {
                        "role": "user",
                        "content": "测试连接"
                    }
                ],
                "max_tokens": 10
            }
            response = await self.client.post("", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"GLM-4V 连接测试失败: {e}")
            return False
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()