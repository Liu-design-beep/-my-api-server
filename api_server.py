# api_server.py
# 灵辑 (Smart Clip) - FastAPI 后端服务
# 将现有的Python逻辑封装为RESTful API

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from smart_clip_llm import SmartClipLLM
from document_manager import DocumentManager

# ============================================
# FastAPI 应用初始化
# ============================================
app = FastAPI(
    title="灵辑 API",
    description="智能笔记助手后端API",
    version="1.0.0"
)

# ============================================
# CORS 配置（允许前端跨域请求）
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 云部署时允许所有来源，最方便的配置
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 会话管理器
# ============================================
class SessionManager:
    """
    管理用户会话，每个session_id对应一个SmartClipLLM实例
    """
    def __init__(self):
        self.sessions: Dict[str, SmartClipLLM] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, SmartClipLLM]:
        """
        获取或创建会话
        
        Args:
            session_id: 会话ID，如果为None则创建新会话
            
        Returns:
            (session_id, SmartClipLLM实例)
        """
        if session_id and session_id in self.sessions:
            return session_id, self.sessions[session_id]
        
        # 创建新会话
        new_session_id = session_id or f"session_{uuid.uuid4().hex[:16]}"
        self.sessions[new_session_id] = SmartClipLLM()
        return new_session_id, self.sessions[new_session_id]
    
    def get_documents(self, session_id: str) -> list[str]:
        """
        获取指定会话的文档列表
        
        Args:
            session_id: 会话ID
            
        Returns:
            文档标题列表
        """
        if session_id not in self.sessions:
            return []
        
        app_instance = self.sessions[session_id]
        return list(app_instance.doc_manager.documents.keys())

# 全局会话管理器实例
session_manager = SessionManager()

# ============================================
# 请求/响应模型
# ============================================

class ChatRequest(BaseModel):
    """聊天请求模型"""
    session_id: Optional[str] = None
    text: str

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response_type: str  # "TEXT" | "CONFIRMATION" | "DOCUMENT"
    content: str
    new_session_id: Optional[str] = None

class DocumentsResponse(BaseModel):
    """文档列表响应模型"""
    documents: list[str]

# ============================================
# API 路由
# ============================================

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "灵辑 API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "documents": "/api/documents"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天消息
    
    这个接口接收用户的文本输入，通过SmartClipLLM处理，
    返回AI的回复或需要确认的操作。
    """
    try:
        # 获取或创建会话
        session_id, app_instance = session_manager.get_or_create_session(request.session_id)
        
        # 处理用户输入
        user_input = request.text.strip()
        if not user_input:
            raise HTTPException(status_code=400, detail="输入不能为空")
        
        # 【优化】优先处理"确认"/"取消"命令，避免调用LLM导致识别错误
        # 如果存在待确认的操作，优先检查是否是明确的确认/取消命令
        if app_instance.pending_action:
            user_input_lower = user_input.lower().strip()
            # 检查是否是明确的确认命令
            if user_input_lower in ['确认', 'confirm', 'yes', 'y', '是', '好的', '好']:
                # 直接处理确认操作，不调用LLM
                action = app_instance.pending_action
                if action["intent"] == "DELETE_CONTENT":
                    app_instance.doc_manager.clear_document(action["title"])
                    app_instance.pending_action = None
                    return ChatResponse(
                        response_type="TEXT",
                        content=f"✅ 已成功清空文档 '{action['title']}' 的所有内容。",
                        new_session_id=session_id if not request.session_id else None
                    )
            # 检查是否是明确的取消命令
            elif user_input_lower in ['取消', 'cancel', 'no', 'n', '否', '不']:
                action = app_instance.pending_action
                app_instance.pending_action = None
                return ChatResponse(
                    response_type="TEXT",
                    content=f"❌ 已取消清空文档 '{action['title']}' 的操作。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        # 调用SmartClipLLM的意图识别和处理逻辑
        # 我们需要模拟run()方法中的处理流程，但不使用input()，而是直接处理
        intent_data = app_instance.intent_recognizer.recognize(user_input)
        
        # 检查是否需要确认
        confirmation_needed = intent_data.get("confirmation_needed", False)
        intent = intent_data.get("intent")
        
        # 处理不同类型的意图
        if intent == "CONFIRM":
            # 用户确认操作
            if app_instance.pending_action:
                # 执行待确认的操作
                action = app_instance.pending_action
                if action["intent"] == "DELETE_CONTENT":
                    app_instance.doc_manager.clear_document(action["title"])
                    app_instance.pending_action = None
                    return ChatResponse(
                        response_type="TEXT",
                        content=f"已成功清空文档 '{action['title']}' 的所有内容。",
                        new_session_id=session_id if not request.session_id else None
                    )
            else:
                return ChatResponse(
                    response_type="TEXT",
                    content="没有待确认的操作。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        elif intent == "CANCEL":
            # 用户取消操作
            if app_instance.pending_action:
                action = app_instance.pending_action
                app_instance.pending_action = None
                return ChatResponse(
                    response_type="TEXT",
                    content=f"已取消清空文档 '{action['title']}' 的操作。",
                    new_session_id=session_id if not request.session_id else None
                )
            else:
                return ChatResponse(
                    response_type="TEXT",
                    content="没有待确认的操作。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        elif intent == "DELETE_CONTENT" and confirmation_needed:
            # 需要确认的删除操作
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            app_instance.pending_action = {
                "intent": "DELETE_CONTENT",
                "title": doc_title
            }
            return ChatResponse(
                response_type="CONFIRMATION",
                content=f"您确定要清空文档 '{doc_title}' 的所有内容吗？此操作不可恢复。",
                new_session_id=session_id if not request.session_id else None
            )
        
        elif intent == "DELETE_CONTENT":
            # 直接删除（不需要确认的情况，理论上不应该发生，但保留作为兜底）
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            app_instance.doc_manager.clear_document(doc_title)
            return ChatResponse(
                response_type="TEXT",
                content=f"已成功清空文档 '{doc_title}' 的所有内容。",
                new_session_id=session_id if not request.session_id else None
            )
        
        elif intent == "ADD_CONTENT":
            # 添加内容
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            content = intent_data.get("content", "")
            position = intent_data.get("position", "end")
            
            # 确保position不为None
            if position is None:
                position = "end"
            
            app_instance.doc_manager.add_content(doc_title, content, position)
            return ChatResponse(
                response_type="TEXT",
                content=f"已成功将内容添加到文档 '{doc_title}' 的{('开头' if position.lower() == 'start' else '结尾')}。",
                new_session_id=session_id if not request.session_id else None
            )
        
        elif intent == "SET_ACTIVE":
            # 切换文档
            doc_title = intent_data.get("doc_title")
            if doc_title:
                app_instance.doc_manager.set_active_document(doc_title)
                return ChatResponse(
                    response_type="TEXT",
                    content=f"已切换到文档：{doc_title}",
                    new_session_id=session_id if not request.session_id else None
                )
            else:
                return ChatResponse(
                    response_type="TEXT",
                    content="未指定要切换的文档。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        elif intent == "DISPLAY_DOC":
            # 显示文档内容
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            doc_content = app_instance.doc_manager.documents.get(doc_title)
            if doc_content and len(doc_content) > 0:
                # 将文档内容列表合并为字符串
                content = '\n'.join(doc_content)
                return ChatResponse(
                    response_type="DOCUMENT",
                    content=content,
                    new_session_id=session_id if not request.session_id else None
                )
            else:
                return ChatResponse(
                    response_type="TEXT",
                    content=f"文档 '{doc_title}' 不存在或为空。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        elif intent == "HELP":
            # 帮助信息
            # 检查LLM是否生成了内容
            content = intent_data.get("content")
            if content and isinstance(content, str) and len(content.strip()) > 0:
                return ChatResponse(
                    response_type="TEXT",
                    content=content,
                    new_session_id=session_id if not request.session_id else None
                )
            else:
                help_text = """我能理解以下指令：
