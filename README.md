# 🍳 智能菜谱管家

基于 AI 的智能菜谱生成工具，支持拍照识别食材、生成一周菜谱、购物清单和营养分析。

## 功能特性

- 📸 **食材识别**：拍照或上传图片识别食材名称和数量
- 📋 **菜谱生成**：基于现有食材生成一周菜谱（早、午、晚三餐）
- 🛒 **购物清单**：自动生成缺失食材的购物清单
- 📊 **营养分析**：每日/每周营养摄入可视化分析
- ⭐ **收藏夹**：收藏喜欢的菜谱
- 📋 **历史记录**：查看历史生成的菜谱
- ⚙️ **多模型支持**：支持 OpenAI、Gemini、通义千问、智谱 GLM 等多种 AI 模型

## 技术栈

- **前端**：Gradio 5.x
- **后端**：Python 3.11+
- **多模态模型**：OpenAI GPT-4o、Google Gemini、通义千问 Qwen-VL、智谱 GLM-4V
- **数据存储**：SQLite
- **数据可视化**：Plotly
- **配置管理**：pydantic-settings + .env

## 快速开始

### 1. 安装依赖

```bash
# 使用 pip 安装
pip install -r requirements.txt

# 或使用 uv（推荐）
uv install
```

### 2. 配置 API Key

复制 `.env.example` 文件为 `.env`，并填写对应模型的 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
# 模型配置
MODEL_NAME=openai  # 可选: openai, gemini, qwen, glm
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
DASHSCOPE_API_KEY=your_dashscope_api_key
ZHIPUAI_API_KEY=your_zhipuai_api_key

# 界面设置
THEME=light
LANGUAGE=zh

# 数据存储
DATABASE_URL=sqlite:///recipe_manager.db
```

### 3. 启动应用

```bash
python app.py
```

应用将在 `http://localhost:7860` 启动。

## 使用指南

### 1. 食材识别

- 在「📸 食材识别」标签页上传食材图片
- 点击「🔍 开始识别」按钮
- 识别结果会显示在右侧，并自动保存到食材列表
- 也可以手动添加食材

### 2. 菜谱生成

- 在「📋 菜谱生成」标签页设置用餐人数、天数、口味等偏好
- 点击「🚀 生成一周菜谱」按钮
- 生成结果会显示在下方
- 可以点击「🛒 生成购物清单」和「📊 营养分析」查看相关信息

### 3. 收藏夹和历史记录

- 在「⭐ 收藏夹」标签页查看收藏的菜谱
- 在「📋 历史记录」标签页查看历史生成的菜谱

### 4. 设置中心

- 在「⚙️ 设置中心」标签页选择模型并输入 API Key
- 点击「🔑 测试连接」验证 API Key 是否有效
- 可以切换主题和语言

## 项目结构

```
smart-recipe-manager/
├── app.py                    # Gradio 入口，UI 定义
├── config.py                 # 配置管理
├── requirements.txt          # 依赖清单
├── .env.example              # 环境变量模板
├── README.md                 # 使用说明
│
├── adapters/                 # 模型适配层
│   ├── __init__.py
│   ├── base.py               # 抽象基类
│   ├── openai_adapter.py     # OpenAI 适配器
│   ├── gemini_adapter.py     # Gemini 适配器
│   ├── qwen_adapter.py       # 通义千问适配器
│   └── glm_adapter.py        # 智谱 GLM 适配器
│
├── services/                 # 业务逻辑层
│   ├── __init__.py
│   ├── ingredient_service.py # 食材服务
│   ├── recipe_service.py     # 菜谱服务
│   ├── nutrition_service.py  # 营养服务
│   └── history_service.py    # 历史记录服务
│
├── db/                       # 数据层
│   ├── __init__.py
│   └── database.py           # SQLite 数据库管理
│
├── static/                   # 静态资源
│   └── custom.css            # 自定义主题样式
```

## 注意事项

1. **API Key 安全**：请妥善保管您的 API Key，不要分享给他人
2. **模型选择**：不同模型的能力和价格不同，建议根据实际需求选择
3. **网络连接**：使用前确保网络连接正常，特别是访问国外 API 时
4. **食材识别**：识别 accuracy 取决于图片质量和模型能力，建议在光线充足的环境下拍摄
5. **营养分析**：营养数据为估算值，仅供参考

## 扩展方向

- 📱 微信小程序版
- 🔄 多轮对话优化
- 🌍 多语言菜谱支持
- 📷 实时摄像头扫描
- 🧊 食材保鲜期管理
- 👨‍👩‍👧‍👦 家庭成员口味管理

## 许可证

MIT License