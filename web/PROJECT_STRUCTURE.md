# 项目结构说明

## 📁 完整文件列表

```
web/
├── 📄 核心代码文件
│   ├── api_server.py              # FastAPI 后端服务（主程序）
│   ├── config.py                  # 配置管理（API密钥加载）
│   ├── document_manager.py        # 文档管理模块（文件存储）
│   ├── intent_recognizer.py       # LLM 意图识别模块
│   ├── smart_clip_llm.py          # 核心对话引擎
│   └── main.py                    # 命令行入口（可选）
│
├── 📦 依赖和配置
│   ├── requirements.txt           # Python 依赖包列表
│   ├── config_local.py.example    # 本地配置示例
│   └── env.example                # 环境变量示例
│
├── 🚀 部署配置文件
│   ├── Dockerfile                 # Docker 镜像构建文件
│   ├── .dockerignore              # Docker 构建排除文件
│   ├── Procfile                   # Heroku 部署配置
│   ├── runtime.txt                # Python 版本指定
│   ├── render.yaml                # Render.com 部署配置
│   └── railway.json               # Railway 部署配置
│
├── 🎯 启动脚本
│   ├── start.sh                   # Unix/Linux/Mac 启动脚本
│   └── start.bat                  # Windows 启动脚本
│
├── 📚 文档
│   ├── README.md                  # 项目主文档
│   ├── DEPLOYMENT.md              # 详细部署指南
│   ├── QUICK_START.md             # 5分钟快速开始
│   └── PROJECT_STRUCTURE.md       # 本文件
│
├── 📂 数据目录
│   └── documents/                 # 文档存储目录
│       ├── metadata.json          # 文档元数据
│       └── 默认文档.txt           # 默认文档
│
└── 🔒 忽略文件
    ├── .gitignore                 # Git 忽略规则
    └── .dockerignore              # Docker 忽略规则
```

## 🔍 文件说明

### 核心代码

#### api_server.py
- **功能**：FastAPI 后端服务主程序
- **端口**：默认 8000（可通过环境变量 PORT 配置）
- **关键功能**：
  - 会话管理
  - RESTful API 路由
  - CORS 配置
  - 错误处理

#### config.py
- **功能**：配置管理
- **支持**：
  - 本地配置文件 (config_local.py)
  - 环境变量
  - 默认值
- **配置项**：
  - DASHSCOPE_API_KEY
  - APP_ID

#### document_manager.py
- **功能**：文档管理
- **存储**：本地文件系统 (documents/ 目录)
- **支持操作**：
  - 创建/读取/更新/删除文档
  - 文档定位（开头/结尾/指定位置）
  - 元数据管理

#### intent_recognizer.py
- **功能**：LLM 意图识别
- **使用**：阿里云百炼智能体
- **支持**：
  - 自然语言理解
  - 对话历史管理
  - JSON 格式修复
  - 意图类型映射

#### smart_clip_llm.py
- **功能**：核心引擎（简化版）
- **用途**：API 服务器使用
- **包含**：
  - 文档管理器初始化
  - 意图识别器初始化
  - 会话管理

### 部署相关

#### Dockerfile
- **用途**：Docker 容器化部署
- **基础镜像**：python:3.9-slim
- **端口**：8000
- **环境变量**：DASHSCOPE_API_KEY, APP_ID, PORT

#### Procfile & runtime.txt
- **用途**：Heroku 部署
- **Python 版本**：3.9.18
- **启动命令**：`web: python api_server.py`

#### render.yaml
- **用途**：Render.com 一键部署
- **配置**：自动安装依赖并启动服务

#### railway.json
- **用途**：Railway 平台部署
- **构建器**：NIXPACKS

### 启动脚本

#### start.sh (Unix/Linux/Mac)
- 检查 Python 安装
- 自动安装依赖
- 检查配置文件
- 启动服务

#### start.bat (Windows)
- Windows 批处理版本
- 功能与 start.sh 相同

## 🎯 快速导航

### 想要...

| 目标 | 查看文件 |
|------|---------|
| 了解项目功能 | README.md |
| 5分钟快速部署 | QUICK_START.md |
| 详细部署步骤 | DEPLOYMENT.md |
| 修改 API 逻辑 | api_server.py |
| 调整 LLM 行为 | intent_recognizer.py |
| 更改文档存储 | document_manager.py |
| 配置 API 密钥 | config.py, config_local.py.example |
| 容器化部署 | Dockerfile |

## 📊 代码统计

| 文件类型 | 数量 | 说明 |
|---------|------|------|
| Python 核心代码 | 6 | 约 1500+ 行代码 |
| 配置文件 | 8 | 支持多平台部署 |
| 文档 | 4 | 详尽的使用说明 |
| 启动脚本 | 2 | 跨平台支持 |
| 数据文件 | 2 | 默认文档和元数据 |

## 🔄 工作流程

```
用户请求
    ↓
api_server.py (接收 HTTP 请求)
    ↓
smart_clip_llm.py (会话管理)
    ↓
intent_recognizer.py (意图识别)
    ↓
document_manager.py (文档操作)
    ↓
api_server.py (返回响应)
    ↓
用户接收结果
```

## 🔐 安全说明

### 敏感文件（已在 .gitignore 中）
- `config_local.py` - 本地 API 密钥
- `.env` - 环境变量配置
- `__pycache__/` - Python 缓存
- `*.log` - 日志文件

### 公开文件
- 所有示例配置文件（.example）
- 文档和说明文件
- 源代码文件

## 📝 修改建议

### 添加新功能
1. 在 `intent_recognizer.py` 定义新意图
2. 在 `api_server.py` 添加处理逻辑
3. 更新云端系统提示词
4. 测试并部署

### 更改存储方式
1. 修改 `document_manager.py`
2. 替换文件存储为数据库
3. 更新依赖 (requirements.txt)

### 自定义 API
1. 在 `api_server.py` 添加新路由
2. 定义请求/响应模型
3. 实现业务逻辑
4. 更新 API 文档

## 🆘 故障排除

### 常见问题文件位置

| 问题类型 | 检查文件 |
|---------|---------|
| API 无法启动 | api_server.py, config.py |
| 配置错误 | config_local.py, .env |
| LLM 调用失败 | intent_recognizer.py, config.py |
| 文档读写失败 | document_manager.py, documents/ |
| 部署失败 | Dockerfile, Procfile, *.yaml |

## 📞 获取帮助

- 📖 查看 README.md 了解基本用法
- 🚀 查看 QUICK_START.md 快速上手
- 🌐 查看 DEPLOYMENT.md 了解部署详情
- 🐛 提交 GitHub Issue 报告问题

---

## 📋 检查清单

部署前确认：

- [ ] 已获取 DASHSCOPE_API_KEY
- [ ] 已获取 APP_ID
- [ ] 已上传代码到 GitHub
- [ ] 已在云平台配置环境变量
- [ ] 已测试 API 接口
- [ ] 已查看部署日志确认无错误

---

Made with ❤️ by 灵辑团队