1. 添加内容：'把[内容]加到[文档名]的[开头/结尾/某个段落之后]'
   示例：'把今天的会议要点加到项目周报的结尾'
2. 切换文档：'打开[文档名]'
   示例：'打开学习笔记'
3. 查看文档：'查看[文档名]'
   示例：'显示项目周报'
4. 删除/清空文档：'删除[文档名]所有内容' 或 '清空[文档名]'
   示例：'删除默认文档所有内容'
5. 重置对话：'重置对话' 或 '清空对话历史'
   示例：'重置对话'（清空对话历史，重新开始）
6. 退出：'退出'"""
                return ChatResponse(
                    response_type="TEXT",
                    content=help_text,
                    new_session_id=session_id if not request.session_id else None
                )
        
        elif intent == "RESET_CONVERSATION" or intent == "CLEAR_CONVERSATION":
            # 重置对话
            app_instance.intent_recognizer.reset_conversation()
            if app_instance.pending_action:
                app_instance.pending_action = None
            return ChatResponse(
                response_type="TEXT",
                content="对话历史已重置，可以重新开始对话了。",
                new_session_id=session_id if not request.session_id else None
            )
        
        elif intent == "EXIT":
            # 退出（在API中，我们只返回消息，不实际退出）
            return ChatResponse(
                response_type="TEXT",
                content="感谢您的使用，再见！",
                new_session_id=session_id if not request.session_id else None
            )
        
        else:
            # 未知意图或UNKNOWN
            return ChatResponse(
                response_type="TEXT",
                content=intent_data.get("content", "抱歉，我没有理解您的指令。请尝试使用更清晰的表达。"),
                new_session_id=session_id if not request.session_id else None
            )
    
    except Exception as e:
        # 捕获所有异常并返回友好的错误消息
        import traceback
        error_detail = str(e)
        print(f"[API错误] {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时发生错误：{error_detail}"
        )

@app.get("/api/documents", response_model=DocumentsResponse)
async def get_documents(session_id: Optional[str] = None):
    """
    获取文档列表
    
    如果提供了session_id，返回该会话的文档列表；
    否则返回默认文档列表。
    """
    try:
        if session_id:
            documents = session_manager.get_documents(session_id)
        else:
            # 如果没有session_id，创建一个临时实例来获取文档列表
            temp_manager = DocumentManager()
            documents = list(temp_manager.documents.keys())
        
        return DocumentsResponse(documents=documents)
    
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[API错误] {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"获取文档列表时发生错误：{error_detail}"
        )

# ============================================
# 启动服务器
# ============================================
if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为 8000
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("灵辑 API 服务器启动中...")
    print("=" * 60)
    print(f"API文档地址: http://0.0.0.0:{port}/docs" )
    print(f"API根路径: http://0.0.0.0:{port}/" )
    print(f"聊天接口: http://0.0.0.0:{port}/api/chat" )
    print(f"文档列表: http://0.0.0.0:{port}/api/documents" )
    print("=" * 60)
    # 云部署时使用 0.0.0.0 监听所有网络接口
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
