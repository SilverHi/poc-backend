# POC Backend

基于 FastAPI 的后端服务，支持 Agent 管理、资源管理和 AI 集成。

## 功能特性

- **Agent 管理**: 创建、更新、删除和执行自定义 AI 代理
- **资源管理**: 文件上传、解析和存储（支持 PDF、Markdown、文本文件）
- **AI 集成**: OpenAI API 集成，支持模拟模式
- **数据库**: SQLite 数据库存储
- **文件处理**: 自动文件解析和内容提取
- **环境变量配置**: 使用 `.env` 文件管理配置

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: SQLite + SQLAlchemy 2.0.23
- **AI**: OpenAI API
- **文件处理**: PyPDF2, python-markdown
- **异步**: aiofiles
- **验证**: Pydantic 2.5.0
- **配置管理**: python-dotenv

## 项目结构

```
poc-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models/              # 数据模型
│   │   ├── agent.py
│   │   └── resource.py
│   ├── schemas/             # Pydantic模式
│   │   ├── agent.py
│   │   ├── resource.py
│   │   └── config.py
│   ├── api/                 # API路由
│   │   ├── agents.py
│   │   ├── resources.py
│   │   └── config.py
│   ├── services/            # 业务逻辑
│   │   ├── agent_service.py
│   │   ├── resource_service.py
│   │   └── ai_service.py
│   ├── core/                # 核心配置
│   │   ├── config.py
│   │   └── database.py
│   └── utils/               # 工具函数
│       └── file_parser.py
├── uploads/                 # 文件上传目录
├── data/                    # 数据库文件目录
├── requirements.txt         # 依赖包
├── config.py               # 配置文件
├── run.py                  # 启动脚本
├── env.template            # 环境变量模板
├── ENV_CONFIG.md           # 环境变量配置详细说明
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd poc-backend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 复制模板文件
cp env.template .env

# 或者手动创建
touch .env
```

在 `.env` 文件中添加以下配置：

```env
# Database Configuration
DATABASE_URL=sqlite:///./data/app.db

# OpenAI Configuration (必需 - 用于AI功能)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_DEFAULT_TEMPERATURE=0.7
OPENAI_DEFAULT_MAX_TOKENS=1000

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=POC Backend
VERSION=1.0.0
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

> **重要**: 请将 `your_openai_api_key_here` 替换为您的实际 OpenAI API 密钥。
> 获取方式：访问 https://platform.openai.com/api-keys

### 3. 启动服务

```bash
# 使用启动脚本（推荐）
python run.py

# 或直接使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后，您会看到配置加载信息：

```
🔧 Configuration loaded:
   - Database: sqlite:///./data/app.db
   - OpenAI configured: True
   - Upload directory: ./uploads
   - CORS origins: ['http://localhost:3000', 'http://localhost:5173']
   - Debug mode: True
```

### 4. 验证安装

访问以下端点验证服务是否正常运行：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **根路径**: http://localhost:8000/

## 环境变量配置详解

### 必需配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | `None` | `sk-...` |

### 可选配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./data/app.db` | `postgresql://user:pass@localhost/db` |
| `HOST` | 服务器监听地址 | `0.0.0.0` | `127.0.0.1` |
| `PORT` | 服务器端口 | `8000` | `3001` |
| `DEBUG` | 调试模式 | `true` | `false` |
| `MAX_FILE_SIZE` | 最大文件大小（字节） | `10485760` | `20971520` |
| `UPLOAD_DIR` | 文件上传目录 | `./uploads` | `/var/uploads` |
| `SECRET_KEY` | 安全密钥 | `your-secret-key-change-in-production` | `your-random-secret` |
| `LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG` |

### CORS 配置

`BACKEND_CORS_ORIGINS` 支持两种格式：

```env
# JSON 格式（推荐）
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# 逗号分隔格式
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## API 接口

### Agent 管理

- `GET /api/v1/agents` - 获取 Agent 列表
- `POST /api/v1/agents` - 创建新 Agent
- `GET /api/v1/agents/{id}` - 获取单个 Agent
- `PUT /api/v1/agents/{id}` - 更新 Agent
- `DELETE /api/v1/agents/{id}` - 删除 Agent
- `POST /api/v1/agents/{id}/execute` - 执行 Agent

### 资源管理

- `GET /api/v1/resources` - 获取资源列表
- `POST /api/v1/resources/upload` - 上传文件
- `GET /api/v1/resources/{id}` - 获取单个资源
- `PUT /api/v1/resources/{id}` - 更新资源
- `DELETE /api/v1/resources/{id}` - 删除资源

### 配置管理

- `GET /api/v1/config/openai` - 获取 OpenAI 配置
- `POST /api/v1/config/openai` - 更新 OpenAI 配置

## 使用说明

### 1. 创建 Agent

```json
POST /api/v1/agents
{
  "name": "需求分析师",
  "description": "专门分析和整理产品需求的AI助手",
  "icon": "📋",
  "category": "analysis",
  "color": "#1890ff",
  "system_prompt": "你是一个专业的需求分析师...",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### 2. 上传资源

```bash
curl -X POST "http://localhost:8000/api/v1/resources/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "title=产品需求文档" \
  -F "description=完整的产品需求文档" \
  -F "file=@document.pdf"
```

### 3. 执行 Agent

```json
POST /api/v1/agents/{agent_id}/execute
{
  "input": "请分析这个产品需求文档..."
}
```

## 安全注意事项

1. **不要将 `.env` 文件提交到版本控制系统**
2. **生产环境中请更改 `SECRET_KEY`**
3. **妥善保管 `OPENAI_API_KEY`**
4. **生产环境中设置 `DEBUG=false`**
5. **限制 CORS 源为实际需要的域名**

## 开发

### 环境变量优先级

1. 系统环境变量（最高优先级）
2. `.env` 文件中的变量
3. 代码中的默认值（最低优先级）

### 添加新的配置项

1. 在 `config.py` 的 `Settings` 类中添加新字段
2. 在 `.env.template` 中添加对应的环境变量
3. 更新 `ENV_CONFIG.md` 文档

### 添加新的文件类型支持

在 `app/utils/file_parser.py` 中添加新的解析方法。

### 扩展 Agent 功能

在 `app/services/agent_service.py` 中添加新的业务逻辑。

### 添加新的 API 端点

1. 在 `app/api/` 中创建新的路由文件
2. 在 `app/main.py` 中注册路由

## 故障排除

### 常见问题

1. **配置加载失败**: 检查 `.env` 文件格式和权限
2. **OpenAI API 错误**: 验证 API 密钥是否正确
3. **数据库连接错误**: 检查 `data/` 目录权限
4. **文件上传失败**: 检查 `uploads/` 目录权限
5. **CORS 错误**: 检查 `BACKEND_CORS_ORIGINS` 配置
6. **依赖安装失败**: 使用 Python 3.12+ 版本

### 调试模式

启用调试模式查看详细配置信息：

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### 验证配置

使用以下命令验证配置是否正确加载：

```bash
python -c "from config import settings; print('✅ 配置加载成功'); print(f'OpenAI配置状态: {settings.is_openai_configured}')"
``` 