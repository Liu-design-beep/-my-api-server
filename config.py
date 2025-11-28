# config.py
# 配置和LLM客户端初始化

import os
from http import HTTPStatus
from dashscope import Application

# 阿里云百炼智能体应用调用配置
# 配置优先级（从高到低）：
# 1. config_local.py 中的配置（本地配置文件，不提交到版本控制）
# 2. 环境变量
# 3. 默认值
# 
# 请确保您已设置以下之一：
# - 创建 config_local.py 文件并设置 DASHSCOPE_API_KEY 和 APP_ID
# - 设置环境变量 DASHSCOPE_API_KEY 和 APP_ID
# 
# 如果未设置，代码将使用默认配置，但实际运行时会失败。

# 尝试从本地配置文件导入（如果存在）
try:
    import config_local
    LOCAL_API_KEY = getattr(config_local, 'DASHSCOPE_API_KEY', None)
    LOCAL_APP_ID = getattr(config_local, 'APP_ID', None)
    API_ID = getattr(config_local, 'API_ID', None)
    _has_local_config = LOCAL_API_KEY is not None
except ImportError:
    _has_local_config = False
    LOCAL_API_KEY = None
    LOCAL_APP_ID = None
    API_ID = None

# 阿里云百炼 API Key（优先使用本地配置，其次环境变量，最后默认值）
API_KEY = LOCAL_API_KEY if _has_local_config else os.environ.get("DASHSCOPE_API_KEY", "YOUR_DASHSCOPE_API_KEY")
# 智能体应用 ID（优先使用本地配置，其次环境变量，最后默认值）
APP_ID = LOCAL_APP_ID if _has_local_config else os.environ.get("APP_ID", "YOUR_APP_ID")

def get_llm_client():
    """
    初始化并返回LLM客户端配置信息
    注意：使用阿里云百炼智能体应用时，不需要返回客户端对象，
    而是直接使用 Application.call() 方法调用
    """
    # 验证配置
    if API_KEY == "YOUR_DASHSCOPE_API_KEY" or APP_ID == "YOUR_APP_ID":
        print("警告：请配置 DASHSCOPE_API_KEY 和 APP_ID")
        print("  方式1：创建 config_local.py 文件并设置 DASHSCOPE_API_KEY 和 APP_ID")
        print("  方式2：设置环境变量 DASHSCOPE_API_KEY 和 APP_ID")
        return None
    
    return {
        "api_key": API_KEY,
        "app_id": APP_ID
    }


