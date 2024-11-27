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

# 进入数据库容器
docker-compose exec db psql -U dev_user -d ckgcus
```

## 数据库结构

### 文档表 (documents)
| 字段 | 类型 | 说明 |
|------|------|------|
|id|int|文档编号；主键|
|title|str|文档标题|
|file_path|str|文件地址|
|file_type|str|文件类型|
|subject_id|int|学科编号；外键|
|origin_text|str|原文本|
|processed_text|str|清洗后文本|
|created_at|datetime|创建时间|
|updated_at|datetime|修改时间|
|subject|Subject|学科；关联属性学科表|
|keywords|list[Keyword]|关键词；关联关键词表|

### 学科表 (subjects)
| 字段 | 类型 | 说明 |
|------|------|------|
|id|int|学科编号；主键|
|name|str|学科名称|
|description|str|描述|
|documents|list[Document]|文档；关联文档表|

### 关键词表 (keywords)
| 字段 | 类型 | 说明 |
|------|------|------|
|id|int|关键词编号；主键|
|name|str|关键词|
|documents|list[Document]|文档；关联文档表|

### 学科类型
- FINANCE (金融)
- ECONOMICS (经济)
- STATISTICS (统计)
- DATA_SCIENCE (数据科学)

## 备份和恢复

### 备份脚本
项目提供了自动备份脚本 `scripts/backup-db.sh`：

```bash
# 创建数据库备份
./scripts/backup-db.sh

# 备份文件将保存在 backups 目录下
# 格式：backup_YYYYMMDD_HHMMSS.sql
# 例如：backup_20240318_143022.sql
```

### 恢复脚本
使用 `scripts/restore-db.sh` 恢复数据库：

```bash
# 恢复指定的备份文件
./scripts/restore-db.sh <backup_file>

# 示例
./scripts/restore-db.sh ./backups/backup_20240318_143022.sql
```

恢复过程会：
1. 终止现有数据库连接
2. 删除现有数据库（如果存在）
3. 创建新数据库
4. 导入备份数据

### 手动备份选项
也可以手动执行备份操作：

```bash
# 创建完整备份
docker-compose exec db pg_dump -U dev_user ckgcus > backup.sql

# 仅备份数据（不包含表结构）
docker-compose exec db pg_dump -U dev_user --data-only ckgcus > data_backup.sql
```

## 迁移管理

### Alembic 配置
项目使用 Alembic 进行数据库迁移管理。配置文件位于：
- `alembic.ini`: 基础配置文件
- `alembic/env.py`: 环境配置，包含数据库连接等设置
- `alembic/versions/`: 存放迁移脚本的目录

### 基本命令
```bash
# 初始化 Alembic（仅首次设置需要）
alembic init alembic

# 创建新的迁移
alembic revision --autogenerate -m "描述变更内容"

# 应用所有迁移
alembic upgrade head

# 回滚一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade <revision_id>

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 版本管理最佳实践

1. 命名规范
```bash
# 格式：日期_时间_简短描述
alembic revision --autogenerate -m "20240301_add_user_table"
```

2. 迁移脚本检查清单
- [ ] 检查自动生成的字段类型是否正确
- [ ] 确认是否需要数据迁移
- [ ] 验证 upgrade 和 downgrade 函数
- [ ] 添加必要的注释说明变更原因

3. 开发流程
```bash
# 1. 创建新分支
git checkout -b feature/db-update

# 2. 修改模型定义

# 3. 生成迁移脚本
alembic revision --autogenerate -m "描述变更内容"

# 4. 检查迁移脚本
# 5. 在测试环境验证
alembic upgrade head

# 6. 提交更改
git add alembic/versions/xxx.py
git commit -m "db: add migration for ..."
```

### 常见问题处理

1. 迁移冲突
```bash
# 重置数据库到特定版本
alembic downgrade <target_revision>

# 删除有问题的迁移脚本
rm alembic/versions/problematic_migration.py

# 重新生成迁移
alembic revision --autogenerate -m "remake_migration"
```

2. 数据备份
```bash
# 在应用迁移前备份
./scripts/backup-db.sh

# 如果需要回滚
alembic downgrade <previous_revision>
./scripts/restore-db.sh <backup_file>
```

3. 生产环境部署
```bash
# 1. 备份数据库
./scripts/backup-db.sh

# 2. 查看待执行的迁移
alembic history --indicate-current

# 3. 应用迁移
alembic upgrade head

# 4. 验证数据库状态
alembic current
```

### 迁移脚本示例

```python
"""add_document_status

Revision ID: a1b2c3d4e5f6
Revises: previous_revision_id
Create Date: 2024-03-01 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# 修订版本信息
revision = 'a1b2c3d4e5f6'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    """升级操作"""
    op.add_column('documents',
        sa.Column('status', sa.String(50), nullable=False, server_default='draft')
    )
    
    # 数据迁移示例
    op.execute(
        "UPDATE documents SET status = 'published' WHERE processed_text IS NOT NULL"
    )

def downgrade():
    """回滚操作"""
    op.drop_column('documents', 'status')
```

### 版本控制注意事项

1. 版本文件管理
- 保留 `versions/.gitkeep` 确保目录存在
- 在 CI/CD 中正确处理迁移文件
- 定期清理旧的迁移文件

2. 团队协作
- 在 PR 中明确说明数据库变更
- 确保迁移脚本经过代码审查
- 保持迁移历史的线性

3. 环境管理
- 开发环境可以频繁重置
- 测试环境模拟生产环境迁移
- 生产环境谨慎操作，做好备份
