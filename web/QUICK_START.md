# 快速开始指南

## 🎯 5分钟快速部署到云端

### 第一步：准备 API 密钥

访问以下网址获取密钥：

1. **阿里云 DashScope API Key**
   - 🔗 https://dashscope.console.aliyun.com/apiKey
   - 点击"创建新的 API-KEY"并复制

2. **百炼应用 ID**
   - 🔗 https://bailian.console.aliyun.com/
   - 进入"应用中心" → 创建或选择应用 → 复制"应用 ID"

### 第二步：上传到 GitHub

```bash
# 1. 在 GitHub 上创建新仓库（不要添加 README）
# 2. 在本地执行：

cd web
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/smart-clip-api.git
git push -u origin main
```

### 第三步：部署到 Render（免费）

1. **注册 Render**
   - 🔗 https://render.com
   - 使用 GitHub 账号登录

2. **创建服务**
   - 点击 "New +" → "Web Service"
   - 选择刚才创建的 GitHub 仓库
   - 点击 "Connect"

3. **配置**
   - **Name**: `smart-clip-api` （或任意名称）
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`
   - **Free** 计划即可

4. **设置环境变量**
   - 在 "Environment" 标签下添加：
     - `DASHSCOPE_API_KEY` = `你的API密钥`
     - `APP_ID` = `你的应用ID`

5. **部署**
   - 点击 "Create Web Service"
   - 等待 2-3 分钟

6. **完成！**
   - 复制 Render 提供的 URL
   - 访问 `https://你的应用.onrender.com/docs` 测试 API

### 第四步：测试 API

访问 API 文档页面，点击 "POST /api/chat" 测试：

```json
{
  "text": "把测试内容加到默认文档"
}
```

应该收到类似响应：

```json
{
  "response_type": "TEXT",
  "content": "已成功将内容添加到文档...",
  "new_session_id": "session_xxx"
}
```

## 🎉 恭喜！

您的 AI 助手 API 已经成功部署到云端！

## 📱 下一步

### 连接前端

如果您有前端应用，修改 API 地址为：

```javascript
const API_BASE_URL = "https://你的应用.onrender.com";
```

### 自定义域名

1. 在 Render 控制台 → Settings → Custom Domain
2. 添加您的域名
3. 在域名提供商处配置 DNS

### 查看日志

- Render 控制台 → 您的服务 → Logs

## ⚠️ 注意事项

### 免费计划限制

- Render 免费计划在 15 分钟无活动后会休眠
- 首次访问需要等待几秒唤醒
- 如需 24/7 运行，升级到 $7/月 计划

### 保护 API

建议添加认证机制：

```python
# api_server.py 中添加
from fastapi import Header, HTTPException

async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != "your_secret_key":
        raise HTTPException(status_code=403, detail="Invalid API Key")

# 在路由中使用
@app.post("/api/chat", dependencies=[Depends(verify_token)])
async def chat(request: ChatRequest):
    # ...
```

## 🆘 遇到问题？

### API 无法访问
- 检查 Render 日志查看错误
- 确认环境变量已正确设置
- 确认构建和启动命令正确

### LLM 调用失败
- 检查 API 密钥是否有效
- 确认账户余额充足
- 查看阿里云控制台的调用日志

### 文档内容丢失
- Render 的文件系统在重启后会重置
- 考虑使用数据库或对象存储持久化数据

## 📚 更多资源

- 📖 完整部署指南：`DEPLOYMENT.md`
- 📖 API 文档：`README.md`
- 🐛 问题反馈：GitHub Issues

---

Made with ❤️ by 灵辑团队


