#!/bin/bash

# 检查是否提供备份文件参数
if [ -z "$1" ]; then
    echo "Usage: ./restore-db.sh <backup_file>"
    echo "Example: ./restore-db.sh ./backups/backup_20240318_123456.sql"
    exit 1
fi

BACKUP_FILE=$1

# 检查备份文件是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file '$BACKUP_FILE' not found!"
    exit 1
fi

echo "Restoring database from $BACKUP_FILE..."

# 删除现有连接
docker-compose exec db psql -U dev_user -d postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'ckgcus'
AND pid <> pg_backend_pid();"

# 删除现有数据库
docker-compose exec db dropdb -U dev_user ckgcus --if-exists

# 创建新数据库
docker-compose exec db createdb -U dev_user ckgcus

# 恢复数据
cat "$BACKUP_FILE" | docker-compose exec -T db psql -U dev_user -d ckgcus

echo "Database restore completed!" 