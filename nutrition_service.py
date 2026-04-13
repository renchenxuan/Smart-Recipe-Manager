from typing import Dict, Any
from adapters.base import WeekPlan, BaseAdapter


class NutritionService:
    """营养服务类"""
    
    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
    
    async def analyze_nutrition(self, week_plan: WeekPlan) -> Dict[str, Any]:
        """分析菜谱的营养成分"""
        nutrition_report = await self.adapter.analyze_nutrition(week_plan)
        return nutrition_report.to_dict()
    
    def generate_nutrition_chart(self, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成营养数据图表配置"""
        # 这里可以生成 Plotly 图表配置
        # 为了简化，返回一个示例配置
        return {
            "data": [
                {
                    "x": ["蛋白质", "碳水化合物", "脂肪"],
                    "y": [
                        nutrition_data.get("daily", {}).get("protein", 0),
                        nutrition_data.get("daily", {}).get("carbs", 0),
                        nutrition_data.get("daily", {}).get("fat", 0)
                    ],
                    "type": "bar",
                    "name": "每日摄入量"
                }
            ],
            "layout": {
                "title": "营养成分分析",
                "xaxis": {"title": "营养成分"},
                "yaxis": {"title": "摄入量 (g)"}
            }
        }