# 安装指南

## 目录
- [环境要求](#环境要求)
- [后端安装](#后端安装)
- [前端安装](#前端安装)
- [数据库配置](#数据库配置)
- [OCR 引擎安装](#ocr-引擎安装)

## 环境要求

### 基本环境
- Python 3.10+
- Node.js 16+
- Docker 和 Docker Compose
- PostgreSQL 14+

### 推荐的开发工具
- VSCode
  - Python 扩展
  - SQLTools
  - PostgreSQL 扩展
- DBeaver（数据库管理工具）

## 后端安装

1. 创建并激活虚拟环境：
```bash
conda create -n ckgcus python=3.10
conda activate ckgcus
```

2. 安装依赖：
```bash
cd backend
pip install -e .         # 安装基本依赖
pip install -e ".[dev]"  # 安装开发依赖
```

3. 配置环境变量：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/ckgcus
ENVIRONMENT=development
```

## 前端安装

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 配置环境变量：
```bash
cp .env.example .env
```

## 数据库配置

1. 启动 PostgreSQL：
```bash
# 在项目根目录下
docker-compose up -d db
```

2. 验证数据库连接：
```bash
# 使用 psql 连接数据库
docker-compose exec db psql -U dev_user -d ckgcus
```

3. 运行数据库迁移：
```bash
cd backend
alembic upgrade head
```

### 数据库管理工具

推荐使用以下工具之一来管理数据库：
- DBeaver（免费、跨平台）
- pgAdmin 4（PostgreSQL 官方工具）
- VSCode + SQLTools 扩展

连接信息：
- Host: localhost
- Port: 5432
- Database: ckgcus
- Username: dev_user
- Password: dev_password

## OCR 引擎安装

### CnOCR（默认）
默认已随基础安装包含，无需额外操作。如果需要单独安装：
```bash
pip install -e .
```

### PaddleOCR（可选）
1. 安装 Python 包：
```bash
pip install -e ".[paddleocr]"
```

2. 可选：使用国内镜像源安装
```bash
pip install -e ".[paddleocr]" -i https://mirror.baidu.com/pypi/simple
```

### Tesseract（可选）
1. 安装系统依赖：

#### Windows
- 下载并安装 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- 安装时选择 "Chinese (Simplified)"
- 将安装路径添加到环境变量 Path 中

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 中文支持
```

#### MacOS
```bash
brew install tesseract
brew install tesseract-lang  # 语言包
```

2. 安装 Python 包：
```bash
pip install -e ".[tesseract]"
```

### 安装所有 OCR 引擎
如果想要使用所有 OCR 引擎：
```bash
pip install -e ".[all_ocr]"
```

注意：安装 Tesseract 引擎时仍需要安装系统依赖。

## 验证安装

1. 检查数据库连接：
```bash
python -c "from app.database import engine; engine.connect()"
```

2. 检查 OCR 引擎：
```bash
python -c "from app.preprocessing.extract_text import extract_text; print('OCR 配置正确')"
```

3. 启动服务：
```bash
# 后端
cd backend
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

现在可以访问：
- 前端界面：http://localhost:5173
- API文档：http://localhost:8000/docs

## 常见问题

### 数据库连接错误
1. 检查 Docker 容器状态：
```bash
docker-compose ps
```

2. 查看数据库日志：
```bash
docker-compose logs db
```

### OCR 引擎问题
1. PaddleOCR 安装失败
- 尝试使用国内镜像源
- 检查 CUDA 版本兼容性

2. Tesseract 找不到
- 检查环境变量 PATH
- 重新安装 Tesseract

## 下一步
- 查看 [开发指南](development.md)
- 了解 [数据库管理](database.md)
- 浏览 [API 文档](api/v1/README.md) 