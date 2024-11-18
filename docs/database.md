# 数据库管理

## 目录
- [配置说明](#配置说明)
- [数据库结构](#数据库结构)
- [备份和恢复](#备份和恢复)
- [迁移管理](#迁移管理)

## 配置说明

### 数据库连接
在 `.env` 文件中配置数据库连接：
```env
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/ckgcus
```

### Docker 环境
使用 Docker Compose 启动数据库：
```bash
# 启动数据库
docker-compose up -d db

# 查看数据库状态
docker-compose ps

# 查看数据库日志
docker-compose logs db
```

## 数据库结构

### 文档表 (documents)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String | 文档标题 |
| file_path | String | 文件路径 |
| processed_text | Text | 处理后的文本 |
| file_type | String | 文件类型 |
| subject_id | Integer | 关联学科ID |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 学科表 (subjects)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 学科名称 |
| type | String | 学科类型 |
| description | Text | 描述 |

### 学科类型
- FINANCE (金融)
- ECONOMICS (经济)
- STATISTICS (统计)
- DATA_SCIENCE (数据科学)

## 备份和恢复

### 数据库备份
```bash
# 创建完整备份
docker-compose exec db pg_dump -U dev_user ckgcus > backup.sql

# 仅备份数据
docker-compose exec db pg_dump -U dev_user --data-only ckgcus > data_backup.sql
```

### 数据库恢复
```bash
# 恢复完整备份
cat backup.sql | docker-compose exec -T db psql -U dev_user -d ckgcus

# 仅恢复数据
cat data_backup.sql | docker-compose exec -T db psql -U dev_user -d ckgcus
```

### 自动备份脚本
```bash
#!/bin/bash
# scripts/backup-db.sh

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose exec db pg_dump -U dev_user ckgcus > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
```

## 迁移管理

### 初始化数据库
```bash
# 创建迁移
alembic revision --autogenerate -m "initial
```

# 文档上传指南

## 目录
- [上传方式](#上传方式)
- [文件要求](#文件要求)
- [学科分类](#学科分类)
- [批量上传](#批量上传)
- [常见问题](#常见问题)

## 上传方式

### 1. 使用 curl 命令
```bash
# 上传单个文档
curl -X POST "http://localhost:8000/api/v1/documents" \
     -H "accept: application/json" \
     -F "file=@/path/to/your/document.pdf" \
     -F "title=金融市场分析" \
     -F "subject_id=1"
```

### 2. 使用 Python 脚本
```python
import requests

def upload_document(file_path: str, title: str, subject_id: int):
    url = "http://localhost:8000/api/v1/documents"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {
            "title": title,
            "subject_id": subject_id
        }
        response = requests.post(url, files=files, data=data)
        return response.json() if response.status_code == 200 else None
```

### 3. 使用 Postman
1. 新建 POST 请求：`http://localhost:8000/api/v1/documents`
2. Body 选择 `form-data`
3. 添加字段：
   - file: 选择文件
   - title: 文档标题
   - subject_id: 学科ID

## 文件要求

### 支持的格式
- PDF文件 (.pdf)
- 文本文件 (.txt)

### 限制条件
- 最大文件大小：20MB
- 文件名要求：避免特殊字符
- 文件编码：UTF-8

## 学科分类

### 学科ID对照表
| ID | 类型 | 说明 |
|----|------|------|
| 1 | FINANCE | 金融 |
| 2 | ECONOMICS | 经济 |
| 3 | STATISTICS | 统计 |
| 4 | DATA_SCIENCE | 数据科学 |

## 批量上传

### 使用批量上传脚本
```python
from pathlib import Path

def batch_upload(folder_path: str, subject_id: int):
    """批量上传文件夹中的文档"""
    docs_dir = Path(folder_path)
    
    for pdf_file in docs_dir.glob("*.pdf"):
        upload_document(
            file_path=str(pdf_file),
            title=pdf_file.stem,
            subject_id=subject_id
        )

# 使用示例
batch_upload("docs/金融文献", subject_id=1)
```

## 常见问题

### 1. 上传失败
- 检查文件大小是否超限
- 确认文件格式是否支持
- 验证学科ID是否正确
- 检查网络连接

### 2. 文本提取失败
- 确保PDF文件可读
- 检查文件是否加密
- 尝试使用其他OCR引擎

### 3. 最佳实践
- 使用有意义的文档标题
- 正确分类文档学科
- 保持文件名规范
- 定期备份上传记录

## 下一步
- 查看 [数据库管理](database.md)
- 了解 [API文档](api/v1/README.md)
