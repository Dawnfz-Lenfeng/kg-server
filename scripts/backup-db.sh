#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

mkdir -p $BACKUP_DIR
docker-compose exec -T db pg_dump -U dev_user ckgcus > "$BACKUP_DIR/backup_$TIMESTAMP.sql" 