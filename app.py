import base64
import json
import gradio as gr
from PIL import Image
import io
from typing import Dict, Any, List

from config import settings
from adapters.openai_adapter import OpenAIAdapter
from adapters.gemini_adapter import GeminiAdapter
from adapters.qwen_adapter import QwenAdapter
from adapters.glm_adapter import GLMAdapter
from adapters.base import Ingredient, UserPref, WeekPlan, DayPlan, Meal

from services.ingredient_service import IngredientService
from services.recipe_service import RecipeService
from services.nutrition_service import NutritionService
from services.history_service import HistoryService
from db.database import db


class ModelAdapterFactory:
    """模型适配器工厂类"""
    
    @staticmethod
    def create(model_name: str, api_key: str) -> Any:
        """创建模型适配器"""
        if model_name == "openai":
            return OpenAIAdapter(api_key)
        elif model_name == "gemini":
            return GeminiAdapter(api_key)
        elif model_name == "qwen":
            return QwenAdapter(api_key)
        elif model_name == "glm":
            return GLMAdapter(api_key)
        else:
            raise ValueError(f"不支持的模型: {model_name}")


class SmartRecipeManager:
    """智能菜谱管家应用"""
    
    def __init__(self):
        self.adapter = None
        self.ingredient_service = None
        self.recipe_service = None
        self.nutrition_service = None
        self.history_service = HistoryService()
        self.current_recipes = None
        self.current_ingredients = []
        self.init_services()
    
    def init_services(self):
        """初始化服务"""
        # 根据配置创建适配器
        api_key = self.get_api_key(settings.model_name)
        if api_key:
            self.adapter = ModelAdapterFactory.create(settings.model_name, api_key)
            self.ingredient_service = IngredientService(self.adapter)
            self.recipe_service = RecipeService(self.adapter)
            self.nutrition_service = NutritionService(self.adapter)
    
    def get_api_key(self, model_name: str) -> str:
        """获取对应模型的 API Key"""
        if model_name == "openai":
            return settings.openai_api_key or ""
        elif model_name == "gemini":
            return settings.google_api_key or ""
        elif model_name == "qwen":
            return settings.dashscope_api_key or ""
        elif model_name == "glm":
            return settings.zhipuai_api_key or ""
        return ""
    
    def get_ingredients_for_table(self):
        """获取食材数据，用于表格展示"""
        ingredients = self.ingredient_service.get_ingredients() if self.ingredient_service else []
        data = []
        for ing in ingredients:
            data.append([
                ing['name'],
                ing['quantity'],
                ing['category'],
                "✏️ 🗑️"
            ])
        return data
    
    async def identify_ingredients(self, image):
        """识别食材"""
        if not self.adapter:
            return "请先在设置中配置模型和 API Key", self.get_ingredients_for_table()
        
        try:
            # 将 PIL Image 转换为 bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            image_bytes = img_byte_arr.getvalue()
            
            ingredients = await self.ingredient_service.identify_ingredients(image_bytes)
            self.current_ingredients = ingredients
            
            # 格式化识别结果
            result = "\n".join([f"{ing.name} × {ing.quantity}" for ing in ingredients])
            return result if result else "未识别到食材", self.get_ingredients_for_table()
        except Exception as e:
            return f"识别失败: {str(e)}", self.get_ingredients_for_table()
    
    def add_ingredient(self, name, quantity, category):
        """手动添加食材"""
        if not self.ingredient_service:
            return "请先在设置中配置模型和 API Key", self.get_ingredients_for_table()
        
        if not name or not quantity:
            return "请填写食材名称和数量", self.get_ingredients_for_table()
        
        self.ingredient_service.add_ingredient(name, quantity, category)
        return f"已添加: {name} × {quantity}", self.get_ingredients_for_table()
    
    async def generate_recipes(self, people_count, days, taste_preference, cuisine_style, allergies):
        """生成菜谱"""
        if not self.recipe_service:
            return "请先在设置中配置模型和 API Key"
        
        # 获取食材列表
        db_ingredients = self.ingredient_service.get_ingredients()
        ingredients = [Ingredient(ing['name'], ing['quantity'], ing['category']) for ing in db_ingredients]
        
        if not ingredients:
            return "请先添加食材"
        
        # 创建用户偏好
        preferences = UserPref(
            people_count=int(people_count),
            taste_preference=taste_preference,
            allergies=allergies,
            cuisine_style=cuisine_style,
            days=int(days)
        )
        
        try:
            recipes = await self.recipe_service.generate_recipes(ingredients, preferences)
            self.current_recipes = recipes
            
            # 格式化菜谱结果
            result = []
            for day_plan in recipes.get('week_plan', []):
                day = day_plan.get('day', '')
                meals = day_plan.get('meals', {})
                result.append(f"📅 {day}")
                for meal_type, meal in meals.items():
                    meal_name = meal.get('name', '')
                    result.append(f"{meal_type}: {meal_name}")
                result.append("")
            
            return "\n".join(result)
        except Exception as e:
            return f"生成失败: {str(e)}"
    
    async def generate_shopping_list(self):
        """生成购物清单"""
        if not self.recipe_service or not self.current_recipes:
            return "请先生成菜谱"
        
        # 获取现有食材
        db_ingredients = self.ingredient_service.get_ingredients()
        ingredients = [Ingredient(ing['name'], ing['quantity'], ing['category']) for ing in db_ingredients]
        
        try:
            shopping_list = await self.recipe_service.generate_shopping_list(self.current_recipes, ingredients)
            items = shopping_list.get('shopping_list', [])
            
            result = "\n".join([f"{item.get('name')} × {item.get('quantity')}" for item in items])
            return result if result else "无需购买其他食材"
        except Exception as e:
            return f"生成失败: {str(e)}"
    
    async def analyze_nutrition(self):
        """分析营养"""
        if not self.nutrition_service or not self.current_recipes:
            return "请先生成菜谱"
        
        try:
            # 构建 WeekPlan 对象
            day_plans = []
            for day_plan in self.current_recipes.get('week_plan', []):
                meals = day_plan.get('meals', {})
                breakfast = Meal(
                    meals.get('breakfast', {}).get('name', ''),
                    meals.get('breakfast', {}).get('ingredients', []),
                    meals.get('breakfast', {}).get('steps', [])
                )
                lunch = Meal(
                    meals.get('lunch', {}).get('name', ''),
                    meals.get('lunch', {}).get('ingredients', []),
                    meals.get('lunch', {}).get('steps', [])
                )
                dinner = Meal(
                    meals.get('dinner', {}).get('name', ''),
                    meals.get('dinner', {}).get('ingredients', []),
                    meals.get('dinner', {}).get('steps', [])
                )
                day_plan_obj = DayPlan(day_plan.get('day', ''), breakfast, lunch, dinner)
                day_plans.append(day_plan_obj)
            
            week_plan = WeekPlan(day_plans)
            nutrition_data = await self.nutrition_service.analyze_nutrition(week_plan)
            
            # 格式化营养分析结果
            result = []
            result.append("每日营养摄入:")
            for nutrient, value in nutrition_data.get('daily', {}).items():
                result.append(f"{nutrient}: {value}")
            result.append("")
            result.append("营养建议:")
            result.append(nutrition_data.get('suggestions', ''))
            
            return "\n".join(result)
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    def get_favorites(self):
        """获取收藏夹"""
        if not self.recipe_service:
            return "请先在设置中配置模型和 API Key"
        
        favorites = self.recipe_service.get_favorites()
        result = []
        for fav in favorites:
            result.append(f"🍳 {fav['recipe_name']}")
            result.append("")
        return "\n".join(result) if result else "收藏夹为空"
    
    def get_history(self):
        """获取历史记录"""
        history = self.history_service.get_recipe_history()
        result = []
        for item in history:
            result.append(f"📋 {item['title']} ({item['created_at']})")
            result.append("")
        return "\n".join(result) if result else "历史记录为空"
    
    async def test_connection(self, model_name, api_key):
        """测试模型连接"""
        try:
            adapter = ModelAdapterFactory.create(model_name, api_key)
            success = await adapter.test_connection()
            await adapter.close()
            return "✅ 连接成功" if success else "❌ 连接失败"
        except Exception as e:
            return f"❌ 测试失败: {str(e)}"
    
    def create_interface(self):
        """创建 Gradio 界面"""
        with gr.Blocks(title="智能菜谱管家") as app:
            gr.Markdown("# 🍳 智能菜谱管家")
            
            with gr.Tabs():
                # 食材识别 Tab
                with gr.Tab("📸 食材识别"):
                    with gr.Row():
                        # 左侧栏：添加方式
                        with gr.Column(scale=1, elem_classes="column-left"):
                            # 图像识别卡片
                            with gr.Column(elem_classes="card"):
                                gr.Markdown("## 📸 图像识别")
                                image_input = gr.Image(
                                    type="pil", 
                                    label="",
                                    elem_classes="upload"
                                )
                                identify_btn = gr.Button("🔍 开始识别", variant="primary")
                                identify_result = gr.Textbox(
                                    label="识别结果", 
                                    lines=5,
                                    elem_classes="textbox"
                                )
                            
                            # 手动添加卡片
                            with gr.Column(elem_classes="card"):
                                gr.Markdown("## ✏️ 手动添加食材")
                                
                                with gr.Column(elem_classes="form-field"):
                                    ingredient_name = gr.Textbox(
                                        label="食材名称",
                                        placeholder="请输入食材名称"
                                    )
                                
                                with gr.Column(elem_classes="form-field"):
                                    ingredient_quantity = gr.Textbox(
                                        label="数量",
                                        placeholder="例如：500g、3个"
                                    )
                                
                                with gr.Column(elem_classes="form-field"):
                                    ingredient_category = gr.Dropdown(
                                        choices=["蔬菜", "水果", "肉类", "蛋奶", "调味品", "主食", "其他"],
                                        label="分类",
                                        value="蔬菜"
                                    )
                                
                                with gr.Column(elem_classes="btn-right"):
                                    add_btn = gr.Button("➕ 添加食材", variant="primary")
                        
                        # 右侧栏：结果区
                        with gr.Column(scale=1, elem_classes="column-right"):
                            with gr.Column(elem_classes="card"):
                                gr.Markdown("## 已添加的食材")
                                
                                add_result = gr.Textbox(
                                    label="操作结果", 
                                    lines=2,
                                    elem_classes="textbox",
                                    visible=False
                                )
                                
                                # 食材表格
                                ingredients_table = gr.Dataframe(
                                    headers=["食材名称", "数量", "分类", "操作"],
                                    datatype=["str", "str", "str", "str"],
                                    column_widths=[2, 2, 2, 1],
                                    interactive=False,
                                    wrap=True
                                )
                                
                                refresh_ingredients_btn = gr.Button("🔄 刷新列表", variant="primary")
                
                # 菜谱生成 Tab
                with gr.Tab("📋 菜谱生成"):
                    # 用户偏好卡片
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("## 用户偏好")
                        with gr.Row():
                            people_count = gr.Dropdown(
                                choices=["1", "2", "3", "4", "5"], 
                                value="2", 
                                label="用餐人数"
                            )
                            days = gr.Dropdown(
                                choices=["3", "5", "7"], 
                                value="7", 
                                label="生成天数"
                            )
                            taste_preference = gr.Dropdown(
                                choices=["家常", "清淡", "麻辣", "酸甜"], 
                                value="家常", 
                                label="口味"
                            )
                            cuisine_style = gr.Dropdown(
                                choices=["中餐", "西餐", "日式", "韩式"], 
                                value="中餐", 
                                label="菜系"
                            )
                        allergies = gr.Textbox(
                            label="忌口/过敏",
                            placeholder="例如：海鲜、花生"
                        )
                        generate_btn = gr.Button("🚀 生成一周菜谱", variant="primary")
                    
                    # 菜谱结果卡片
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("## 菜谱结果")
                        recipe_result = gr.Textbox(
                            label="一周菜谱", 
                            lines=20,
                            elem_classes="textbox"
                        )
                    
                    # 操作按钮和结果卡片
                    with gr.Row():
                        with gr.Column(scale=1, elem_classes="card"):
                            gr.Markdown("## 购物清单")
                            shopping_btn = gr.Button("🛒 生成购物清单", variant="primary")
                            shopping_result = gr.Textbox(
                                label="缺失食材", 
                                lines=10,
                                elem_classes="textbox"
                            )
                        with gr.Column(scale=1, elem_classes="card"):
                            gr.Markdown("## 营养分析")
                            nutrition_btn = gr.Button("📊 营养分析", variant="primary")
                            nutrition_result = gr.Textbox(
                                label="营养报告", 
                                lines=10,
                                elem_classes="textbox"
                            )
                
                # 收藏夹 Tab
                with gr.Tab("⭐ 收藏夹"):
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("## 收藏的菜谱")
                        favorites_list = gr.Textbox(
                            label="收藏清单", 
                            lines=20,
                            elem_classes="textbox"
                        )
                        refresh_favorites_btn = gr.Button("🔄 刷新收藏夹", variant="primary")
                
                # 历史记录 Tab
                with gr.Tab("📋 历史记录"):
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("## 历史生成记录")
                        history_list = gr.Textbox(
                            label="历史清单", 
                            lines=20,
                            elem_classes="textbox"
                        )
                        refresh_history_btn = gr.Button("🔄 刷新历史", variant="primary")
                
                # 设置中心 Tab
                with gr.Tab("⚙️ 设置中心"):
                    # 模型配置卡片
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("## 🤖 模型配置")
                        model_name = gr.Dropdown(
                            choices=["openai", "gemini", "qwen", "glm"],
                            value=settings.model_name,
                            label="选择模型"
                        )
                        api_key = gr.Textbox(
                            label="API Key", 
                            type="password",
                            placeholder="请输入对应模型的 API Key"
                        )
                        test_btn = gr.Button("🔑 测试连接", variant="primary")
                        test_result = gr.Textbox(
                            label="测试结果",
                            lines=2,
                            elem_classes="textbox"
                        )
                    
                    # 界面设置卡片
                    with gr.Column(elem_classes="card"):
                        gr.Markdown("## 🎨 界面设置")
                        with gr.Row():
                            theme = gr.Dropdown(
                                choices=["浅色", "深色"], 
                                value="浅色", 
                                label="主题"
                            )
                            language = gr.Dropdown(
                                choices=["中文", "英文"], 
                                value="中文", 
                                label="语言"
                            )
            
            # 事件绑定
            identify_btn.click(
                fn=self.identify_ingredients,
                inputs=[image_input],
                outputs=[identify_result, ingredients_table]
            )
            
            add_btn.click(
                fn=self.add_ingredient,
                inputs=[ingredient_name, ingredient_quantity, ingredient_category],
                outputs=[add_result, ingredients_table]
            )
            
            refresh_ingredients_btn.click(
                fn=self.get_ingredients_for_table,
                outputs=[ingredients_table]
            )
            
            generate_btn.click(
                fn=self.generate_recipes,
                inputs=[people_count, days, taste_preference, cuisine_style, allergies],
                outputs=[recipe_result]
            )
            
            shopping_btn.click(
                fn=self.generate_shopping_list,
                outputs=[shopping_result]
            )
            
            nutrition_btn.click(
                fn=self.analyze_nutrition,
                outputs=[nutrition_result]
            )
            
            refresh_favorites_btn.click(
                fn=self.get_favorites,
                outputs=[favorites_list]
            )
            
            refresh_history_btn.click(
                fn=self.get_history,
                outputs=[history_list]
            )
            
            test_btn.click(
                fn=self.test_connection,
                inputs=[model_name, api_key],
                outputs=[test_result]
            )
            
            # 初始化食材表格
            app.load(
                fn=self.get_ingredients_for_table,
                outputs=[ingredients_table]
            )
        
        return app


if __name__ == "__main__":
    app = SmartRecipeManager()
    interface = app.create_interface()
    interface.launch(share=False, debug=True, css="static/custom.css")
