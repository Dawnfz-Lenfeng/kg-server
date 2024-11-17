# CKG-CUS: 中文知识图谱构建与更新系统

## 项目描述

CKG-CUS（Chinese Knowledge Graph Construction and Update System，中文知识图谱构建与更新系统）是一个用于从各种中文语料中构建和更新知识图谱的系统。该系统提供了完整的工具链，从文本提取、预处理到知识图谱的构建与可视化。它支持从 PDF 文件中提取文本，并集成了多种 OCR 技术。

## 项目结构

```
ckgcus/
├── backend/                # 后端服务
│   ├── app/               # 应用代码
│   │   ├── preprocessing/ # 文本预处理模块
│   │   ├── models/       # 数据模型
│   │   ├── api/          # API接口
│   │   └── services/     # 业务逻辑
│   └── tests/            # 测试代码
└── frontend/              # 前端界面
```

## 安装说明

### 后端安装

1. 克隆项目：
```bash
git clone https://github.com/Dawnfz-Lenfeng/CKG-CUS.git
cd CKG-CUS
```

2. 安装后端：
```bash
cd backend
conda create -n ckgcus python=3.10
conda activate ckgcus
pip install -e .         # 安装基本依赖
pip install -e ".[dev]"  # 安装开发依赖
```

3. OCR引擎选择：
- 默认使用 `cnocr`（已包含在基本依赖中）
- 可选安装 `paddleocr`：
  ```bash
  pip install -e ".[paddleocr]"
  ```
- 可选安装 `tesseract`：
  - Windows：[Tesseract安装指南](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS：`brew install tesseract`
  ```bash
  pip install -e ".[tesseract]"
  ```

### 前端安装

```bash
cd frontend
npm install
```

## 开发运行

1. 运行后端：
```bash
cd backend
uvicorn app.main:app --reload
```

2. 运行前端：
```bash
cd frontend
npm run dev
```


## 主要功能

- 文本处理
  - PDF文本提取
  - OCR文本识别
  - 文本清洗
- 知识图谱
  - 图谱构建
  - 图谱更新
  - 图谱可视化
- 用户交互
  - 文件上传
  - 图谱展示
  - 关键词管理

## API文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

```bash
cd backend
pytest
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 作者

- Dawnfz-Lenfeng (2912706234@qq.com)

## 致谢

感谢所有贡献者的付出。
