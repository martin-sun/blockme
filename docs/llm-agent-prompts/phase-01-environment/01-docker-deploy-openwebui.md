# 任务01：Docker 部署 Open WebUI

## 任务目标

在本地使用 Docker 容器化部署 Open WebUI，提供一个稳定的、可持久化数据的 AI 对话平台基础环境。该环境需要支持后续的自定义 Pipelines、Functions 和 Knowledge 管理功能。

## 技术要求

**必需工具：**
- Docker Engine >= 24.0
- Docker Compose >= 2.20
- 至少 4GB 可用内存
- 10GB+ 磁盘空间

**网络要求：**
- 访问 Docker Hub（或配置镜像加速）
- 访问 GitHub（下载配置文件）

## 实现步骤

### 1. 准备工作

首先检查 Docker 环境：
```bash
docker --version
docker compose version
```

确认 Docker 服务运行正常：
```bash
docker ps
```

### 2. 创建项目目录

在项目根目录创建 Open WebUI 部署目录：
```bash
mkdir -p openwebui-deployment
cd openwebui-deployment
```

### 3. 编写 docker-compose.yml

创建一个支持数据持久化和自定义配置的 Docker Compose 文件。关键配置点：

- **数据卷挂载**：确保对话历史、知识库、配置不丢失
- **端口映射**：默认 3000 端口，可根据需要调整
- **环境变量**：预留 API 配置、模型配置等
- **网络模式**：使用 bridge 网络便于后续扩展

### 4. 配置数据持久化

需要挂载以下目录：
- `/app/backend/data`：存储用户数据、对话历史
- `/app/backend/uploads`：上传的文档文件
- `/root/.ollama`（可选）：如果使用本地 Ollama 模型

### 5. 启动服务

使用以下命令启动：
```bash
docker compose up -d
```

查看日志确认启动成功：
```bash
docker compose logs -f
```

## 关键代码提示

**docker-compose.yml 核心结构：**
```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - ./data:/app/backend/data
      - ./uploads:/app/backend/uploads
    environment:
      - WEBUI_SECRET_KEY=your-secret-key-here
    restart: unless-stopped
```

**重要环境变量：**
- `WEBUI_SECRET_KEY`：会话加密密钥（必须设置）
- `ENABLE_RAG_WEB_SEARCH`：启用网络搜索（可选）

## 测试验证

### 1. 访问界面

浏览器访问：`http://localhost:3000`

应该看到 Open WebUI 登录/注册页面。

### 2. 创建管理员账号

首次访问时注册的第一个用户自动成为管理员。

### 3. 验证数据持久化

```bash
# 停止容器
docker compose down

# 重新启动
docker compose up -d

# 确认之前的账号和数据仍然存在
```

### 4. 检查容器健康状态

```bash
docker compose ps
# 状态应为 "Up" 且无错误
```

## 注意事项

**安全配置：**
1. 修改默认端口避免冲突
2. 设置强随机密钥作为 `WEBUI_SECRET_KEY`
3. 如果公网访问，务必配置 HTTPS 和防火墙

**性能优化：**
1. 根据使用规模调整容器资源限制
2. 定期清理旧日志和未使用的文档
3. 使用 SSD 存储数据卷提升性能

**常见问题：**
- **端口被占用**：修改 docker-compose.yml 中的端口映射
- **容器无法启动**：检查 Docker 日志 `docker logs open-webui`
- **数据丢失**：确认卷挂载路径正确且有写入权限

**后续扩展预留：**
- 预留额外端口用于 Pipelines 服务（建议 9099）
- 配置独立的数据库（PostgreSQL）替代默认 SQLite
- 使用 Docker 网络连接其他服务（Ollama、向量数据库等）

## 依赖关系

**前置任务：** 无

**后置任务：**
- 任务02：配置 Claude API 接入
- 任务03：配置 GLM API 接入
