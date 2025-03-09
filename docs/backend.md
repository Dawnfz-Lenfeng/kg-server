# 知识图谱构建系统后端文档

## 1. 系统概述

### 1.1 功能简介
本系统后端负责文档处理、文本提取、知识图谱构建等核心功能。

### 1.2 技术栈
- FastAPI + Python 3.10+
- SQLAlchemy 异步 ORM
- OCR: CnOCR/Tesseract
- SQLite/PostgreSQL

### 1.3 系统架构
```mermaid
graph TD
    subgraph API[FastAPI 接口层]
        Upload[文件上传] --> Doc[文档处理]
        Doc --> Graph[图谱构建]
    end
    
    subgraph Service[服务层]
        DocService[文档服务] --> OCR[文本提取]
        OCR --> TextNorm[文本标准化]
        TextNorm --> GraphBuild[图谱构建]
    end
    
    subgraph Storage[存储层]
        DB[(数据库)] --> Files[文件系统]
        Files --> Cache[缓存]
    end
    
    API --> Service
    Service --> Storage
```

## 2. 核心功能模块

### 2.1 文档处理流程
```mermaid
graph LR
    Upload[文件上传] --> Validate[格式验证]
    Validate --> Extract[文本提取]
    Extract --> Normalize[文本标准化]
    Normalize --> Graph[图谱构建]
```

### 2.2 文本提取
- OCR 引擎支持
  - CnOCR (默认)
  - Tesseract (可选)
- 多线程处理
- 异步操作
- 进度跟踪

### 2.3 知识图谱构建
- 关键词提取
- 关系构建
- 权重计算
- 图谱存储

## 3. 数据模型

### 3.1 文档模型
```python
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    file_name: Mapped[str]
    file_type: Mapped[FileType]
    state: Mapped[DocState]
    word_count: Mapped[int | None]
    
    keywords: Mapped[set[Keyword]] = relationship(secondary=document_keywords)
```

### 3.2 关键词模型
```python
class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    documents: Mapped[set[Document]] = relationship(secondary=document_keywords)
```

## 4. API 接口

### 4.1 文档管理
```python
@router.post("/documents", response_model=DocUploadResult)
async def create_doc(
    doc: DocCreate = Depends(get_doc),
    doc_svc: DocService = Depends(get_doc_svc),
) -> DocUploadResult:
    """上传文档"""

@router.put("/documents/{doc_id}/extract", response_model=DocResponse)
async def extract_doc_text(
    doc_id: int,
    extract_config: ExtractConfig,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """提取文档文本"""
```

### 4.2 图谱操作
```python
@router.get("/graph", response_model=GraphData)
async def get_graph(
    graph_svc: GraphService = Depends(get_graph_svc),
):
    """获取知识图谱"""

@router.get("/graph/search", response_model=SearchResult)
async def search_graph(
    keyword: str,
    graph_svc: GraphService = Depends(get_graph_svc),
):
    """搜索图谱"""
```

### 4.2 关键词管理
```python
@router.post("/keywords/upload/{doc_id}")
async def upload_keywords_file(
    doc_id: int,
    file: UploadFile
) -> DocResponse:
    """上传关键词文本文件"""
```

## 5. 服务实现

### 5.1 文档服务
```python
class DocService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_doc(self, doc: DocCreate) -> Document:
        """创建文档"""
        
    async def extract_text(
        self, doc_id: int, config: ExtractConfig
    ) -> Document | None:
        """提取文本"""
```

### 5.2 图谱服务
```python
class GraphService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_graph(self, doc_id: int) -> GraphData:
        """构建知识图谱"""
        
    async def search_keyword(self, keyword: str) -> SearchResult:
        """搜索关键词"""
```

## 6. 异步处理

### 6.1 文件操作
```python
async def save_file(file: UploadFile) -> str:
    """异步保存文件"""
    content = await file.read()
    file_path = _get_unique_path(file.filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    return file_path
```

## 7. 部署配置

### 7.1 环境变量
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
UPLOAD_DIR=/path/to/uploads
OCR_ENGINE=cnocr
DEBUG=False
```

### 7.2 依赖安装
```bash
# 基础依赖
pip install -r requirements.txt

# OCR 依赖
pip install cnocr[ort-cpu]
pip install pytesseract
```

### 7.3 数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "message"

# 执行迁移
alembic upgrade head
```

### 7.4 启动服务
```bash
# 开发环境
uvicorn app.main:app --reload

# 生产环境
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
