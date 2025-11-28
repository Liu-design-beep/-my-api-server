# 灵辑 (Smart Clip) - AI 内容收藏助手

基于阿里云百炼大模型的智能文档管理助手，支持自然语言交互。

## 📋 功能特性

- **自然语言交互**：使用自然语言添加、查看、管理文档内容
- **智能意图识别**：基于 LLM 的意图识别，理解复杂指令
- **文档管理**：支持多文档管理、切换、内容定位
- **RESTful API**：FastAPI 后端，支持前后端分离
- **会话管理**：支持多用户会话隔离

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

#### 方式一：使用配置文件（推荐本地开发）

```bash
cp config_local.py.example config_local.py
```

编辑 `config_local.py`，填入您的 API 密钥：

```python
DASHSCOPE_API_KEY = "your_dashscope_api_key"
APP_ID = "your_app_id"
```

#### 方式二：使用环境变量（推荐云部署）

```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"
export APP_ID="your_app_id"
```

#### 获取 API 密钥

1. **DASHSCOPE_API_KEY**：访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/apiKey)
2. **APP_ID**：访问 [阿里云百炼应用中心](https://bailian.console.aliyun.com/)，创建或选择您的应用

### 4. 启动服务

```bash
python api_server.py
```

服务将在 `http://0.0.0.0:8000` 启动。

访问 API 文档：`http://localhost:8000/docs`

## 📡 API 接口

### 1. 聊天接口

**POST** `/api/chat`

```json
{
  "session_id": "optional_session_id",
  "text": "把测试内容加到默认文档"
}
```

**响应**：

```json
{
  "response_type": "TEXT",
  "content": "已成功将内容添加到文档...",
  "new_session_id": "session_xxx"
}
```

### 2. 文档列表

**GET** `/api/documents?session_id=xxx`

**响应**：

```json
{
  "documents": ["默认文档", "学习笔记"]
}
```

## 🌐 云部署指南

### Render / Railway / Heroku

1. 将代码推送到 GitHub
2. 在平台上创建新应用
3. 连接 GitHub 仓库
4. 设置环境变量：
   - `DASHSCOPE_API_KEY`
   - `APP_ID`
   - `PORT`（可选，默认 8000）
5. 设置启动命令：`python api_server.py`

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000

CMD ["python", "api_server.py"]
```

构建和运行：

```bash
docker build -t smart-clip .
docker run -p 8000:8000 \
  -e DASHSCOPE_API_KEY=your_key \
  -e APP_ID=your_app_id \
  smart-clip
```

## 📁 项目结构

```
web/
├── api_server.py           # FastAPI 后端服务
├── config.py               # 配置管理
├── config_local.py.example # 配置示例
├── document_manager.py     # 文档管理模块
├── intent_recognizer.py    # LLM 意图识别
├── smart_clip_llm.py       # 核心引擎
├── main.py                 # 命令行入口
├── requirements.txt        # Python 依赖
├── documents/              # 文档存储目录
│   ├── metadata.json       # 文档元数据
│   └── *.txt               # 文档文件
└── README.md               # 项目文档
```

## 🛠️ 使用示例

### 添加内容

```
用户：把今天的会议要点加到项目周报
AI：已成功将内容添加到文档 '项目周报' 的结尾。
```

### 查看文档

```
用户：显示项目周报
AI：[返回文档内容]
```

### 切换文档

```
用户：打开学习笔记
AI：已切换到文档：学习笔记
```

### 删除内容

```
用户：清空默认文档
AI：您确定要清空文档 '默认文档' 的所有内容吗？
用户：确认
AI：✅ 已成功清空文档 '默认文档' 的所有内容。
```

## ⚙️ 配置说明

### 环境变量

- `DASHSCOPE_API_KEY`：阿里云 DashScope API 密钥（必需）
- `APP_ID`：百炼应用 ID（必需）
- `PORT`：服务端口（可选，默认 8000）

### CORS 配置

默认允许所有来源访问。如需限制，请修改 `api_server.py` 中的 `allow_origins`。

## 📝 开发说明

### 添加新功能

1. 在 `intent_recognizer.py` 中定义新的意图类型
2. 在 `api_server.py` 中实现对应的处理逻辑
3. 更新系统提示词（在阿里云百炼控制台）

### 测试 API

访问 `http://localhost:8000/docs` 使用 Swagger UI 进行交互式测试。

## 🐛 故障排除

### 问题：API 调用失败

**解决方案**：

1. 检查 API 密钥是否正确配置
2. 确认网络连接正常
3. 查看服务器日志获取详细错误信息

### 问题：文档内容丢失

**解决方案**：

文档存储在 `documents/` 目录下，确保该目录有写入权限。

### 问题：端口被占用

**解决方案**：

修改环境变量 `PORT` 或在 `api_server.py` 中更改默认端口。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题，请在 GitHub 上提交 Issue。

---

Made with ❤️ by 灵辑团队


