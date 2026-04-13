from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    # 模型配置
    model_name: str = "openai"
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    dashscope_api_key: Optional[str] = None
    zhipuai_api_key: Optional[str] = None
    
    # 界面设置
    theme: str = "light"
    language: str = "zh"
    
    # 数据存储
    database_url: str = "sqlite:///recipe_manager.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()