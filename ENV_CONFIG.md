# 环境变量配置说明

本项目使用 `.env` 文件来管理环境变量配置。请按照以下步骤进行配置：

## 1. 创建 .env 文件

在 `poc-backend` 目录下创建 `.env` 文件：

```bash
cp .env.example .env  # 如果有示例文件
# 或者直接创建新文件
touch .env
```

## 2. 配置环境变量

在 `.env` 文件中添加以下配置：

```env
# Database Configuration
DATABASE_URL=sqlite:///./data/app.db

# OpenAI Configuration
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

# CORS Configuration (JSON格式或逗号分隔)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
# 或者使用逗号分隔: BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

## 3. 配置说明

### 必需配置

- **OPENAI_API_KEY**: OpenAI API密钥，用于AI功能
  - 获取方式：访问 https://platform.openai.com/api-keys
  - 如果不配置，AI功能将使用模拟模式

### 可选配置

- **DATABASE_URL**: 数据库连接字符串
  - 默认使用SQLite: `sqlite:///./data/app.db`
  - 支持PostgreSQL: `postgresql://user:password@localhost/dbname`

- **HOST/PORT**: 服务器监听地址和端口
  - 默认: `0.0.0.0:8000`

- **DEBUG**: 调试模式
  - `true`: 启用调试模式，自动重载
  - `false`: 生产模式

- **BACKEND_CORS_ORIGINS**: 允许的跨域源
  - 支持JSON格式或逗号分隔的字符串

## 4. 安全注意事项

- **不要将 `.env` 文件提交到版本控制系统**
- 生产环境中请更改 `SECRET_KEY`
- 妥善保管 `OPENAI_API_KEY`

## 5. 环境变量优先级

1. 系统环境变量（最高优先级）
2. `.env` 文件中的变量
3. 代码中的默认值（最低优先级）

## 6. 验证配置

启动服务器后，可以访问以下端点验证配置：

- `GET /`: 查看基本信息和OpenAI配置状态
- `GET /health`: 健康检查
- `GET /docs`: API文档

配置成功后，控制台会显示配置加载信息。 