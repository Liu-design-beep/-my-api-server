# config.py (最终云端优化版)

import os

print("[配置加载] 正在从环境变量加载配置...")

# --- API Key 加载 ---
# 优先从 'DASHSCOPE_API_KEY' 读取，这是阿里云SDK的官方推荐名称。
# 如果找不到，再从通用的 'API_KEY' 读取。
# 关键：不再提供任何默认值！如果都找不到，API_KEY 将是 None。
API_KEY = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("API_KEY")

# --- App ID 加载 ---
# 关键：不再提供任何默认值！
APP_ID = os.environ.get("APP_ID")

# --- 启动时检查 ---
# 在程序启动时就进行严格检查，如果关键配置缺失，直接打印错误。
if not API_KEY:
    print("[配置错误] 严重错误：环境变量 'DASHSCOPE_API_KEY' 或 'API_KEY' 未设置或为空！")
else:
    # 为了安全，只打印部分key来确认加载成功
    print(f"[配置加载] API Key 加载成功 (开头: {API_KEY[:5]}...)")

if not APP_ID:
    print("[配置错误] 严重错误：环境变量 'APP_ID' 未设置或为空！")
else:
    print(f"[配置加载] App ID 加载成功: {APP_ID}")

def get_llm_client():
    """
    初始化并返回LLM客户端配置信息。
    在云环境中，如果配置不完整，返回 None，让调用者处理。
    """
    # 再次验证配置是否完整
    if not API_KEY or not APP_ID:
        print("警告：由于 API Key 或 App ID 缺失，无法初始化LLM客户端。")
        return None
    
    return {
        "api_key": API_KEY,
        "app_id": APP_ID
    }

