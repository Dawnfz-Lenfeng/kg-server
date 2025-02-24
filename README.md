# CKG-CUS: 中文知识图谱构建与更新系统

## 项目描述
CKG-CUS 是一个用于从各种中文语料中构建和更新知识图谱的系统。该系统提供了完整的工具链，从文本提取、预处理到知识图谱的构建与可视化。

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- Docker 和 Docker Compose

### 安装和运行
1. 克隆项目
```bash
git clone https://github.com/Dawnfz-Lenfeng/CKG-CUS.git
cd CKG-CUS
```

2. 启动数据库
```bash
docker-compose up -d db
```

3. 安装和运行后端
```bash
cp .env.example .env
pip install -e .
uvicorn app.main:app --reload
```

<!-- 4. 安装和运行前端
```bash
cd frontend
npm install
npm run dev
``` -->

## 详细文档
- [安装指南](docs/installation.md)
- [开发指南](docs/development.md)
- [数据库管理](docs/database.md)
- [API 文档](docs/api/v1/README.md)

## 作者
- Dawnfz-Lenfeng (2912706234@qq.com)

## 许可证
[MIT License](LICENSE)
