# 云部署指南

本文档详细说明如何将灵辑 (Smart Clip) API 部署到各种云平台。

## 📦 准备工作

### 1. 获取 API 密钥

部署前，您需要准备以下信息：

- **DASHSCOPE_API_KEY**：阿里云 DashScope API 密钥
  - 获取地址：https://dashscope.console.aliyun.com/apiKey
  
- **APP_ID**：阿里云百炼应用 ID
  - 获取地址：https://bailian.console.aliyun.com/
  - 在"应用中心"创建或选择一个应用

### 2. 上传到 GitHub

将 `web` 文件夹作为独立仓库上传到 GitHub：

```bash
cd web
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/smart-clip-api.git
git push -u origin main
```

## 🚀 部署到 Render.com（推荐）

Render 提供免费层级，适合个人项目。

### 步骤

1. **注册 Render 账号**
   - 访问 https://render.com 并注册

2. **创建 Web Service**
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - 选择您的 `smart-clip-api` 仓库

3. **配置服务**
   - **Name**: `smart-clip-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`

4. **设置环境变量**
   - 点击 "Environment" 标签
   - 添加以下环境变量：
     - `DASHSCOPE_API_KEY` = `your_api_key`
     - `APP_ID` = `your_app_id`
     - `PORT` = `8000`

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成（约 2-5 分钟）

6. **访问 API**
   - 部署完成后，Render 会提供一个 URL
   - 访问 `https://your-app.onrender.com/docs` 查看 API 文档

### 注意事项

- 免费层级的服务在 15 分钟无活动后会休眠
- 首次访问可能需要几秒钟启动
- 如需持续运行，考虑升级到付费计划

## 🌐 部署到 Railway

Railway 提供简单的部署流程和慷慨的免费额度。

### 步骤

1. **注册 Railway 账号**
   - 访问 https://railway.app 并注册

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 授权并选择您的仓库

3. **配置环境变量**
   - 项目创建后，点击项目
   - 进入 "Variables" 标签
   - 添加：
     - `DASHSCOPE_API_KEY`
     - `APP_ID`
     - `PORT`

4. **部署**
   - Railway 会自动检测 Python 项目并部署
   - 查看日志确认部署成功

5. **生成域名**
   - 点击 "Settings" → "Generate Domain"
   - 访问生成的域名测试 API

## ☁️ 部署到 Heroku

Heroku 是经典的云平台选择。

### 步骤

1. **安装 Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # 下载安装程序：https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **登录 Heroku**
   ```bash
   heroku login
   ```

3. **创建应用**
   ```bash
   cd web
   heroku create your-app-name
   ```

4. **设置环境变量**
   ```bash
   heroku config:set DASHSCOPE_API_KEY="your_key"
   heroku config:set APP_ID="your_app_id"
   ```

5. **部署**
   ```bash
   git push heroku main
   ```

6. **访问应用**
   ```bash
   heroku open
   ```

## 🐋 使用 Docker 部署

适用于任何支持 Docker 的云平台（AWS ECS, Google Cloud Run, Azure 等）。

### 本地测试

```bash
cd web

# 构建镜像
docker build -t smart-clip-api .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e DASHSCOPE_API_KEY="your_key" \
  -e APP_ID="your_app_id" \
  --name smart-clip \
  smart-clip-api

# 查看日志
docker logs -f smart-clip

# 访问 API
curl http://localhost:8000/
```

### 部署到 Docker Hub

```bash
# 登录 Docker Hub
docker login

# 标记镜像
docker tag smart-clip-api your-username/smart-clip-api:latest

# 推送镜像
docker push your-username/smart-clip-api:latest
```

### 部署到云平台

#### Google Cloud Run

```bash
# 安装 gcloud CLI 并认证
gcloud auth login

# 构建并推送到 Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/smart-clip-api

# 部署到 Cloud Run
gcloud run deploy smart-clip-api \
  --image gcr.io/YOUR_PROJECT_ID/smart-clip-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars DASHSCOPE_API_KEY=your_key,APP_ID=your_app_id \
  --allow-unauthenticated
```

#### AWS ECS

```bash
# 推送到 ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag smart-clip-api:latest \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/smart-clip-api:latest

docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/smart-clip-api:latest

# 在 ECS 控制台创建服务并配置环境变量
```

## 🔧 自定义域名

### Render

1. 在 Render 控制台进入您的服务
2. 点击 "Settings" → "Custom Domain"
3. 添加您的域名
4. 按提示在域名提供商处配置 DNS

### Railway

1. 进入项目 "Settings"
2. 在 "Domains" 部分添加自定义域名
3. 配置 DNS CNAME 记录

### Heroku

```bash
heroku domains:add www.yourdomain.com
heroku domains:add yourdomain.com
```

然后在 DNS 提供商配置 CNAME 记录。

## 📊 监控和日志

### 查看日志

**Render**:
- 在服务页面点击 "Logs"

**Railway**:
- 在项目页面点击 "Deployments" → 选择部署 → "View Logs"

**Heroku**:
```bash
heroku logs --tail
```

**Docker**:
```bash
docker logs -f smart-clip
```

### 性能监控

建议集成监控服务：
- **Sentry**：错误追踪
- **New Relic**：性能监控
- **Datadog**：全面监控

## 🔒 安全建议

1. **不要在代码中硬编码 API 密钥**
   - 始终使用环境变量

2. **限制 CORS**
   - 在 `api_server.py` 中配置 `allow_origins` 只允许您的前端域名

3. **添加认证**
   - 考虑添加 API Key 或 JWT 认证

4. **HTTPS**
   - 确保使用 HTTPS（大多数云平台自动提供）

5. **速率限制**
   - 使用 `slowapi` 等库添加速率限制

## 🐛 常见问题

### 问题：部署后 API 无法访问

**解决方案**：
1. 检查端口配置是否正确（使用 `PORT` 环境变量）
2. 确认防火墙规则允许入站流量
3. 查看部署日志查找错误

### 问题：环境变量未生效

**解决方案**：
1. 重新部署应用
2. 检查环境变量名称拼写
3. 确认环境变量值没有引号（除非需要）

### 问题：文档内容丢失

**解决方案**：
1. 云平台的文件系统通常是临时的
2. 考虑使用持久化存储（如 AWS S3、云数据库）
3. 或在每次部署前备份 `documents/` 文件夹

### 问题：API 响应慢

**解决方案**：
1. 升级到更高性能的计划
2. 使用 CDN 加速
3. 优化代码（添加缓存、减少 LLM 调用）

## 📞 获取帮助

- 查看主 README.md
- 提交 GitHub Issue
- 查阅云平台文档

---

祝部署顺利！🎉


