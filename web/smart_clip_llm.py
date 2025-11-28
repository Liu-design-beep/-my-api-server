# smart_clip_llm.py
# 灵辑 (Smart Clip) - AI 内容收藏助手 LLM增强版 (基于通义千问)
# 核心对话引擎 (Core Conversation Engine)

from document_manager import DocumentManager
from intent_recognizer import LLMIntentRecognizer
from config import get_llm_client

class SmartClipLLM:
    def __init__(self):
        self.doc_manager = DocumentManager()
        self.client_config = get_llm_client()
        self.intent_recognizer = LLMIntentRecognizer(self.doc_manager, self.client_config)
        # 重置对话历史，确保每次启动时都是干净的状态
        # 这可以避免之前对话历史中的错误格式（如双大括号）影响后续的回复
        self.intent_recognizer.reset_conversation()
        self.is_running = True
        # 待确认的操作（用于二次确认机制）
        self.pending_action = None


